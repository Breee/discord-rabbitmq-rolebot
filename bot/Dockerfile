FROM python:3.7-alpine

# Working directory for the application
WORKDIR /usr/src/app
COPY . /usr/src/app

RUN apk --no-cache update && apk --no-cache upgrade && apk --no-cache add --virtual buildpack gcc musl-dev build-base
RUN apk --no-cache update && apk add git
RUN pip install -U -r requirements.txt

# Set Entrypoint with hard-coded options
ENTRYPOINT ["python3"]
CMD ["./start_bot.py"]

