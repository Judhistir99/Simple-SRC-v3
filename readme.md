# Simple SRC v3

A simplest Telegram Save Restricted bot repo (just 100 lines) that helps batch process messages from private and public channels.

## Features
- Extracts messages from channels and forwards them.
- Supports downloading media for private channels.
- Allows batch processing of multiple messages.
- Provides a cancellation option.

## Requirements
- Python 3.8+
- `pyrogram` and `tgcrypto` libraries

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/batch-bot.git
   cd batch-bot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `API_ID` – Your Telegram API ID
   - `API_HASH` – Your Telegram API Hash
   - `BOT_TOKEN` – Your Bot Token
   - `SESSION` – Your Pyrogram session string Can be generated from - [Pyrogram Session Generator](https://telegram.tools/session-string-generator#pyrogram,user)

## Running the Bot
```sh
python main.py
```
## Deployments (other than VPS)
- [Deploy on Heroku](https://heroku.com/deploy)
- you can connect and deploy on any PaaS (platform as service) provider like koyeb, render, northflank, railway etc via dockerfile

## Commands
- `start` - check if bot alive
- `/batch` – Start batch processing messages.
- `/cancel` – Cancel an ongoing operation.

## License
This project is open-source. Modify and use as needed.
