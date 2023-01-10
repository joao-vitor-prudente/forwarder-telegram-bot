FROM python:3.10

WORKDIR /ForwarderTelegramBot

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

RUN python3 create_db.py prod

CMD [ "python3", "main.py", "prod"]