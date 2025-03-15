import os as O, re as R
from pyrogram import Client as C, filters as F
from pyrogram.types import Message as M, InlineKeyboardMarkup, InlineKeyboardButton
import time
from config import API_ID as A, API_HASH as H, BOT_TOKEN as T, SESSION as S
import sys
import psutil
import json
from functions import is_safe_path, read_remove_text, read_add_text, set_thumbnail, remove_thumbnail, set_remove_text, clear_remove_text, set_add_text, clear_add_text
from progress_bar import K

REBOOT_FLAG = "/app/reboot.flag"
STATE_FILE = "/app/state.json"

API_ID = O.getenv("API_ID")
API_HASH = O.getenv("API_HASH")
BOT_TOKEN = O.getenv("BOT_TOKEN")
SESSION = O.getenv("SESSION")

X, Y = C("X", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN), C("Y", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
Z, W = {}, {}
try:
    Y.start()
    print("userbot started")
except Exception:
    print("check your session")
    pass

# Check if reboot flag exists and send reboot success message
if is_safe_path("/app", REBOOT_FLAG) and O.path.exists(REBOOT_FLAG):
    with open(REBOOT_FLAG, "r") as f:
        chat_id = f.read().strip()
    O.remove(REBOOT_FLAG)
    
    # Load state from file and resume tasks
    if is_safe_path("/app", STATE_FILE) and O.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            Z = json.load(f)
        O.remove(STATE_FILE)
    
    async def send_reboot_success():
        await X.send_message(chat_id, "Rebooted successfully and resumed tasks.")
        for U in Z:
            await process_batch(X, Z[U]["message"])
    X.loop.run_until_complete(send_reboot_success())

def E(L):
    Q = R.match(r"https://t\.me/c/(\d+)/(\d+)", L)
    P = R.match(r"https://t\.me/([^/]+)/(\d+)", L)
    
    if Q:
        return f"-100{Q.group(1)}", int(Q.group(2)), "private"
    elif P:
        return P.group(1), int(P.group(2)), "public"
    else:
        return None, None, None
        
async def J(C, U, I, D, link_type):
    try:
        print(f"Fetching message from {I}, Message ID: {D}, Type: {link_type}")
        return await (C if link_type == "public" else U).get_messages(I, D)
    except Exception as e:
        print(f"Error fetching message: {e}")
        return None

async def V(C, U, m, d, link_type, u, batch_progress, text_to_remove=None, text_to_add=None, thumbnail=None, send_as_document=False):
    try:
        if m.media:
            st = time.time()
            if link_type == "private":
                P = await C.send_message(d, "Downloading...")
                W[u] = {"cancel": False, "progress": P.id}
                F = await U.download_media(m, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                
                if W.get(u, {}).get("cancel"):
                    await C.edit_message_text(d, P.id, "Canceled.")
                    if O.path.exists(F) and is_safe_path("/app", F): O.remove(F)
                    del W[u]
                    return "Canceled."
                
                if not F:
                    await C.edit_message_text(d, P.id, "Failed.")
                    del W[u]
                    return "Failed."
                
                await C.edit_message_text(d, P.id, "Uploading...")
                
                # Remove custom text from filename and caption
                caption = m.caption.markdown if m.caption else ""
                filename = F if not text_to_remove else F.replace(text_to_remove, "")
                caption = caption.replace(text_to_remove, "") if text_to_remove else caption
                
                # Add custom text to filename and caption
                if text_to_add:
                    filename_parts = O.path.splitext(filename)
                    filename = f"{filename_parts[0]}{text_to_add}{filename_parts[1]}"
                    caption = f"{caption}{text_to_add}"
                
                # Use filename as caption if no caption is provided
                if not caption:
                    caption = O.path.basename(filename)

                if send_as_document:
                    await C.send_document(d, document=filename, caption=caption, thumb=thumbnail, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                else:
                    if m.video:
                        width, height, duration = m.video.width, m.video.height, m.video.duration
                        await C.send_video(d, video=filename, caption=caption, thumb=thumbnail, width=width, height=height, duration=duration, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                    elif m.video_note:
                        await C.send_video_note(d, video_note=filename, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                    elif m.voice:
                        await C.send_voice(d, filename, caption=caption, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                    elif m.sticker:
                        await C.send_sticker(d, m.sticker.file_id)
                    elif m.audio:
                        await C.send_audio(d, audio=filename, caption=caption, thumb=thumbnail, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                    elif m.photo:
                        await C.send_photo(d, photo=filename, caption=caption, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                    else:
                        await C.send_document(d, document=filename, caption=caption, thumb=thumbnail, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                        
                if O.path.exists(F) and is_safe_path("/app", F): O.remove(F)
                await C.delete_messages(d, P.id)
                del W[u]
                return "Done."
            else:
                await m.copy(chat_id=d)
                return "Copied."
        elif m.text:
            await (C.send_message(d, text=m.text.markdown) if link_type == "private" else m.copy(chat_id=d))
            return "Sent."
    except Exception as e:
        return f"Error: {e}"

@X.on_message(F.command("start"))
async def sex(C, m: M):
    await m.reply_text("Welcome to bot. Use /batch to start magic.")

@X.on_message(F.command("batch"))
async def B(C, m: M):
    U = m.from_user.id
    Z[U] = {"step": "start", "message": m}
    await m.reply_text("Send start link.")

@X.on_message(F.command("cancel"))
async def N(C, m: M):
    U = m.from_user.id
    if U in W:
        W[U]["cancel"] = True
        await m.reply_text("Cancelling...")
    else:
        await m.reply_text("No active task.")

@X.on_message(F.command("usage"))
async def usage(C, m: M):
    # Fetch live system statistics
    cpu_usage = psutil.cpu_percent()  # in percentage
    memory_usage = psutil.virtual_memory().percent  # in percentage
    disk_usage = psutil.disk_usage('/').percent  # in percentage

    usage_text = (
        f"**Resource Utilization:**\n\n"
        f"CPU Usage: {cpu_usage}%\n"
        f"Memory Usage: {memory_usage}%\n"
        f"Disk Usage: {disk_usage}%\n"
    )
    
    await m.reply_text(usage_text)

@X.on_message(F.command("setthumbnail"))
async def set_thumbnail_command(C, m: M):
    await set_thumbnail(C, m)

@X.on_message(F.command("removethumbnail"))
async def remove_thumbnail_command(C, m: M):
    await remove_thumbnail(C, m)

@X.on_message(F.command("setremovetext"))
async def set_remove_text_command(C, m: M):
    await set_remove_text(C, m)

@X.on_message(F.command("clearremovetext"))
async def clear_remove_text_command(C, m: M):
    await clear_remove_text(C, m)

@X.on_message(F.command("setaddtext"))
async def set_add_text_command(C, m: M):
    await set_add_text(C, m)

@X.on_message(F.command("clearaddtext"))
async def clear_add_text_command(C, m: M):
    await clear_add_text(C, m)

@X.on_message(F.text & ~F.command(["start", "batch", "cancel", "usage", "setthumbnail", "removethumbnail", "setremovetext", "clearremovetext", "setaddtext", "clearaddtext"]))
async def H(C, m: M):
    U = m.from_user.id
    if U not in Z:
        return
    S = Z[U].get("step")
    if S == "start":
        L = m.text
        I, D, link_type = E(L)
        if not I or not D:
            await m.reply_text("Invalid link. Please check the format.")
            del Z[U]
            return
        Z[U].update({"step": "count", "cid": I, "sid": D, "lt": link_type})
        await m.reply_text("How many messages?")
    
    elif S == "count":
        if not m.text.isdigit():
            await m.reply_text("Enter a valid number.")
            return
        Z[U].update({"step": "use_config", "num": int(m.text)})
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Use Config Files", callback_data=f"use_config_{U}")],
             [InlineKeyboardButton("Enter Custom Text", callback_data=f"custom_text_{U}")]]
        )
        await m.reply_text("Use configuration files or enter custom text?", reply_markup=keyboard)

@X.on_callback_query(F.regex(r"use_config_(\d+)"))
async def use_config_callback(C, cq):
    U = int(cq.data.split("_")[-1])
    Z[U].update({"step": "set_media_type", "use_config": True})
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Default", callback_data=f"default_{U}")],
         [InlineKeyboardButton("All Media", callback_data=f"all_media_{U}")],
         [InlineKeyboardButton("All Document", callback_data=f"all_document_{U}")]]
    )
    await cq.message.reply_text("Send media as:", reply_markup=keyboard)

@X.on_callback_query(F.regex(r"custom_text_(\d+)"))
async def custom_text_callback(C, cq):
    U = int(cq.data.split("_")[-1])
    Z[U]["step"] = "custom_text_input"
    await cq.message.reply_text("Enter text to remove:")

@X.on_callback_query(F.regex(r"default_(\d+)"))
async def default_callback(C, cq):
    U = int(cq.data.split("_")[-1])
    Z[U].update({"step": "dest", "media_type": "default"})
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Use Current Chat", callback_data=f"use_current_chat_{U}")],
         [InlineKeyboardButton("Enter Chat ID Manually", callback_data=f"enter_chat_id_{U}")]]
    )
    await cq.message.reply_text("Set destination chat ID:", reply_markup=keyboard)

@X.on_callback_query(F.regex(r"all_media_(\d+)"))
async def all_media_callback(C, cq):
    U = int(cq.data.split("_")[-1])
    Z[U].update({"step": "dest", "media_type": "all_media"})
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Use Current Chat", callback_data=f"use_current_chat_{U}")],
         [InlineKeyboardButton("Enter Chat ID Manually", callback_data=f"enter_chat_id_{U}")]]
    )
    await cq.message.reply_text("Set destination chat ID:", reply_markup=keyboard)

@X.on_callback_query(F.regex(r"all_document_(\d+)"))
async def all_document_callback(C, cq):
    U = int(cq.data.split("_")[-1])
    Z[U].update({"step": "dest", "media_type": "all_document"})
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Use Current Chat", callback_data=f"use_current_chat_{U}")],
         [InlineKeyboardButton("Enter Chat ID Manually", callback_data=f"enter_chat_id_{
