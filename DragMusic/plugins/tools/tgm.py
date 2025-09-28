import requests
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from DragMusic import app

def upload_to_catbox(file_path):
    """Uploads a file to Catbox and returns the file URL."""
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as file:
        response = requests.post(
            url,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": file}
        )
    if response.status_code == 200:
        return response.text.strip()
    else:
        raise Exception(f"Cᴀᴛʙᴏx ᴜᴘʟᴏᴀᴅ ғᴀɪʟᴇᴅ: {response.text}")

@app.on_message(filters.command("tgm"))
def ul(_, message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return message.reply("Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴏʀ ᴍᴇᴅɪᴀ ᴛᴏ ᴜᴘʟᴏᴀᴅ.")

    i = message.reply("Downloading...")
    path = reply.download()

    if not path:
        return i.edit("Fᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇ ғɪʟᴇ.")

    try:
        # Upload to Catbox
        file_url = upload_to_catbox(path)

        # Create a button with the Catbox link
        button = InlineKeyboardButton("ᴄᴀᴛʙᴏx ʟɪɴᴋ", url=file_url)
        markup = InlineKeyboardMarkup([[button]])

        # Send a reply with the button
        i.edit("Yᴏᴜʀ ғɪʟᴇ ʜᴀs ʙᴇᴇɴ ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ Cᴀᴛʙᴏx:", reply_markup=markup)
    except Exception as e:
        i.edit(f"An error occurred: {str(e)}")
