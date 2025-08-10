FROM python:3.12-alpine3.22

ENV APP_HOME=/opt/flags-data-harvester

RUN mkdir $APP_HOME
COPY . $APP_HOME
RUN pip install -r $APP_HOME/requirements.txt

CMD ["python", "/opt/flags-data-harvester/main.py"]