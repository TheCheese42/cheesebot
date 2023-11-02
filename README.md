# Cheese Bot

The cheesiest bot on the Planet!
Despite not having the ability to bypass earth's boundaries, I'll try my best serving you lots of cheesecake.

Cheese bot is a several purpose Discord Bot written in Python, using the Pycord API Wrapper.
It was created with the intention to deliver way more cheesecake to Discord!

## Running the bot locally

### Step 1: Clone this repo

For Linux:

```bash
git clone "https://github.com/NotYou404/cheesebot"
cd cheesebot
```

For Windows:

```powershell
git clone "https://github.com/NotYou404/cheesebot"
cd cheesebot
```

Or download the ZIP archive at the top right of this page.

### Step 2: Installing dependencies

Install Python (recommended version: 3.11 or higher)

- <https://www.python.org/downloads>

Create and activate a Virtual Environment (optional)

For Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows:

```powershell
python3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

\
Install dependencies:

```shell
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
```

### Step 3: Add your Token and database access

Create a `.env` file in the projects root directory and populate it with the following keys:

```txt
TOKEN = <YOUR_BOT_TOKEN>
MYSQL_HOST = <DATABASE_IP_ADDRESS>
MYSQL_PORT = <DATABASE_PORT>
MYSQL_USERNAME = <MYSQL_USERNAME>
MYSQL_PASSWORD = <MYSQL_PASSWORD>
MYSQL_DATABASE = <DATABASE_NAME>
```

### Step 4: Run the Bot

```shell
python3 cheesebot
```

## Database

CheeseBot makes use of a MySQL database to store it's persistent data. The schema is created automatically, the only thing you have to do is setup a MySQL Server and pass the authentication credentials to the `.env` file.

### Database migration

New database tables and columns may be added, so the existing database needs to be migrated. The Bot does not do this by itself but throw an error if an invalid database schema is detected. Please migrate manually using the table definitions in [`database.py`](https://github.com/NotYou404/cheesebot/blob/main/cheesebot/database/database.py). If you don't know what tool to use, I am using [MySQL Workbench](https://www.mysql.com/products/workbench/). It can also be used to make manual database backups.

## Localization

The bot is NOT making use of localized slash commands. This is because people with different languages than the command executor most likely won't understand the output. This is not very useful in multilingual servers. However there is server-wide command output localization. The language can be set, get and reset using the `/language` command group.

Supported Languages:

- en_US (English)

And that's it. If you want to contribute, please copy the [`en_US.toml`](https://github.com/NotYou404/cheesebot/blob/main/cheesebot/langs/en_US.toml) file from the `cheesebot/langs` directory, set the required metadata and begin translating! When you're done, please submit a pull request or send your copy to `thecheese_knife` on Discord.

## Voice Support

For voice support to work, `ffmpeg` should be installed and on PATH. Also make sure `libopus` is installed on your system.

## Required Permissions

The Bots requires following permissions to work properly:

### Text Permissions

- Send Messages
- Manage Messages
- Embed Links
- Attach Files
- Use External Emojis
- Add Reactions
- Use Slash Commands

### Voice Permissions

- Connect
- Speak
