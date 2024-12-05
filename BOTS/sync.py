import json
import re
from pyrogram import Client, filters
from pyrogram.types import Message


video_pattern = re.compile(r'https?://\S+\.(mkv|mp4)', re.IGNORECASE)
srt_pattern = re.compile(r'https?://\S+\.srt', re.IGNORECASE)

mkv_links = []
srt_links = []

async def collect_links(client, message, links , episode_names):
    global mkv_links, srt_links

    if isinstance(links, list) and any(isinstance(sublist, list) for sublist in links):
        links = [item for sublist in links for item in sublist]

    mkv_found = []
    srt_found = []

    for line in links:
        if isinstance(line, str):
            line = line.strip()
            if video_pattern.search(line):
                mkv_found.append(line)
            elif srt_pattern.search(line):
                srt_found.append(line)

    mkv_links.extend(mkv_found)
    srt_links.extend(srt_found)

    if isinstance(episode_names, list) and isinstance(episode_names[0], list):
        episode_names = [item for sublist in episode_names for item in sublist]

    final = await end_collecting(client, message , episode_names)
    
    return final

async def end_collecting(client, message , names):
    global mkv_links, srt_links

    if not mkv_links or not srt_links:
        await message.reply("اول لینک هارا بفرست")
        return

    if len(names) != len(mkv_links) or len(names) != len(srt_links):
        await message.reply(f"تعداد نام‌ها با تعداد لینک‌ها تطابق ندارد. لطفاً برای هر جفت لینک نام اضافه کنید.\n names:{len(names)}\nmkv:{len(mkv_links)}\nsrt:{len(srt_links)}")
        mkv_links = []
        srt_links = []
        return

    formatted_messages = [
        f"{mkv}\n\n{srt}\n\n{name}"
        for mkv, srt, name in zip(mkv_links, srt_links, names)
    ]
    mkv_links = []
    srt_links = []
    return formatted_messages
