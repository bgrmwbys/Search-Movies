from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import db
from .utils import is_admin

@Client.on_message(filters.command("settings") & filters.group)
async def settings_cmd(client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("⛔ פקודה זו זמינה למנהלים בלבד.", quote=True)
    
    await send_settings_panel(message.chat.id, message)

async def send_settings_panel(chat_id, message, is_edit=False):
    settings = await db.get_settings(chat_id)
    
    res_val = settings.get('results_per_page', 10)
    disp_val = settings.get('display_mode', 'inline')
    trig_val = settings.get('search_trigger', 'all')

    text = "<b>⚙️ הגדרות הבוט ⚙️</b>\n\nלחץ על הערך לשינוי.\n"
    
    res_btn = str(res_val)
    disp_btn = 'כפתורים' if disp_val == 'inline' else 'טקסט'
    trig_btn = 'כל הודעה' if trig_val == 'all' else 'רק עם !'

    buttons = [
        [InlineKeyboardButton(res_btn, callback_data="set_res"), InlineKeyboardButton('מספר תוצאות:', callback_data="noop")],
        [InlineKeyboardButton(disp_btn, callback_data="set_disp"), InlineKeyboardButton('מצב תצוגה:', callback_data="noop")],
        [InlineKeyboardButton(trig_btn, callback_data="set_trig"), InlineKeyboardButton('טריגר חיפוש:', callback_data="noop")],
        [InlineKeyboardButton('✘ סגור תפריט ✘', callback_data="close_settings")]
    ]
    
    markup = InlineKeyboardMarkup(buttons)

    if is_edit:
        await message.edit_text(text, reply_markup=markup)
    else:
        await message.reply(text, reply_markup=markup, quote=True)

@Client.on_callback_query(filters.regex(r"^(set_|close_settings)"))
async def settings_callback(client, query: CallbackQuery):
    chat_id = query.message.chat.id
    
    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("⛔ למנהלים בלבד!", show_alert=True)
    
    data = query.data

    if data == "close_settings":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            pass 
        return

    settings = await db.get_settings(chat_id)
    
    if data == "set_res":
        new_val = 5 if settings.get('results_per_page', 10) == 10 else 10
        await db.update_settings(chat_id, 'results_per_page', new_val)
        
    elif data == "set_disp":
        curr = settings.get('display_mode', 'inline')
        new_val = 'text' if curr == 'inline' else 'inline'
        await db.update_settings(chat_id, 'display_mode', new_val)
        
    elif data == "set_trig":
        curr = settings.get('search_trigger', 'all')
        new_val = 'bang' if curr == 'all' else 'all'
        await db.update_settings(chat_id, 'search_trigger', new_val)
        
    await query.answer("ההגדרה עודכנה ✅")
    await send_settings_panel(chat_id, query.message, is_edit=True)
