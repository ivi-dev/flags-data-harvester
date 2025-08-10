FROM python:3.12-alpine3.22

ENV APP_HOME=/opt/flags-data-harvester
RUN mkdir $APP_HOME
WORKDIR $APP_HOME
COPY . $APP_HOME
RUN pip install -r requirements.txt

CMD ["python", "/opt/flags-data-harvester/main.py"]