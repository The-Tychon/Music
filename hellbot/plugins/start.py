import datetime
import time

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ..config import BOT_USERNAME as BUN, OWNER
from ..helper.database.db import get_collections
from ..helper.filters import command, commandpro
from ..helper.miscs import clog, get_file_id


GROUPS = get_collections("GROUPS")
BOT_PIC = "https://te.legra.ph/file/a3685d590ff1c7ed32978.jpg"
START_TIME = datetime.datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60 * 60 * 24),
    ("hour", 60 * 60),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append("{} {}{}".format(amount, unit, "" if amount == 1 else "s"))
    return ", ".join(parts)


@Client.on_message(command("slovesp") & filters.private & ~filters.edited)
async def start_(client: Client, message: Message):
    await message.reply_photo(
        photo=BOT_PIC,
        caption=f"<b><i>Hello there!! \nI'm a Telegram voice chat music player by @Itz_me_tychon. Enjoy my advanced features along with a simple and sexy interface</b></i>",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🎶Add In Group🔥",
                        url=f"https://t.me/{BUN}?startgroup=true",
                    )
                ],
                [
                    InlineKeyboardButton("Guide 📜", callback_data="cbhowtouse"),
                    InlineKeyboardButton("Commands 📌", callback_data="cbcmds"),
                ],
                [
                    InlineKeyboardButton(
                        "🔥Channel🔮", url=f"https://t.me/electro_updates"
                    ),
                    InlineKeyboardButton(
                        "🔮Support🔥", url="https://t.me/electrobot_support"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🎶Ashiq🔥", url=f"tg://openmessage?user_id={OWNER}"
                    )
                ]
           ]
        ),
    )


@Client.on_message(commandpro(["/slovesp", "/zinda"]) & filters.group & ~filters.edited)
async def start(client: Client, message: Message):
    gid = message.chat.id
    gidtype = message.chat.type
    if gidtype in ["supergroup", "group"] and not await (GROUPS.find_one({"id": gid})):
        try:
            gidtitle = message.chat.username
        except KeyError:
            gidtitle = message.chat.title
        await GROUPS.insert_one({"id": gid, "grp": gidtitle})
        await clog("HELLBOT_MUSIC", f"Bot added to a new group\n\n{gidtitle}\nID: `{gid}`", "NEW_GROUP")
    await message.reply_photo(photo=BOT_PIC, caption=f"<b><i>🤠 Yo!! Wanna listen to some music now?</b></i>")


@Client.on_message(command(["ping", f"ping@{BUN}"]) & ~filters.edited)
async def ping(client: Client, message: Message):
    gid = message.chat.id
    gidtype = message.chat.type
    if gidtype in ["supergroup", "group"] and not await (GROUPS.find_one({"id": gid})):
        try:
            gidtitle = message.chat.username
        except KeyError:
            gidtitle = message.chat.title
        await GROUPS.insert_one({"id": gid, "grp": gidtitle})
        await clog("HELLBOT_MUSIC", f"Bot added to a new group\n\n{gidtitle}\nID: `{gid}`", "NEW_GROUP")
    start = time.time()
    m_reply = await message.reply_text("<b><i>Pong!</b></i>")
    _ping = time.time() - start
    current_time = datetime.datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await m_reply.edit_text(f"<b><i>• Pong!</b></i> <i>{_ping * 1000:.3f} ms</i> \n<b><i>• Uptime:</b></i> <code>{uptime}</code> \n")


@Client.on_message(command(["id", f"id@{BUN}"]))
async def showid(_, message: Message):
    gid = message.chat.id
    gidtype = message.chat.type
    if gidtype in ["supergroup", "group"] and not await (GROUPS.find_one({"id": gid})):
        try:
            gidtitle = message.chat.username
        except KeyError:
            gidtitle = message.chat.title
        await GROUPS.insert_one({"id": gid, "grp": gidtitle})
        await clog("HELLBOT_MUSIC", f"Bot added to a new group\n\n{gidtitle}\nID: `{gid}`", "NEW_GROUP")
    if gidtype == "private":
        user_id = message.chat.id
        await message.reply_text(f"<b><i>Your ID:</b></i> <code>{user_id}</code>")
    elif gidtype in ["group", "supergroup"]:
        _id = ""
        _id += f"<b><i>Chat ID:</b></i> <code>{message.chat.id}</code>\n"
        if message.reply_to_message:
            _id += f"<b><i>User ID:</b></i> <code>{message.reply_to_message.from_user.id}</code>\n"
            file_info = get_file_id(message.reply_to_message)
        else:
            _id += f"<b><i>User ID:</b></i> <code>{message.from_user.id}</code>\n"
            file_info = get_file_id(message)
        if file_info:
            _id += f"<b><i>{file_info.message_type}:</b></i> <code>{file_info.file_id}</code>\n"
        await message.reply_text(_id)
