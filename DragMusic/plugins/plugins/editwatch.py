import traceback
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.raw.types import UpdateEditMessage, UpdateEditChannelMessage
from pyrogram.types import Message
from DragMusic import app
from pymongo import MongoClient
from config import MONGO_DB_URI

# MongoDB setup
mongo = MongoClient(MONGO_DB_URI)
db = mongo["AnonX"]
group_col = db["editwatch_groups"]
auth_col = db["editwatch_auth_users"]

# Check if user is admin
async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

# Enable/Disable edit scan
@app.on_message(filters.command("editscan") & filters.group)
async def editscan_toggle(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("Only admins can use this command.")

    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply_text("Usage: `/editscan enable` or `/editscan disable`")

    cmd = args[1].lower()
    if cmd == "enable":
        group_col.update_one({"chat_id": chat_id}, {"$set": {"enabled": True}}, upsert=True)
        await message.reply_text("✅ Edit scan enabled.")
    elif cmd == "disable":
        group_col.delete_one({"chat_id": chat_id})
        await message.reply_text("❌ Edit scan disabled.")
    else:
        await message.reply_text("Invalid option. Use `enable` or `disable`.")

# Authorize or remove user with /sauth
@app.on_message(filters.command("sauth") & filters.group)
async def sauth_handler(client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return await message.reply_text("Only admins can use this command.")

    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply_text("Reply to a user's message to auth/remove them.")

    target_user_id = message.reply_to_message.from_user.id
    args = message.text.split(None, 1)
    cmd = args[1].lower() if len(args) > 1 else "add"

    if cmd == "remove":
        auth_col.update_one(
            {"chat_id": chat_id},
            {"$pull": {"users": target_user_id}}
        )
        await message.reply_text("❌ User has been removed from authorized list.")
    else:
        auth_col.update_one(
            {"chat_id": chat_id},
            {"$addToSet": {"users": target_user_id}},
            upsert=True
        )
        await message.reply_text("✅ User has been authorized to edit without deletion.")

# Monitor edits via raw updates
@app.on_raw_update(group=-1)
async def raw_edit_delete(client: Client, update, users, chats):
    if isinstance(update, (UpdateEditMessage, UpdateEditChannelMessage)):
        msg = update.message

        try:
            if getattr(msg, "edit_hide", False):
                return

            if not hasattr(msg, "from_id") or not hasattr(msg, "peer_id"):
                return

            user_id = msg.from_id.user_id
            chat_id = getattr(msg.peer_id, "channel_id", None)
            if chat_id:
                chat_id = int(f"-100{chat_id}")
            else:
                chat_id = getattr(msg.peer_id, "chat_id", None)

            if not chat_id:
                return

            group_data = group_col.find_one({"chat_id": chat_id})
            if not group_data or not group_data.get("enabled"):
                return

            # Skip admins
            try:
                member = await client.get_chat_member(chat_id, user_id)
                if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    return
            except:
                pass

            # Check if user is in auth list
            auth_data = auth_col.find_one({"chat_id": chat_id})
            if auth_data and user_id in auth_data.get("users", []):
                return

            # Delete message
            await client.delete_messages(chat_id, msg.id)
            user = await client.get_users(user_id)
            await client.send_message(
                chat_id,
                f"{user.mention} edited a message — I deleted it."
            )

        except Exception:
            print("Error during edit scan:\n", traceback.format_exc()) 