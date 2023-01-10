# Forwarder Telegram Bot

## About

This app is a telegram bot that you can chat with to create input/output connections between telegram channels where every time a message is sent to the input channel, the bot forwards it to the output channel.

Aside of that, you can also create filters to treat the messages before forwarding it.

## Tecnologies

- [Python](https://www.python.org/)
- [Sqlalchemy](https://www.sqlalchemy.org/)
- [Telethon](https://github.com/LonamiWebs/Telethon)

## Configuration

### Clone Repository:

```bash
git clone https://github.com/joao-vitor-prudente/forwarder-telegram-bot
```

### Dependencies:
- [Python 3.10](https://www.python.org/downloads/release/python-3100/)

Other python interpreter versions may work but it's not garanteed.

### Set Up Environment:

In the command prompt, run:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
touch prod.env
touch dev.env
```

for linux or mac, you may need to replace python for python3 and/or pip for pip3.

### Set Up Telegram Bot:

On your telegram account, find a chat named BotFather and follow the instructions to create a bot.

### Set Up Telegram API:

You can get your telegram api id in https://my.telegram.org/auth, fill in your phone number and go to API Development Tools.

### Get Your Encrypting Salt:

In your command prompt run:
``` bash
python get_salt.py
```


### Set Up Environment Variables:

In the prod.env and dev.env files, write the following:

```
API_ID=<telegram api id>
API_HASH=<telegram api hash>
PHONE=<your phone number>
BOT_URL=<the link to the telegram bot>
SALT=<salt to encode the password>
ADMIN_LOGIN=<your admin login>
ADMIN_PASSWORD=<your password login>
```

Replace the <...> for your information. There is a prod.env and a dev.env to separate the development environment and the production environment, if you do not want to make this separation, just use one or the other.

### Create SQLite Database

To create the database with the production environment, run in the command prompt:

```bash
python create_db.py prod
```

For development environmnet:

```bash
python create_db.py dev
```

### Run ForwarderTelegramBot

To run the bot with the production environment, run in the command prompt:

```bash
python main.py prod
```

For development environmnet:

```bash
python main.py dev
```

### Run in [Docker](https://www.docker.com/)

Build image:

```bash
docker build --tag forwarder-telegram-bot  ./
```

Run container:

```bash
docker run forwarder-telegram-bot
```

When the program starts the first time, telegram will send you a confirmation code, which you will be asked by the program, after you do this, the program will generate a session.session file in the root directory of the app, which will be used to log in to telegram.

So if you do not have already a session.session file, you will have to run it in interactive mode (add a -ti in the command after run).

I recommend you to first run the program without docker, generate the session.session file and then run it in docker.

## Usage

### Utility Commands:

```
/help
```

Shows a list with all commands.

```
/auth --login=<admin_username> --password=<admin_password>
```

You will need to authorize this chat to run every command other than /help. Login and password are the .env's.

```
/sync
```

Syncronize the telegram api with the database if there was any error and they got unsyncronized

### Managing Channels Commands:

```
/add_channel --name=<channel_name> --url=<channel_url>
```

Add a channel to the database.

```
/remove_channel --filter=<channel_name_or_url>
```

Remove a channel from the database and all its connections. The filter argument can be any channel's name or url.

```
/view_channel --filter=<channel_name_or_url>
```

View all information of any channel in database.

```
/view_all_channel
```

View all channels registered in the database.

```
/view_connections
```

View all the connections between channels and their information.

```
/connect_channels --input=<input_channel_name_or_url> --output=<output_channel_name_or_url>
```

Connects two channels. Either the input and attribute arguments can be any channel's name or url

```
/disconnect_channels --input=<input_channel_name_or_url> --output=<output_channel_name_or_url>
```

Disconnects two channels.

### Managing Filters Commands:

```
/add_to_blacklist --condition=<condition>
```

Add a string to the blacklist, messages containing string in the blacklist won't be forwarded. The condition argument is the string

```
/add_replacement --condition=<condition> --replacement=<replacement>
```

Add string to be replaced and a replacement. The condition argument is the string to be replaced and the replacement is the replacement string. All occourences of a string to be replaced will be replaced with it's replacement.

```
/add_link_remover --condition=<condition>
```

Add a link remover. The condition argument is a link domain. All phrases or lines containing urls in the message of the specified domain will be removed from the message.

```
/remove_from_blacklist --condition=<condition>
```

Remove a string from the blacklist.

```
/remove_replacement --condition=<condition>
```

Remove a string to be replaced and its replacement from the replacements.

```
/remove_link_remover --condition=<condition>
```

Remove a domain from the link removers
```
/view_blacklist
```

View all strings on the blacklist.

```
/view_replacements
```

View all strings to be replaced and their replacements.

```
/view_link_removers
```

View all link removers