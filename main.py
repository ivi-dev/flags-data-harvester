from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import re
import traceback
import requests
from bs4 import BeautifulSoup
import pymongo


config = {}

corrections = {}

db_client = None

db = None

countries = None


@dataclass
class Country:
    name: str
    iso: str
    capital: str
    flag: bytes


def load_config():
    try:
        with open("config.json") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        raise Exception("Config file not found.")
    except json.JSONDecodeError:
        raise Exception("Error decoding JSON from config file.")


def init_data_dir():
    if not os.path.exists(config["dataPath"]):
        os.makedirs(config["dataPath"])


def update_country_record(dest, country):
    def update_db():
        global db, db_client, countries
        if db_client is None:
            uri = f'mongodb://' \
                  f'{config["db"]["user"]}:' \
                  f'{config["db"]["pass"]}@' \
                  f'{config["db"]["host"]}:' \
                  f'{config["db"]["port"]}/' \
                  f'{config["db"]["name"]}?' \
                  f'authSource={config["db"]["authSource"]}&' \
                  f'connectTimeoutMS={config["db"]["connectTimeout"]}&' \
                  'tls=true&' \
                  'tlsCAFile=/etc/ssl/certs/flags/root.crt'
            db_client = pymongo.MongoClient(uri)
            db = db_client[config["db"]["name"]]
            countries = db.countries
        update_country_db(country)

    destinations = ["fs", "db", "fs-db"]
    if dest not in destinations:
        raise ValueError(
            f"Unknown destination option '{dest}'. "
            f"Supported options: {','.join(destinations)}"
        )
    if dest == "fs":
        update_country_dir(country)
    elif dest == "db":
        update_db()
    elif dest == "fs-db":
        update_country_dir(country)
        update_db()


def update_country_dir(country):
    country_dir = os.path.join(config["dataPath"], country.name)
    if not os.path.exists(country_dir):
        os.makedirs(country_dir)
    init_country_meta(country_dir, country)
    save_country_flag(country_dir, country.flag)


def update_country_db(country):
    meta = get_country_meta(country)
    countries.update_one(
        {
            "name": country.name
        }, 
        {
            "$set": {
                "meta": meta, 
                "flag": country.flag
            }
        }, 
        upsert=True
    )


def get_country_meta(country):
    data = {
        "name": {
            "en": [country.name]
        },
        "capital": {
            "en": [country.capital]
        },
        "iso-3166": country.iso
    }
    if country_name in corrections:
        deep_update(data, corrections[country.name])
    return data


def init_country_meta(country_dir, country):
    with open(os.path.join(country_dir, "Meta.json"), "w") as meta:
        data = get_country_meta(country)
        meta.write(json.dumps(data, indent=4, ensure_ascii=False))


def save_country_flag(country_dir, country_flag):
    with open(os.path.join(country_dir, "Flag.svg"), "wb") as flag:
        flag.write(country_flag)


def country_name_spans_multiple_rows(col):
    rowspan = col["rowspan"] if "rowspan" in col.attrs else None
    return col.name == "th" and rowspan is not None and rowspan != "1"


def iso_3166_column(tag):
    return "title" in tag.attrs and config["iso3166ColId"] in tag["title"]


def get_data_table(session=None):
    res = request(url=config["dataUrl"], method='GET', session=session)
    soup = BeautifulSoup(res.text, features="html.parser")
    rows = soup.find("table", class_="wikitable").find("tbody").find_all("tr")
    return rows


def get_country_name(tag):
    country_name = tag.find("th")
    if country_name is None:
        return None
    else:
        return country_name.find("a").string


def get_user_agent():
    bot_name = {
        'human': f'{config["user-agent"]["name"]["human"]}/{config["user-agent"]["version"]}',
        'machine': f'{config["user-agent"]["name"]["machine"]}/{config["user-agent"]["version"]}'
    }
    return f'{bot_name["human"]} ' + \
           f'({config["user-agent"]["email"]}) ' + \
           f'{bot_name["machine"]}'


def request(url, method='GET', session=None):
    headers = {
        'User-Agent': get_user_agent()
    }
    obj = session or requests
    meth = getattr(obj, method.lower())
    return meth(url, headers=headers)


def get_country_soup(tag, session=None):
    link = f'https://en.wikipedia.org{tag.find("th").find("a")["href"]}'
    res = request(url=link, method='GET', session=session)
    return BeautifulSoup(res.text, features="html.parser")
    

def get_country_iso_code(soup):
    table = soup.find("table", class_="infobox")
    data_cols = table.find_all("td", class_="infobox-data")
    for data_col in data_cols:
        iso_col = data_col.find(iso_3166_column)
        if iso_col:
            return iso_col.string


def get_country_capital(soup):
    table = soup.find("table", class_="infobox")
    data_rows = table.find_all("tr")
    for data_row in data_rows:
        header = data_row.find("th")
        if header and "Capital" in header.text:
            data_col = data_row.find("td")
            if data_col:
                return data_col.find("a").text.strip()
        

def get_country_flag(tag, session=None):
    flag_url = tag.find("td").find("figure").find("a").find("img")["src"]\
                  .replace("//", "https://")\
                  .replace("thumb/", "")
    match = re.search(r"https://.+?\.svg", flag_url)
    flag_url = flag_url[match.start():match.end()]
    res = request(url=flag_url, method='GET', session=session)
    return res.content


def load_corrections():
    with open("corrections.json") as corr:
        return json.loads(corr.read())
    

def deep_update(d1, d2):
    for key in d1:
        if key in d2:
            correction = d2[key]
            if isinstance(correction, dict):
                deep_update(d1[key], correction)
            elif isinstance(correction, list):
                d1[key].extend(correction)
            else:
                d1[key] = correction


def print_progress(tag, index):
    country_name_ = get_country_name(tag)
    print(f'{index}. Harvested data for "{country_name_}".')


def formatted_now(fmt="%Y/%m/%d %H:%M:%S %Z"):
    return datetime.now(timezone.utc).strftime(fmt)


def log_harvest(status, storage, start_time, n_harvested=None, err=None):
    if status.lower() not in ['success', 'failure']:
        raise ValueError("Status must be either 'success' or 'failure'.")
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open("logs/Harvest-Result.txt", "wt") as log:
        log.write(f"Harvest status: {status.upper()}\n")
        log.write(f"Date/time of completing harvest: {formatted_now()}\n")
        if status == "success":
            log_success(log, storage, start_time, n_harvested)
        elif status == "failure":
            log_error(log, err)


def log_success(log, storage, start_time, n_harvested):
    duration = datetime.now(timezone.utc) - start_time
    log.write(f"Harvest duration: {str(duration)}\n")
    log.write(f"Number of harvested countries: {n_harvested}\n")
    log.write(f"Harvesting source: \"{config["dataUrl"]}\"\n")
    dataPath = os.path.abspath(config["dataPath"])
    if storage == "fs":
        harvestDest = f"Local file system directory \"{dataPath}\""
    elif storage == "db":
        harvestDest = f"MongDB " \
                      f"(host) \"{config['db']['host']}\", " \
                      f"(port) {config['db']['port']}, " \
                      f"(name) \"{config['db']['name']}\", " \
                      f"(collection) \"{config['db']['collection']}\"\n"
    elif storage == "fs-db":
        harvestDest = f"Both local file system directory \"{dataPath}\" and " \
                      "MongDB " \
                      f"(host) \"{config['db']['host']}\", " \
                      f"(port) {config['db']['port']}, " \
                      f"(name) \"{config['db']['name']}\", " \
                      f"(collection) \"{config['db']['collection']}\"\n"
    log.write(f"Harvested data is at: {harvestDest}")


def log_error(log, err):
    log.write(f"Error details:\n{"\n".join(traceback.format_exception(err))}\n")


start_time = datetime.now(timezone.utc)
storage = "db"
try:
    config = load_config()
    with requests.Session() as session:
        table = get_data_table(session)
        n_harvested = 0
        init_data_dir()
        corrections = load_corrections()
        start, end = 1, len(table) # Skip the first row, which is the table's header
        for i in range(start, end):
            is_primary_flag_row = table[i].find("th") is not None
            if is_primary_flag_row:
                n_harvested += 1
                country_name = get_country_name(table[i])
                soup = get_country_soup(table[i], session)
                country_iso = get_country_iso_code(soup)
                country_capital = get_country_capital(soup)
                country_flag = get_country_flag(table[i], session)
                country = Country(
                    name=country_name,
                    iso=country_iso,
                    capital=country_capital,
                    flag=country_flag
                )
                update_country_record(storage, country)
                print_progress(table[i], n_harvested)
        log_harvest('success', storage, start_time, n_harvested)
except Exception as e:
    log_harvest('failure', storage, start_time, err=e)
    raise