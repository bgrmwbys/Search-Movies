from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMINS
from database import db
import random
import asyncio

CAPTCHA_DATA = {}

@Client.on_message(filters.command("clean") & filters.user(ADMINS))
async def clean_command(client, message):
    buttons = [
        [InlineKeyboardButton("🗑️ ניקוי קבצים", callback_data="ask_clean_files")],
        [InlineKeyboardButton("🗑️ ניקוי משתמשים", callback_data="ask_clean_users")],
        [InlineKeyboardButton("🗑️ ניקוי קבוצות", callback_data="ask_clean_groups")],
        [InlineKeyboardButton("❌ ביטול", callback_data="clean_cancel")]
    ]
    await message.reply("⚠️ **תפריט ניקוי נתונים**\nבחר מה ברצונך למחוק מהדאטה בייס:", reply_markup=InlineKeyboardMarkup(buttons), quote=True)

@Client.on_callback_query(filters.regex(r"^ask_clean_"))
async def ask_clean_callback(client, query):
    action = query.data.replace("ask_clean_", "")
    user_id = query.from_user.id
    
    num1 = random.randint(1, 9)
    num2 = random.randint(1, 9)
    correct_ans = num1 + num2
    
    CAPTCHA_DATA[(query.message.chat.id, user_id)] = {
        'answer': correct_ans,
        'action': action
    }
    
    answers = [correct_ans, correct_ans + random.randint(1, 3), correct_ans - random.randint(1, 3)]
    random.shuffle(answers)
    
    btns = []
    for ans in answers:
        btns.append(InlineKeyboardButton(str(ans), callback_data=f"solve_clean_{ans}"))
    
    markup = InlineKeyboardMarkup([btns, [InlineKeyboardButton("❌ ביטול", callback_data="clean_cancel")]])
    
    target_name = "קבצים" if action == "files" else "משתמשים" if action == "users" else "קבוצות"
    await query.message.edit_text(
        f"⚠️ **אימות אבטחה**\n\nאתה עומד למחוק את כל ה-**{target_name}**!\nכדי לאשר, פתור את התרגיל:\n\n**{num1} + {num2} = ?**",
        reply_markup=markup
    )

@Client.on_callback_query(filters.regex(r"^solve_clean_"))
async def solve_clean_callback(client, query):
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    key = (chat_id, user_id)
    
    if key not in CAPTCHA_DATA:
        return await query.answer("הזמן עבר, נסה שוב.", show_alert=True)
    
    user_ans = int(query.data.split("_")[-1])
    correct_ans = CAPTCHA_DATA[key]['answer']
    action = CAPTCHA_DATA[key]['action']
    
    if user_ans != correct_ans:
        del CAPTCHA_DATA[key]
        await query.message.delete()
        return await query.answer("❌ תשובה שגויה. הפעולה בוטלה.", show_alert=True)
    
    count = 0
    if action == "files":
        count = await db.delete_all_files()
        msg = f"✅ נמחקו {count} קבצים מהמערכת."
    elif action == "users":
        count = await db.delete_all_users()
        msg = f"✅ נמחקו {count} משתמשים מהמערכת."
    elif action == "groups":
        count = await db.delete_all_groups()
        msg = f"✅ נמחקו {count} קבוצות מהמערכת."
    
    del CAPTCHA_DATA[key]
    await query.message.edit_text(msg)

@Client.on_callback_query(filters.regex("clean_cancel"))
async def clean_cancel(client, query):
    await query.message.delete()
