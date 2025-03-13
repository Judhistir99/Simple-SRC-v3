import os as O, re as R
from pyrogram import Client as C, filters as F
from pyrogram.types import Message as M, InlineKeyboardMarkup, InlineKeyboardButton
import time
from config import API_ID as A, API_HASH as H, BOT_TOKEN as T, SESSION as S
import sys

X, Y = C("X", api_id=A, api_hash=H, bot_token=T), C("Y", api_id=A, api_hash=H, session_string=S)
Z, W = {}, {}
try:
    Y.start()
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

async def K(batch_progress, c, t, C, h, m, start_time):
    global progress_cache
    p = (c / t) * 100
    step = int(p // 10) * 10

    if m not in progress_cache or progress_cache[m] != step or p >= 100:
        progress_cache[m] = step
        completed = int(p // 10)
        ongoing = 1 if p % 10 != 0 and p < 100 else 0
        incomplete = 10 - completed - ongoing

        bar = "🟩" * completed + "🟨" * ongoing + "🟥" * incomplete
        speed = (c / (time.time() - start_time)) / (1024 * 1024) if time.time() > start_time else 0
        eta = time.strftime("%M:%S", time.gmtime((t - c) / (speed * 1024 * 1024))) if speed > 0 else "00:00"
        
        # Batch progress bar
        batch_total, batch_completed = batch_progress
        batch_p = (batch_completed / batch_total) * 100
        batch_bar = "🟩" * (int(batch_p / 10)) + "🟥" * (10 - int(batch_p / 10))

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel ❌", callback_data=f"cancel_{m}"),
              InlineKeyboardButton("Restart 🔄", callback_data=f"restart_{m}"),
              InlineKeyboardButton("Reboot 🔄", callback_data=f"reboot_{m}")]]
        )

        await C.edit_message_text(h, m, f"__**Pyro Handler...**__\n\n{bar}\n\n📊 **__Completed__**: {p:.2f}%\n🚀 **__Speed**__: {speed:.2f} MB/s\n⏳ **__ETA**__: {eta}\n\n🔄 **Batch Progress**: {batch_bar} {batch_completed}/{batch_total}\n\n**All Set ☑️**", reply_markup=keyboard)
        if p >= 100:
            progress_cache.pop(m, None)

async def V(C, U, m, d, link_type, u, batch_progress):
    try:
        if m.media:
            st = time.time()
            if link_type == "private":
                P = await C.send_message(d, add_emojis("Downloading..."))
                W[u] = {"cancel": False, "progress": P.id}
                F = await U.download_media(m, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                
                if W.get(u, {}).get("cancel"):
                    await C.edit_message_text(d, P.id, add_emojis("Canceled."))
                    if O.path.exists(F): O.remove(F)
                    del W[u]
                    return add_emojis("Canceled.")
                
                if not F:
                    await C.edit_message_text(d, P.id, add_emojis("Failed."))
                    del W[u]
                    return add_emojis("Failed.")
                
                await C.edit_message_text(d, P.id, add_emojis("Uploading..."))
                th = "v3.jpg"
                if m.video:
                    width, height, duration = m.video.width, m.video.height, m.video.duration
                    await C.send_video(d, video=F, caption=m.caption.markdown, thumb=th, width=width, height=height, duration=duration, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                elif m.video_note: await C.send_video_note(d, video_note=F, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                elif m.voice: await C.send_voice(d, F, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                elif m.sticker: await C.send_sticker(d, m.sticker.file_id)
                elif m.audio: await C.send_audio(d, audio=F, caption=m.caption.markdown, thumb=th, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                elif m.photo: await C.send_photo(d, photo=F, caption=m.caption.markdown, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                elif m.document: await C.send_document(d, document=F, caption=m.caption.markdown, progress=K, progress_args=(batch_progress, C, d, P.id, st))
                O.remove(F)
                await C.delete_messages(d, P.id)
                del W[u]
                return add_emojis("Done.")
            else:
                await m.copy(chat_id=d)
                return add_emojis("Copied.")
        elif m.text:
            await (C.send_message(d, text=add_emojis(m.text.markdown)) if link_type == "private" else m.copy(chat_id=d))
            return add_emojis("Sent.")
    except Exception as e:
        return f"Error: {e}"

@X.on_message(F.command("start"))
async def sex(C, m: M):
    await m.reply_text(add_emojis("Welcome to bot. Use /batch to start magic."))

@X.on_message(F.command("batch"))
async def B(C, m: M):
    U = m.from_user.id
    Z[U] = {"step": "start"}
    await m.reply_text(add_emojis("Send start link."))

@X.on_message(F.command("cancel"))
async def N(C, m: M):
    U = m.from_user.id
    if U in W:
        W[U]["cancel"] = True
        await m.reply_text(add_emojis("Cancelling..."))
    else:
        await m.reply_text(add_emojis("No active task."))

@X.on_message(F.command("usage"))
async def usage(C, m: M):
    # Sample data for resource utilization
    cpu_usage = 50  # in percentage
    memory_usage = 1024  # in MB
    disk_usage = 2048  # in MB

    usage_text = (
        f"**Resource Utilization:**\n"
        f"CPU Usage: {cpu_usage}%\n"
        f"Memory Usage: {memory_usage} MB\n"
        f"Disk Usage: {disk_usage} MB\n"
    )
    
    await m.reply_text(add_emojis(usage_text))

@X.on_message(F.command("restart"))
async def restart(C, m: M):
    U = m.from_user.id
    if U in W:
        W[U]["cancel"] = True
        await m.reply_text(add_emojis("Restarting..."))
        # Reset the progress and restart the batch process
        Z[U]["step"] = "process"
        await process_batch(C, m)
    else:
        await m.reply_text(add_emojis("No active task."))

@X.on_message(F.command("reboot"))
async def reboot(C, m: M):
    await m.reply_text(add_emojis("Rebooting..."))
    O.execv(sys.executable, ['python'] + sys.argv)

@X.on_callback_query(F.regex(r"cancel_(\d+)"))
async def cancel_callback(C, cq):
    U = cq.from_user.id
    if U in W:
        W[U]["cancel"] = True
        await cq.answer("Cancelling...")
    else:
        await cq.answer("No active task.")

@X.on_callback_query(F.regex(r"restart_(\d+)"))
async def restart_callback(C, cq):
    U = cq.from_user.id
    if U in W:
        W[U]["cancel"] = True
        await cq.answer("Restarting...")
        # Reset the progress and restart the batch process
        Z[U]["step"] = "process"
        await process_batch(C, cq.message)
    else:
        await cq.answer("No active task.")

@X.on_callback_query(F.regex(r"reboot_(\d+)"))
async def reboot_callback(C, cq):
    await cq.answer("Rebooting...")
    O.execv(sys.executable, ['python'] + sys.argv)

async def process_batch(C, m):
    U = m.from_user.id
    I, S, N, link_type = Z[U]["cid"], Z[U]["sid"], Z[U]["num"], Z[U]["lt"]
    R = 0
    pt = await m.reply_text(add_emojis("Trying hard 🐥..."))
    
    for i in range(N):
        M = S + i
        msg = await J(C, Y, I, M, link type)
        if msg:
            res = await V(C, Y, msg, Z[U]["did"], link type, U, (N, i+1))
            await pt.edit(f"{i+1}/{N}: {res}")
            if "Done" in res: R += 1
        else:
            await m.reply_text(f"{M} not found.")
    
    await m.reply_text(f"Batch Completed ✅")
    del Z[U]

@X.on_message(F.text & ~F.command(["start", "batch", "cancel", "restart", "reboot"]))
async def H(C, m: M):
    U = m.from_user.id
    if U not in Z:
        return
    S = Z[U].get("step")
    if S == "start":
        L = m.text
        I, D, link type = E(L)
        if not I or not D:
            await m.reply_text(add_emojis("Invalid link. Please check the format."))
            del Z[U]
            return
        Z[U].update({"step": "count", "cid": I, "sid": D, "lt": link type})
        await m.reply_text(add_emojis("How many messages?"))
    
    elif S == "count":
        if not m.text.isdigit():
            await m.reply_text(add_emojis("Enter a valid number."))
            return
        Z[U].update({"step": "dest", "num": int(m.text)})
        await m.reply_text(add_emojis("Send destination chat ID."))
    
    elif S == "dest":
        D = m.text
        Z[U].update({"step": "process", "did": D})
        
        I, S, N, link type = Z[U]["cid"], Z[U]["sid"], Z[U]["num"], Z[U]["lt"]
        R = 0
        pt = await m.reply_text(add_emojis("Trying hard 🐥..."))
        
        for i in range(N):
            M = S + i
            msg = await J(C, Y, I, M, link type)
            if msg:
                res = await V(C, Y, msg, D, link type, U, (N, i+1))
                await pt.edit(f"{i+1}/{N}: {res}")
                if res and "Done" in res: 
                    R += 1
            else:
                await m.reply_text(f"{M} not found.")
        
        await m.reply_text(f"Batch Completed ✅")
        del Z[U]

print("Bot started successfully!!")
X.run()
