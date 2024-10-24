FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh 

COPY . . 

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]