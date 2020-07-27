FROM python:3.8-alpine

# Working directory for the application
WORKDIR /usr/src/app
COPY bot/requirements.txt /usr/src/app/requirements.txt

RUN apk --no-cache update && apk --no-cache upgrade && apk --no-cache add --virtual buildpack gcc musl-dev build-base
RUN apk --no-cache update && apk add git
RUN pip install -U -r requirements.txt

COPY bot /usr/src/app
COPY bot/config.py.dist /usr/src/app/config.py

# Set Entrypoint with hard-coded options
ENTRYPOINT ["python3"]
CMD ["./start_bot.py"]

