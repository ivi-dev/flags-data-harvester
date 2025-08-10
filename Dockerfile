FROM python:3.12-alpine3.22

ENV APP_HOME=/opt/flags

RUN mkdir $APP_HOME
WORKDIR $APP_HOME
COPY . .
RUN pip install -r $APP_HOME/requirements.txt

CMD ["python", "main.py"]