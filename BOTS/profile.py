import json
from pyrogram import Client, filters

with open('config.json') as config_file:
    config = json.load(config_file)

api_id = int(config['api_id'])
api_hash = config['api_hash']
bot_token = config['bot_token']

user_state = {}

app = Client(
    "sub",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

persian_ordinals = [
    "اول", "دوم", "سوم", "چهارم", "پنجم", "ششم", "هفتم", "هشتم", "نهم", "دهم",
    "یازدهم", "دوازدهم", "سیزدهم", "چهاردهم", "پانزدهم", "شانزدهم", "هفدهم", 
    "هجدهم", "نوزدهم", "بیستم", "بیست و یکم", "بیست و دوم", "بیست و سوم", 
    "بیست و چهارم", "بیست و پنجم", "بیست و ششم", "بیست و هفتم", "بیست و هشتم", 
    "بیست و نهم", "سی‌ام", "سی و یکم", "سی و دوم", "سی و سوم", "سی و چهارم",
]

def get_caption(series_name, episode_ordinal, last_part, quality):
    caption = (
        f"🎬 {series_name}\n"
        f"🐈 قسمت {episode_ordinal}{last_part}\n"
        f"زیرنویس چسبیده بدون سانسور🍷\n"
        f"کیفیت : {quality}✨\n"
        f"🫰🏻| @RiRiKdrama | ❤️"
    )

    return caption