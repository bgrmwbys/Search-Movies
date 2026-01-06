from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote

@Client.on_message(filters.command(["share", "share_text", "sharetext"]))
async def share_text_handler(client, message):
    text_to_share = ""

    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        text_to_share = message.reply_to_message.text or message.reply_to_message.caption
    elif len(message.command) > 1:
        text_to_share = message.text.split(None, 1)[1]

    if not text_to_share:
        return await message.reply_text("❌ אנא הגב על הודעת טקסט או כתוב טקסט לאחר הפקודה.", quote=True)

    encoded_text = quote(text_to_share)
    share_link = f"https://t.me/share/url?url={encoded_text}"

    await message.reply_text(
        f"**הנה קישור השיתוף שלך:**\n\n`{share_link}`",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 שתף עכשיו", url=share_link)],
            [InlineKeyboardButton("❌ סגור", callback_data="closea")]
        ]),
        quote=True,
        disable_web_page_preview=True
    )