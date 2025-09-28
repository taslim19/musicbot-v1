import os
import re
import subprocess
import sys
import traceback
from inspect import getfullargspec
from io import StringIO
from time import time

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery

from DragMusic import app
from config import OWNER_ID
from DragMusic.core.mongo import mongodb
from DragMusic import userbot  # Ensure userbot is imported
from DragMusic.utils.gemini import get_gemini_fix

async def aexec(code, client, message):
    afkdb = mongodb.afk

    # Create a local execution environment
    local_vars = {
        "client": client,
        "message": message,
        "afkdb": afkdb,
        "userbot": userbot,  # Add userbot to the eval environment
        "get_afk_users": lambda: afkdb.find({"user_id": {"$gt": 0}}).to_list(1000),
    }

    # Prepare the async wrapper function
    exec(
        f"async def __aexec(client, message):\n"
        + "".join(f"    {l}\n" for l in code.split("\n")),
        globals(),
        local_vars,
    )

    return await local_vars["__aexec"](client, message)


async def edit_or_reply(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user.is_self else msg.reply
    await func(**kwargs)


@app.on_message(filters.text & filters.user(OWNER_ID) & ~filters.forwarded & ~filters.via_bot)
async def executor(client: app, message: Message):
    """Executes Python or shell commands based on plain text input."""
    if not message.text:
        return  # Prevent errors when message.text is None

    if message.text.startswith("eval"):
        if len(message.text.split()) < 2:
            return await edit_or_reply(message, text="<b>ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴɴᴀ ᴇxᴇᴄᴜᴛᴇ ʙᴀʙʏ ?</b>")
        
        cmd = message.text.split(" ", maxsplit=1)[1]
        t1 = time()
        old_stderr, old_stdout = sys.stderr, sys.stdout
        redirected_output = sys.stdout = StringIO()
        redirected_error = sys.stderr = StringIO()
        stdout, stderr, exc = None, None, None
        gemini_suggestion = None
        gemini_result = None
        try:
            await aexec(cmd, client, message)
        except Exception:
            exc = traceback.format_exc()
            # Try Gemini fix
            gemini_suggestion = await get_gemini_fix(exc, cmd, mode="python")
            if gemini_suggestion and gemini_suggestion.strip() != cmd.strip():
                # Try to run Gemini's suggestion
                try:
                    redirected_output = sys.stdout = StringIO()
                    redirected_error = sys.stderr = StringIO()
                    await aexec(gemini_suggestion, client, message)
                    gemini_result = redirected_output.getvalue() or "Success"
                except Exception as e2:
                    gemini_result = f"Gemini fix also failed: {traceback.format_exc()}"
        stdout, stderr = redirected_output.getvalue(), redirected_error.getvalue()
        sys.stdout, sys.stderr = old_stdout, old_stderr
        
        evaluation = exc or stderr or stdout or "Success"
        final_output = f"<b>⥤ ʀᴇsᴜʟᴛ :</b>\n<pre language='python'>{evaluation}</pre>"
        if gemini_suggestion:
            final_output += f"\n\n<b>Gemini Suggestion:</b>\n<pre language='python'>{gemini_suggestion}</pre>"
            if gemini_result:
                final_output += f"\n<b>Gemini Result:</b>\n<pre language='python'>{gemini_result}</pre>"
        
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Runtime: {round(t2-t1, 3)}s", callback_data=f"runtime {round(t2-t1, 3)}"),
                    InlineKeyboardButton(" Close", callback_data=f"close|{message.from_user.id}"),
                ]
            ]
        )

        await edit_or_reply(message, text=final_output, reply_markup=keyboard)

    elif message.text.startswith("sh"):
        """Executes shell commands."""
        if len(message.text.split()) < 2:
            return await edit_or_reply(message, text="<b>ᴇxᴀᴍᴩʟᴇ :</b>\nsh git pull")
        
        text = message.text.split(None, 1)[1]
        shell = re.split(r""" (?=(?:[^'\"]|'[^']*'|\"[^\"]*\")*$)""", text)
        t1 = time()  # Ensure t1 is defined before usage
        output = None
        exc = None
        gemini_suggestion = None
        gemini_result = None
        try:
            process = subprocess.Popen(shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = process.stdout.read().decode("utf-8").strip() or "None"
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(etype=exc_type, value=exc_obj, tb=exc_tb)
            exc = ''.join(errors)
            # Try Gemini fix
            gemini_suggestion = await get_gemini_fix(exc, text, mode="shell")
            if gemini_suggestion and gemini_suggestion.strip() != text.strip():
                shell2 = re.split(r""" (?=(?:[^'\"]|'[^']*'|\"[^\"]*\")*$)""", gemini_suggestion)
                try:
                    process2 = subprocess.Popen(shell2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    gemini_result = process2.stdout.read().decode("utf-8").strip() or "None"
                except Exception as e2:
                    gemini_result = f"Gemini fix also failed: {traceback.format_exc()}"
        t2 = time()
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(f"Runtime: {round(t2-t1, 3)}s", callback_data=f"runtime {round(t2-t1, 3)}"),
                    InlineKeyboardButton(" Close", callback_data=f"close|{message.from_user.id}"),
                ]
            ]
        )
        if exc:
            final_output = f"<b>ERROR :</b>\n<pre>{exc}</pre>"
            if gemini_suggestion:
                final_output += f"\n\n<b>Gemini Suggestion:</b>\n<pre>{gemini_suggestion}</pre>"
                if gemini_result:
                    final_output += f"\n<b>Gemini Result:</b>\n<pre>{gemini_result}</pre>"
        else:
            final_output = f"<b>OUTPUT :</b>\n<pre>{output}</pre>"
        await edit_or_reply(message, text=final_output, reply_markup=keyboard)

    await message.stop_propagation()


@app.on_callback_query(filters.regex(r"runtime"))
async def runtime_func_cq(_, cq):
    runtime = cq.data.split(None, 1)[1]
    await cq.answer(runtime, show_alert=True)


@app.on_callback_query(filters.regex(r"close\|"))
async def close_command(_, CallbackQuery: CallbackQuery):
    user_id = int(CallbackQuery.data.split("|")[1])
    if CallbackQuery.from_user.id != user_id:
        return await CallbackQuery.answer(" You can't close this!", show_alert=True)
    
    await CallbackQuery.message.delete()
    await CallbackQuery.answer()
