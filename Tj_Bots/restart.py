import os
import sys
from pyrogram import Client, filters
from config import ADMINS

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart_bot(client, message):
    msg = await message.reply("🔄 מפעיל מחדש...", quote=True)
    
    with open("restart.txt", "w") as f:
        f.write(f"{message.chat.id} {msg.id}")
    
    os.execl(sys.executable, sys.executable, "bot.py")
