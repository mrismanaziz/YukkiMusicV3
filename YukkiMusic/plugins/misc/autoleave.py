#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.

import asyncio

import config
from YukkiMusic.utils.database import get_client, is_active_chat


async def auto_leave():
    if config.AUTO_LEAVING_ASSISTANT != str(True):
        return
    while not await asyncio.sleep(
            config.AUTO_LEAVE_ASSISTANT_TIME
        ):
        from YukkiMusic.core.userbot import assistants

        for num in assistants:
            client = await get_client(num)
            try:
                async for i in client.iter_dialogs():
                    chat_type = i.chat.type
                    if chat_type in [
                            "supergroup",
                            "group",
                            "channel",
                        ]:
                        chat_id = i.chat.id
                        if chat_id not in [
                            config.LOG_GROUP_ID,
                            -1001268711582,
                            -1001473548283,
                            -1001446229394,
                        ] and not await is_active_chat(chat_id):
                            try:
                                await client.leave_chat(
                                    chat_id
                                )
                            except:
                                continue
            except:
                pass


asyncio.create_task(auto_leave())
