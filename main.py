import os, re
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import time
from config import API_ID, API_HASH, BOT_TOKEN, SESSION
import sys

bot_client, user_client = Client("bot_client", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN), Client("user_client", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
user_data, task_data = {}, {}
try:
    user_client.start()
    print("userbot started")
except Exception:
    print("check your session")
    pass

progress_cache = {}

EMOJI_MAP = {
    "running": "🏃‍♂️",
    "download": "⬇️",
    "upload": "⬆️",
    "complete": "✅",
    "cancel": "❌",
    "error": "⚠️",
    "start": "🚀",
    "batch": "📦",
    "process": "🔄",
    "done": "✔️"
}

def add_emojis(text):
    words = text.split()
    return ' '.join([f"{word} {EMOJI_MAP.get(word.lower(), '')}".strip() for word in words])

def extract_link_details(link):
    private_match = re.match(r"https://t\.me/c/(\d+)/(\d+)", link)
    public_match = re.match(r"https://t\.me/([^/]+)/(\d+)", link)
    
    if private_match:
        return f"-100{private_match.group(1)}", int(private_match.group(2)), "private"
    elif public_match:
        return public_match.group(1), int(public_match.group(2)), "public"
    else:
        return None, None, None
        
async def fetch_message(client, user, chat_id, message_id, link_type):
    try:
        print(f"Fetching message from {chat_id}, Message ID: {message_id}, Type: {link_type}")
        return await (client if link_type == "public" else user).get_messages(chat_id, message_id)
    except Exception as e:
        print(f"Error fetching message: {e}")
        return None

async def update_progress_bar(batch_progress, current, total, client, chat_id, message_id, start_time):
    global progress_cache
    progress = (current / total) * 100
    step = int(progress // 10) * 10

    if message_id not in progress_cache or progress_cache[message_id] != step or progress >= 100:
        progress_cache[message_id] = step
        completed = int(progress // 10)
        ongoing = 1 if progress % 10 != 0 and progress < 100 else 0
        incomplete = 10 - completed - ongoing

        bar = "🟩" * completed + "🟨" * ongoing + "🟥" * incomplete
        speed = (current / (time.time() - start_time)) / (1024 * 1024) if time.time() > start_time else 0
        eta = time.strftime("%M:%S", time.gmtime((total - current) / (speed * 1024 * 1024))) if speed > 0 else "00:00"
        
        batch_total, batch_completed = batch_progress
        batch_progress_percentage = (batch_completed / batch_total) * 100
        batch_bar = "🟩" * (int(batch_progress_percentage / 10)) + "🟥" * (10 - int(batch_progress_percentage / 10))

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel ❌", callback_data=f"cancel_{message_id}"),
              InlineKeyboardButton("Restart 🔄", callback_data=f"restart_{message_id}"),
              InlineKeyboardButton("Reboot 🔄", callback_data=f"reboot_{message_id}")]]
        )

        await client.edit_message_text(chat_id, message_id, f"__**Pyro Handler...**__\n\n{bar}\n\n📊 **__Completed__**: {progress:.2f}%\n🚀 **__Speed**__: {speed:.2f} MB/s\n⏳ **__ETA**__: {eta}\n\n🔄 **Batch Progress**: {batch_bar} {batch_completed}/{batch_total}\n\n**All Set ☑️**", reply_markup=keyboard)
        if progress >= 100:
            progress_cache.pop(message_id, None)

async def handle_media(client, user, message, destination_chat_id, link_type, user_id, batch_progress):
    try:
        if message.media:
            start_time = time.time()
            if link_type == "private":
                progress_message = await client.send_message(destination_chat_id, add_emojis("Downloading..."))
                task_data[user_id] = {"cancel": False, "progress": progress_message.id}
                file_path = await user.download_media(message, progress=update_progress_bar, progress_args=(batch_progress, client, destination_chat_id, progress_message.id, start_time))
                
                if task_data.get(user_id, {}).get("cancel"):
                    await client.edit_message_text(destination_chat_id, progress_message.id, add_emojis("Canceled."))
                    if os.path.exists(file_path): os.remove(file_path)
                    del task_data[user_id]
                    return add_emojis("Canceled.")
                
                if not file_path:
                    await client.edit_message_text(destination_chat_id, progress_message.id, add_emojis("Failed."))
                    del task_data[user_id]
                    return add_emojis("Failed.")
                
                await client.edit_message_text(destination_chat_id, progress_message.id, add_emojis("Uploading..."))
                thumb = "v3.jpg"
                if message.video:
                    width, height, duration = message.video.width, message.video.height, message.video.duration
                    await client.send_video(destination_chat_id, video=file_path, caption=message.caption.markdown, thumb=thumb, width=width, height=height, duration=duration, progress=update_progress_bar, progress_args=(batch_progress, client, destination_chat_id, progress_message.id, start_time))
                elif message.video_note: await client.send_video_note(destination_chat_id, video_note=file_path, progress=update_progress_bar, progress_args=(batch_progress, client, destination_chat_id, progress_message.id, start_time))
                elif message.voice: await client.send_voice(destination_chat_id, file_path, progress=update_progress_bar, progress_args=(batch_progress, client, destination_chat_id, progress_message.id, start_time))
                elif message.sticker: await client.send_sticker(destination_chat_id, message.sticker.file_id)
                elif message.audio: await client.send_audio(destination_chat_id, audio=file_path, caption=message.caption.markdown, thumb=thumb, progress=update_progress_bar, progress_args=(batch_progress, client, destination_chat_id, progress_message.id, start_time))
                elif message.photo: await client.send_photo(destination_chat_id, photo=file_path, caption=message.caption.markdown, progress=update_progress_bar, progress_args=(batch_progress, client, destination_chat_id, progress_message.id, start_time))
                elif message.document: await client.send_document(destination_chat_id, document=file_path, caption=message.caption.markdown, progress=update_progress_bar, progress_args=(batch_progress, client, destination_chat_id, progress_message.id, start_time))
                os.remove(file_path)
                await client.delete_messages(destination_chat_id, progress_message.id)
                del task_data[user_id]
                return add_emojis("Done.")
            else:
                await message.copy(chat_id=destination_chat_id)
                return add_emojis("Copied.")
        elif message.text:
            await (client.send_message(destination_chat_id, text=add_emojis(message.text.markdown)) if link_type == "private" else message.copy(chat_id=destination_chat_id))
            return add_emojis("Sent.")
    except Exception as e:
        return f"Error: {e}"

@bot_client.on_message(filters.command("start"))
async def start_command(client, message: Message):
    await message.reply_text(add_emojis("Welcome to bot. Use /batch to start magic."))

@bot_client.on_message(filters.command("batch"))
async def batch_command(client, message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {"step": "start"}
    await message.reply_text(add_emojis("Send start link."))

@bot_client.on_message(filters.command("cancel"))
async def cancel_command(client, message: Message):
    user_id = message.from_user.id
    if user_id in task_data:
        task_data[user_id]["cancel"] = True
        await message.reply_text(add_emojis("Cancelling..."))
    else:
        await message.reply_text(add_emojis("No active task."))

@bot_client.on_message(filters.command("restart"))
async def restart_command(client, message: Message):
    user_id = message.from_user.id
    if user_id in task_data:
        task_data[user_id]["cancel"] = True
        await message.reply_text(add_emojis("Restarting..."))
        user_data[user_id]["step"] = "process"
        await process_batch(client, message)
    else:
        await message.reply_text(add_emojis("No active task."))

@bot_client.on_message(filters.command("reboot"))
async def reboot_command(client, message: Message):
    await message.reply_text(add_emojis("Rebooting..."))
    os.execv(sys.executable, ['python'] + sys.argv)

@bot_client.on_callback_query(filters.regex(r"cancel_(\d+)"))
async def cancel_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in task_data:
        task_data[user_id]["cancel"] = True
        await callback_query.answer("Cancelling...")
    else:
        await callback_query.answer("No active task.")

@bot_client.on_callback_query(filters.regex(r"restart_(\d+)"))
async def restart_callback(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in task_data:
        task_data[user_id]["cancel"] = True
        await callback_query.answer("Restarting...")
        user_data[user_id]["step"] = "process"
        await process_batch(client, callback_query.message)
    else:
        await callback_query.answer("No active task.")

@bot_client.on_callback_query(filters.regex(r"reboot_(\d+)"))
async def reboot_callback(client, callback_query):
    await callback_query.answer("Rebooting...")
    os.execv(sys.executable, ['python'] + sys.argv)

async def process_batch(client, message):
    user_id = message.from_user.id
    chat_id, start_id, num_messages, link_type = user_data[user_id]["cid"], user_data[user_id]["sid"], user_data[user_id]["num"], user_data[user_id]["lt"]
    successful_tasks = 0
    progress_message = await message.reply_text(add_emojis("Trying hard 🐥..."))
    
    for i in range(num_messages):
        message_id = start_id + i
        msg = await fetch_message(client, user_client, chat_id, message_id, link_type)
        if msg:
            result = await handle_media(client, user_client, msg, user_data[user_id]["did"], link_type, user_id, (num_messages, i+1))
            await progress_message.edit(f"{i+1}/{num_messages}: {result}")
            if "Done" in result: successful_tasks += 1
        else:
            await message.reply_text(f"{message_id} not found.")
    
    await message.reply_text(f"Batch Completed ✅")
    del user_data[user_id]

@bot_client.on_message(filters.text & ~filters.command(["start", "batch", "cancel", "restart", "reboot"]))
async def handle_text_message(client, message: Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        return
    step = user_data[user_id].get("step")
    if step == "start":
        link = message.text
        chat_id, start_id, link_type = extract_link_details(link)
        if not chat_id or not start_id:
            await message.reply_text(add_emojis("Invalid link. Please check the format."))
            del user_data[user_id]
            return
        user_data[user_id].update({"step": "count", "cid": chat_id, "sid": start_id, "lt": link_type})
        await message.reply_text(add_emojis("How many messages?"))
    
    elif step == "count":
        if not message.text.isdigit():
            await message.reply_text(add_emojis("Enter a valid number."))
            return
        user_data[user_id].update({"step": "dest", "num": int(message.text)})
        await message.reply_text(add_emojis("Send destination chat ID."))
    
    elif step == "dest":
        destination_chat_id = message.text
        user_data[user_id].update({"step": "process", "did": destination_chat_id})
        
        chat_id, start_id, num_messages, link_type = user_data[user_id]["cid"], user_data[user_id]["sid"], user_data[user_id]["num"], user_data[user_id]["lt"]
        successful_tasks = 0
        progress_message = await message.reply_text(add_emojis("Trying hard 🐥..."))
        
        for i in range(num_messages):
            message_id = start_id + i
            msg = await fetch_message(client, user_client, chat_id, message_id, link_type)
            if msg:
                result = await handle_media(client, user_client, msg, destination_chat_id, link_type, user_id, (num_messages, i+1))
                await progress_message.edit(f"{i+1}/{num_messages}: {result}")
                if result and "Done" in result:
                    successful_tasks += 1
            else:
                await message.reply_text(f"{message_id} not found.")
        
        await message.reply_text(f"Batch Completed ✅")
        del user_data[user_id]

print("Bot started successfully!!")
bot_client.run()
