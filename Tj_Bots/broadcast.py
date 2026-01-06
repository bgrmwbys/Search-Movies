from pyrogram import Client, filters
from config import ADMINS
from database import db
import asyncio
import time

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_users(client, message):
    is_forward = False
    if len(message.command) > 1 and message.command[1] == "-f":
        is_forward = True
        msg_text = "🚀 מתחיל שידור (Forward)..."
    else:
        msg_text = "🚀 מתחיל שידור (Copy)..."

    msg = await message.reply(msg_text, quote=True)
    users = await db.get_all_users()
    
    count = 0
    blocked = 0
    last_update_time = time.time()
    
    async for user in users:
        try:
            if is_forward:
                await message.reply_to_message.forward(user['_id'])
            else:
                await message.reply_to_message.copy(user['_id'])
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            blocked += 1
            
        if time.time() - last_update_time >= 5:
            try:
                await msg.edit(f"⏳ שידור למשתמשים...\n✅ נשלח: {count}\n🚫 נכשל: {blocked}")
                last_update_time = time.time()
            except: pass
            
    await msg.edit(f"✅ **שידור למשתמשים הסתיים.**\n\n📫 נשלח ל: {count}\n🚫 נכשל/נחסם: {blocked}")

@Client.on_message(filters.command("broadcast_groups") & filters.user(ADMINS) & filters.reply)
async def broadcast_groups(client, message):
    msg = await message.reply("🚀 מתחיל שידור לקבוצות...", quote=True)
    groups = await db.get_all_groups()
    
    count = 0
    failed = 0
    last_update_time = time.time()
    
    async for group in groups:
        try:
            await message.reply_to_message.copy(group['_id'])
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1
            
        if time.time() - last_update_time >= 5:
            try:
                await msg.edit(f"⏳ שידור לקבוצות...\n✅ נשלח: {count}\n🚫 נכשל: {failed}")
                last_update_time = time.time()
            except: pass
            
    await msg.edit(f"✅ **שידור לקבוצות הסתיים.**\n\n📫 נשלח ל: {count}\n🚫 נכשל: {failed}")
