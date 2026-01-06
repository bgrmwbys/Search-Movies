from pyrogram import Client, filters
from gtts import gTTS
from io import BytesIO
import asyncio

def convert_to_audio(text):
    lang = 'iw' if any("\u0590" <= c <= "\u05EA" for c in text) else 'en'
    
    tts = gTTS(text=text, lang=lang)
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.name = "tts.mp3"
    audio_file.seek(0)
    return audio_file

@Client.on_message(filters.command("tts"))
async def tts_handler(client, message):
    text = ""
    
    if message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
    elif len(message.command) > 1:
        text = message.text.split(maxsplit=1)[1]
    else:
        return await message.reply("⚠️ **שימוש שגוי.**\nתגיב `/tts` על הודעה או כתוב טקסט ליד הפקודה.", quote=True)

    status = await message.reply("🎧 **מעבד סאונד...**", quote=True)

    try:
        loop = asyncio.get_running_loop()
        audio = await loop.run_in_executor(None, convert_to_audio, text)
        
        await message.reply_audio(audio, quote=True)
        await status.delete()
        
    except Exception as e:
        await status.edit(f"❌ שגיאה: `{e}`")