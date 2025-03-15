import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

progress_cache = {}

async def K(batch_progress, c, t, C, h, m, start_time):
    global progress_cache
    p = (c / t) * 100
    step = int(p // 10) * 10

    if m not in progress_cache or progress_cache[m] != step or p >= 100:
        progress_cache[m] = step
        completed = int(p // 10)
        ongoing = 1 if p % 10 != 0 and p < 100 else 0
        incomplete = 10 - completed - ongoing

        bar = "🟩" * completed + "🟧" * ongoing + "⬜" * incomplete
        speed = (c / (time.time() - start_time)) / (1024 * 1024) if time.time() > start_time else 0
        eta = time.strftime("%M:%S", time.gmtime((t - c) / (speed * 1024 * 1024))) if speed > 0 else "00:00"
        
        # Batch progress bar
        batch_total, batch_completed = batch_progress
        batch_p = (batch_completed / batch_total) * 100
        batch_bar = "🟩" * (int(batch_p / 10)) + "⬜" * (10 - int(batch_p / 10))

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Cancel ❌", callback_data=f"cancel_{m}"),
              InlineKeyboardButton("Restart 🔄", callback_data=f"restart_{m}"),
              InlineKeyboardButton("Reboot 🔄", callback_data=f"reboot_{m}")]]
        )

        await C.edit_message_text(h, m, f"__**Pyro Handler...**__\n\n{bar}\n\n📊 **__Completed__**: {p:.2f}%\n🚀 **__Speed**__: {speed:.2f} MB/s\n⏳ **__ETA**__: {eta}\n\n🔄 **Batch Progress**: {batch_bar}")
        if p >= 100:
            progress_cache.pop(m, None)
