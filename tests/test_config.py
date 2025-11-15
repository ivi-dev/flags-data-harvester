import json
import os
import unittest
from unittest import mock
from unittest.mock import mock_open, patch
import main


mock_db_section_key = "db"
mock_dbname_key = "name"
mock_dbname = "countries"
mock_dataurl_key = "dataUrl"
mock_data_url = "https://example.com"
mock_config = \
    "{" + \
        f'"{mock_dataurl_key}": "{mock_data_url}",' + \
        f'"{mock_db_section_key}": ' + \
            "{" + \
                f'"{mock_dbname_key}": "{mock_dbname}"' + \
            "}" + \
    "}"


def mock_secret_file_content(filename, *args, **kwargs):
    if filename == f"{main.SECRET_FILE_PATH_PREFIX}db.name":
        return mock.mock_open(read_data=mock_dbname).return_value
    elif filename == f"{main.SECRET_FILE_PATH_PREFIX}dataUrl":
        return mock.mock_open(read_data=mock_data_url).return_value
    else:
        raise ValueError(
            f"\"{filename}\" is not a valid key for a secret file."
        )


class ConfigTest(unittest.TestCase):

    # ================================
    # Config file present scenarios
    # ================================
    @patch("builtins.open", new_callable=mock_open, read_data=mock_config)
    def test_try_load_config_loads_a_valid_json_config(self, mock_open):
        config = main.try_load_config()
        self.assertEqual(json.loads(mock_config), config)

    @patch("main.config", json.loads(mock_config))
    def test_get_config_value_returns_top_level_value_when_config_file_is_present(self):
        val = main.get_config_value(mock_dataurl_key)
        self.assertEqual(mock_data_url, val)

    @patch("main.config", json.loads(mock_config))
    def test_get_config_value_returns_nested_value_when_config_file_is_present(self):
        val = main.get_config_value("db.name")
        self.assertEqual(mock_dbname, val)
    
    @patch("main.config", json.loads(mock_config))
    def test_get_config_value_raises_on_invalid_path_when_config_file_is_present(self):
        with self.assertRaises(KeyError) as cm:
            key = "db.unknown"
            main.get_config_value(key)
        self.assertEqual(str(cm.exception), f"\"Key '{key}' not found in config.\"")


    # ================================
    # Config file missing scenarios
    # ================================
    @patch("main.config", None)
    def test_get_config_value_returns_top_level_value_when_config_file_is_missing(self):
        with mock.patch.dict(os.environ, {f"{main.CONFIG_ENVIRON_PREFIX}DATAURL": mock_data_url}):
            val = main.get_config_value("dataUrl")
            self.assertEqual(mock_data_url, val)

    @patch("main.config", None)
    def test_get_config_value_returns_nested_value_when_config_file_is_missing(self):
        with mock.patch.dict(os.environ, {f"{main.CONFIG_ENVIRON_PREFIX}DB_NAME": mock_dbname}):
            val = main.get_config_value("db.name")
            self.assertEqual(mock_dbname, val)

    @patch("main.config", None)
    @patch("builtins.open", side_effect=mock_secret_file_content)
    def test_get_config_value_returns_top_level_value_when_config_file_and_env_var_are_missing(
        self, 
        mock_open
    ):
        with mock.patch.dict(os.environ, {}):
            val = main.get_config_value("dataUrl")
            self.assertEqual(mock_data_url, val)

    @patch("main.config", None)
    @patch("builtins.open", side_effect=mock_secret_file_content)
    def test_get_config_value_returns_nested_value_when_config_file_and_env_var_are_missing(
        self,
        mock_open
    ):
        with mock.patch.dict(os.environ, {}):
            val = main.get_config_value("db.name")
            self.assertEqual(mock_dbname, val)