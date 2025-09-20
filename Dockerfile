FROM python:3.12-alpine3.22

ENV APP_HOME=/opt/flags \
    USER="flags-data-harvester"

RUN mkdir $APP_HOME
WORKDIR $APP_HOME
COPY . .
RUN pip install -r $APP_HOME/requirements.txt
RUN adduser -D -u 1001 -H -s /sbin/nologin $USER
RUN chown -R $USER $APP_HOME
RUN chmod -R 700 $APP_HOME

USER $USER

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]