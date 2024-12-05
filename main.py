from pyrogram import Client, filters
from BOTS.profile import app, user_state
from BOTS.name import text_handler
from BOTS.link import handle_message
from BOTS.sync import collect_links
from BOTS.sub import video_queue, handle_output_name
from pyrogram.types import ReplyKeyboardMarkup
import BOTS.downloader
import BOTS.ffmpeg
import os
import json
import time
from pyrogram import Client, filters
from urllib.parse import urlparse
import subprocess
import signal

user_session_index = {}

def find_and_kill_bot():
    try:
        pid = int(subprocess.check_output(["pgrep", "-f", "main.py"]))
        
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped bot with PID {pid}")
        
        time.sleep(2)
    except subprocess.CalledProcessError:
        print("Bot is not running.")

def start_bot():
    subprocess.Popen(["nohup", "python3", "main.py", "&"])
    print("Bot restarted.")

@app.on_message(filters.command("test"))
def toggle_test(client, message):
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

    config['test'] = not config['test']

    with open('config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

    new_value = "enabled" if config['test'] else "disabled"
    client.send_message(message.chat.id, f"Test mode has been {new_value}.")

@app.on_message(filters.command("restart"))
def restart(client, message):
    find_and_kill_bot()
    start_bot()
    client.send_message(message.chat.id, "Bot restarted.")

@app.on_message(filters.text & filters.regex("🟢 شروع"))
async def handle_button(client, message):
    user_id = message.from_user.id
    session_index = user_session_index.get(user_id, 0) + 1  
    user_session_index[user_id] = session_index  

    session_key = f"{user_id}_{session_index}"  
    user_state[session_key] = {"stage": "awaiting_name"}

    await message.reply(
        "لطفاً پیام را به فرمت صحیح وارد کنید:"
    )

@app.on_message(filters.text & filters.regex("🔴 پایان"))
async def handle_button2(client, message):
    user_id = message.from_user.id
    session_index = user_session_index.get(user_id, 0)  

    session_key = f"{user_id}_{session_index}"  
    links = user_state[session_key]["LINKS"]
    episode_names = user_state[session_key]["EP_List"]
    final = await collect_links(client, message, links, episode_names)
    for task in final:
        lines = [line.strip() for line in task.split("\n") if line.strip()]
        if len(lines) == 3:
            video_link = lines[0]
            subtitle_link = lines[1]
            output_name = lines[2]
            persian_name = user_state[session_key]["fa_name"]
            episode_count = user_state[session_key]["ep_count"]
            cover = str(session_index) + ".jpg"
            if video_link and subtitle_link and output_name:
                video_queue.put((video_link, subtitle_link, output_name, client, message.chat.id, persian_name, episode_count, cover))

    if not video_queue.empty():
        await client.send_message(message.chat.id, "لینک‌ها دریافت شد. در حال پردازش...")

    del user_state[session_key]

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    keyboard = ReplyKeyboardMarkup(
        [
            ["🟢 شروع"],
            ["🔴 پایان"]
        ],
        resize_keyboard=True
    )
    user_id = message.from_user.id
    session_index = user_session_index.get(user_id, 0) + 1
    user_session_index[user_id] = session_index
    session_key = f"{user_id}_{session_index}"

    user_state[session_key] = {"stage": "awaiting_name"}

    await message.reply(
        "لطفاً پیام را به فرمت صحیح وارد کنید:",
        reply_markup=keyboard
    )

@app.on_message(filters.photo & filters.private)
async def handle_cover(client, message):
    try:
        user_id = message.from_user.id
        session_index = user_session_index.get(user_id, 0)
        session_key = f"{user_id}_{session_index}"
        state = user_state.get(session_key, {}).get("stage")
        if state == "awaiting_cover":
            session_key = f"{user_id}_{session_index}"
            cover_image_path = str(session_index) + ".jpg"
            
            if os.path.exists(cover_image_path):
                os.remove(cover_image_path)
            
            downloaded_file_path = await message.download()
            os.rename(downloaded_file_path, cover_image_path)
            
            await message.reply("عکس کاور دریافت شد...")
            await message.reply("لطفا لینک ها را ارسال کنید")
            user_state[session_key]["stage"] = "awaiting_collect_links"
    except Exception as e:
        await message.reply(f"Error handling cover image: {str(e)}")

@app.on_message(filters.text)
async def text_hub(client, message):
    user_id = message.from_user.id
    session_index = user_session_index.get(user_id, 0)
    session_key = f"{user_id}_{session_index}"
    cover_path = str(session_index) + ".jpg"
    state = user_state.get(session_key, {}).get("stage")
    if state == "awaiting_name":
        episode_names, persian_name, episode_count = text_handler(client, message)
        user_state[session_key] = {"stage": "awaiting_cover", "EP_List": [], "LINKS": [], "fa_name": persian_name, "ep_count": episode_count , "cover_path": cover_path}
        user_state[session_key]["EP_List"].append(episode_names)
        await message.reply("لطفا کاور را ارسال کنید.")
    elif state == "awaiting_collect_links":
        links = handle_message(client, message)
        user_state[session_key]["LINKS"].append(links)
    elif state == "awaiting_file_name":
        await handle_output_name(client, message)

app.run()
