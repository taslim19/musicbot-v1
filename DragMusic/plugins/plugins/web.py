from pyrogram import filters
from pyrogram.enums import ChatAction, ParseMode
from DragMusic import app
import aiohttp

# Function to fetch data from the web API
async def fetch_data_from_api(question):
    url = "https://app-paal-chat-1003522928061.us-east1.run.app/api/chat/web"
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    payload = {"prompt": question, "bid": "edwo6pg1"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            return data.get("answer", "No response received.")

# Command handler for /web
@app.on_message(filters.command("web"))
async def web_command(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Indicate typing action
    await app.send_chat_action(chat_id, ChatAction.TYPING)
    
    if len(message.command) < 2:
        await message.reply_text("Exᴀᴍᴘʟᴇ ᴜsᴀɢᴇ: /web [your search!]")
        return
    
    question = " ".join(message.command[1:])  # Get the query from command arguments
    response = await fetch_data_from_api(question)
    
    formatted_response = f"<blockquote>{response}</blockquote>"
    
    await message.reply_text(formatted_response, parse_mode=ParseMode.HTML)
