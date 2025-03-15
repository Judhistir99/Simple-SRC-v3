import os as O

def is_safe_path(basedir, path, follow_symlinks=True):
    if follow_symlinks:
        return O.path.realpath(path).startswith(basedir)
    return O.path.abspath(path).startswith(basedir)

def read_remove_text():
    file_path = O.path.join("config", "setremove.txt")
    if O.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read().strip()
    return ""

def read_add_text():
    file_path = O.path.join("config", "addtext.txt")
    if O.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read().strip()
    return ""

async def set_thumbnail(C, m):
    if m.reply_to_message and m.reply_to_message.photo:
        file_path = O.path.join("/app", "thumbnail.jpg")
        await m.reply_to_message.download(file_path)
        await m.reply_text("Thumbnail set successfully!")
    else:
        await m.reply_text("Please reply to a photo to set it as the thumbnail.")

async def remove_thumbnail(C, m):
    file_path = O.path.join("/app", "thumbnail.jpg")
    if O.path.exists(file_path):
        O.remove(file_path)
        await m.reply_text("Thumbnail removed successfully!")
    else:
        await m.reply_text("No thumbnail set.")

async def set_remove_text(C, m):
    U = m.from_user.id
    text_to_remove = m.text.split(" ", 1)[1] if len(m.text.split(" ", 1)) > 1 else ""
    if text_to_remove:
        file_path = O.path.join("config", "setremove.txt")
        with open(file_path, "w") as f:
            f.write(text_to_remove)
        await m.reply_text(f"Text to remove set: {text_to_remove}")
    else:
        await m.reply_text("Please provide the text to remove.")

async def clear_remove_text(C, m):
    file_path = O.path.join("config", "setremove.txt")
    if O.path.exists(file_path):
        O.remove(file_path)
        await m.reply_text("Text to remove cleared.")
    else:
        await m.reply_text("No text to remove set.")

async def set_add_text(C, m):
    add_text = m.text.split(" ", 1)[1] if len(m.text.split(" ", 1)) > 1 else ""
    if add_text:
        file_path = O.path.join("config", "addtext.txt")
        with open(file_path, "w") as f:
            f.write(add_text)
        await m.reply_text(f"Text to add set: {add_text}")
    else:
        await m.reply_text("Please provide the text to add.")

async def clear_add_text(C, m):
    file_path = O.path.join("config", "addtext.txt")
    if O.path.exists(file_path):
        O.remove(file_path)
        await m.reply_text("Text to add cleared.")
    else:
        await m.reply_text("No text to add set.")
