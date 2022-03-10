#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import filters
from pyrogram.types import (InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)
from youtubesearchpython.__future__ import VideosSearch

import config
from config import BANNED_USERS
from config.config import OWNER_ID
from strings import get_command, get_string
from YukkiMusic import Telegram, YouTube, app
from YukkiMusic.misc import SUDOERS
from YukkiMusic.plugins.play.playlist import del_plist_msg
from YukkiMusic.plugins.sudo.sudoers import sudoers_list
from YukkiMusic.utils.database import (add_served_chat,
                                       add_served_user, get_assistant,
                                       get_lang, get_userss,
                                       is_on_off,
                                       is_served_private_chat)
from YukkiMusic.utils.decorators.language import language
from YukkiMusic.utils.inline import (help_pannel, private_panel,
                                     start_pannel)


@app.on_message(
    filters.command(get_command("START_COMMAND"))
    & filters.private
    & ~filters.edited
    & ~BANNED_USERS
)
@language
async def start_comm(client, message: Message, _):
    await add_served_user(message.from_user.id)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[:4] == "help":
            keyboard = help_pannel(_)
            return await message.reply_text(
                _["help_1"], reply_markup=keyboard
            )
        if name[:4] == "song":
            return await message.reply_text(_["song_2"])
        if name[:3] == "sta":
            m = await message.reply_text(
                "🔎 Fetching your personal stats.!"
            )
            stats = await get_userss(message.from_user.id)
            tot = len(stats)
            tracks = min(tot, 10)
            if not stats:
                return await m.edit(_["ustats_1"])
            msg = ""
            limit = 0
            results = {}
            for i in stats:
                top_list = stats[i]["spot"]
                results[str(i)] = top_list
                list_arranged = dict(
                    sorted(
                        results.items(),
                        key=lambda item: item[1],
                        reverse=True,
                    )
                )
            if not results:
                return await m.edit(_["ustats_1"])
            tota = 0
            for vidid, count in list_arranged.items():
                tota += count
                if limit > 9:
                    continue
                if limit == 0:
                    thumbnail = await YouTube.thumbnail(vidid, True)
                limit += 1
                details = stats.get(vidid)
                title = (details["title"][:35]).title()
                if vidid == "telegram":
                    msg += f"🔗[Telegram Files and Audios](https://t.me/telegram) ** played {count} times**\n\n"
                else:
                    msg += f"🔗 [{title}](https://www.youtube.com/watch?v={vidid}) ** played {count} times**\n\n"
            msg = _["ustats_2"].format(tot, tota, tracks) + msg
            await message.reply_photo(photo=thumbnail, caption=msg)
            return
        if name[:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(config.LOG):
                sender_id = message.from_user.id
                sender_name = message.from_user.first_name
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} has just started bot to check <code>SUDOLIST</code>\n\n**USER ID:** {sender_id}\n**USER NAME:** {sender_name}",
                )
            return
        if name[:3] == "lyr":
            query = (str(name)).replace("lyrics_", "", 1)
            lyrical = config.lyrical
            if lyrics := lyrical.get(query):
                return await Telegram.send_split_text(message, lyrics)
            else:
                return await message.reply_text(
                    "Failed to get lyrics."
                )
        if name[:3] == "del":
            await del_plist_msg(client=client, message=message, _=_)
        if name[:3] == "inf":
            m = await message.reply_text("🔎 Fetching Info!")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[
                    0
                ]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = f"""
🔍__**Video Track Information**__

❇️ **Title:** `{title}`

⏱ **Duration:** {duration} Mins
👀 **Views:** `{views}`
⏰ **Published Time:** {published}
🎥 **Channel Name:** {channel}
📎 **Channel Link:** [Visit From Here]({channellink})
🔗 **Video Link:** [Link]({link})

⚡️ **Searched Powered By** {config.MUSIC_BOT_NAME}"""
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="• ᴡᴀᴛᴄʜ •", url=f"{link}"
                        ),
                        InlineKeyboardButton(
                            text="• ᴄʟᴏsᴇ •", callback_data="close"
                        ),
                    ],
                ]
            )
            await app.send_photo(
                message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                parse_mode="markdown",
                reply_markup=key,
            )
            if await is_on_off(config.LOG):
                sender_id = message.from_user.id
                sender_name = message.from_user.first_name
                return await app.send_message(
                    config.LOG_GROUP_ID,
                    f"{message.from_user.mention} has just started bot to check <code>VIDEO INFORMATION</code>\n\n**USER ID:** {sender_id}\n**USER NAME:** {sender_name}",
                )
    else:
        try:
            await app.resolve_peer(OWNER_ID[0])
            OWNER = OWNER_ID[0]
        except:
            OWNER = None
        if await is_on_off(config.LOG):
            sender_id = message.from_user.id
            sender_name = message.from_user.first_name
            return await app.send_message(
                config.LOG_GROUP_ID,
                f"{message.from_user.mention} has just started Bot.\n\n**USER ID:** {sender_id}\n**USER NAME:** {sender_name}",
            )


@app.on_message(
    filters.command(get_command("START_COMMAND"))
    & filters.group
    & ~filters.edited
    & ~BANNED_USERS
)
@language
async def testbot(client, message: Message, _):
    out = start_pannel(_)
    return await message.reply_text(
        _["start_1"].format(
            message.chat.title, config.MUSIC_BOT_NAME
        ),
        reply_markup=InlineKeyboardMarkup(out),
    )


welcome_group = 2


@app.on_message(filters.new_chat_members, group=welcome_group)
async def welcome(client, message: Message):
    chat_id = message.chat.id
    if config.PRIVATE_BOT_MODE == str(True):
        if not await is_served_private_chat(message.chat.id):
            await message.reply_text(
                "**Private Music Bot**\n\nOnly for authorized chats from the owner. Ask my owner to allow your chat first."
            )
            return await app.leave_chat(message.chat.id)
    else:
        await add_served_chat(chat_id)
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            if member.id == app.id:
                chat_type = message.chat.type
                if chat_type != "supergroup":
                    await message.reply_text(_["start_6"])
                    return await app.leave_chat(message.chat.id)
                userbot = await get_assistant(message.chat.id)
                out = start_pannel(_)
                await message.reply_text(
                    _["start_3"].format(
                        config.MUSIC_BOT_NAME,
                        userbot.username,
                        userbot.id,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
            if member.id in config.OWNER_ID:
                return await message.reply_text(
                    _["start_4"].format(
                        config.MUSIC_BOT_NAME, member.mention
                    )
                )
            if member.id in SUDOERS:
                return await message.reply_text(
                    _["start_5"].format(
                        config.MUSIC_BOT_NAME, member.mention
                    )
                )
            return
        except:
            return
