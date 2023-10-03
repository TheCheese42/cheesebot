# Cheese Bot

The most cheesiest bot on the Planet!
Despite not having the ability to bypass earth's boundaries, I'll try my best serving you a lot of cheesecake.

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

```pwsh
git clone "https://github.com/NotYou404/cheesebot"
cd cheesebot
```

Or download the ZIP archive at the top right of this page.

### Step 2: Installing dependencies

Install Python (recommended version: 3.11.x)

- <https://www.python.org/downloads/>

Create and activate a Virtual Environment (optional)

For Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows:

```pwsh
python3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```shell
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt
```

### Step 3: Add you Token

Create a `.token` file in the projects root directory and paste your bot token there.

### Step 4: Run the Bot

```shell
python3 cheesebot
```

## Localization

The bot is NOT making use of localized slash commands. This is because people with different languages than the command executor most likely won't understand the output. This is not very useful in multilingual servers. Ability for guild-wide localization may be added in the future.

## Voice Support

For voice support to work you have to create a `lib/` folder in the projects root directory. This folder should contain an ffmpeg binary, called `ffmpeg` (or `ffmpeg.exe` on Windows). Also make sure libopus is installed on your system.

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
