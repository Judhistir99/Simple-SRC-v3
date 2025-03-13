# JSimpleSRC-vE3

Simplest Save Restricted Content Bot for self use.

This branch is further edited version where as code variables are in their full form instead their short replaced with variables. For better understanding while modification. 

Please use master branch for original code with minimal changes for original code check 

'''
https://github.com/devgaganin/Simple-SRC-v3
'''

## Description

This bot helps you save restricted content from Telegram channels and chats. It works with both private and public links and can handle various media types including videos, photos, documents, and more.

## Features extra + original

- Save media from both private and public Telegram channels.
- Supports video, audio, photo, document, sticker, and more.
- Shows a progress bar with detailed upload/download status.
- Reboot command to restart the bot from the server side.
- Cancel and restart options for ongoing tasks.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Judhistir888/Simple-SRC-v3.git
    cd Simple-SRC-v3
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Configure your bot by updating the `config.py` file with your Telegram API credentials:
    ```python
    API_ID = 'your_api_id'
    API_HASH = 'your_api_hash'
    BOT_TOKEN = 'your_bot_token'
    SESSION = 'your_session_string'
    ```
    - [Pyrogram Session Generator](https://telegram.tools/session-string-generator#pyrogram,user)
      

4. Run the bot:
    ```sh
    python main.py
    ```

## Usage

### Commands extra + original 

- `/start`: Welcome message and initial instructions.
- `/batch`: Start the batch process by sending the start link.
- `/cancel`: Cancel the current task.
- `/restart`: Restart the current batch process.
- `/reboot`: Reboot the bot.

### Progress Details

The progress bar now uses green squares (🟩) for completed parts, yellow squares (🟨) for ongoing parts, and red squares (🟥) for incomplete parts. The progress details include the completion percentage, speed, estimated time remaining (ETA), and batch progress. Here is an example of the progress details:

```
__**Pyro Handler...**__

🟩🟩🟩🟩🟩🟩🟩🟩🟩🟥

📊 **__Completed__**: 90.00%
🚀 **__Speed__**: 1.23 MB/s
⏳ **__ETA__**: 00:01

🔄 **Batch Progress**: 🟩🟩🟩🟩🟩🟩🟩🟩🟩🟥 9/10

**All Set ☑️**

[Cancel ❌] [Restart 🔄] [Reboot 🔄]
```

## Contributing

Feel free to contribute to this project by submitting a pull request or opening an issue, And Set ☑️

## License

This project is licensed under the MIT License.
