import requests
import time
import os
import asyncio
import zipfile
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

DOWNLOAD_DIRECTORY = "./"
cancel_event = asyncio.Event()


proxies = []
proxy_index = 0

def load_proxies():
    """Load proxies from the 'proxy.txt' file and set to the global proxies list."""
    global proxies
    try:
        with open('proxy.txt', 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        print(f"Loaded {len(proxies)} proxies from proxy.txt")
    except FileNotFoundError:
        print("Error: 'proxy.txt' file not found. Please add the file with the list of proxies.")
        proxies = []

load_proxies()


async def download_file(client, url, filename, chat_id, message_id):
    """Download a file using a proxy and switch proxies if speed is low."""
    global proxies, proxy_index
    proxy = proxies[proxy_index]
    proxy_index += 1
    if proxy_index == 100:
        proxy_index = 1


    proxies_dict = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'
    }
    print(f"Using proxy: {proxy}")

    try:
        response = requests.get(url, stream=True, proxies=proxies_dict, timeout=10)
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()
        low_speed_start_time = None  

        if not filename:
            filename = os.path.basename(url)

        with open(filename, 'wb') as f:
            last_update_time = time.time()
            previous_message = ""

            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                downloaded += len(data)
                current_time = time.time()
                elapsed_time = current_time - start_time

                if elapsed_time > 0:
                    speed = (downloaded / (1024 * 1024)) / elapsed_time
                else:
                    speed = 0

                
            if speed < 1:
                if not low_speed_start_time:
                    low_speed_start_time = current_time  
                elif current_time - low_speed_start_time >= 10:
                    if not is_speed_low:
                        
                        await client.edit_message_text(
                            chat_id,
                            message_id,
                            "⏸️ سرعت دانلود پایین است! دانلود ادامه خواهد داشت! 🔄",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("لغو", callback_data=f"cancel:{message_id}")]
                            ])
                        )
                        is_speed_low = True  
                    
                    return await download_file(client, url, filename, chat_id, message_id)

            else:
                low_speed_start_time = None   

                if current_time - last_update_time >= 1:
                    remaining_time = (total_size - downloaded) / (speed * 1024 * 1024) if speed > 0 else float('inf')
                    message_content = (
                        f"دانلود: {downloaded / (1024 * 1024):.2f} MB از {total_size / (1024 * 1024):.2f} MB\n"
                        f"سرعت: {speed:.2f} MB/s\n"
                        f"زمان باقی‌مانده: {remaining_time:.2f} ثانیه\n"
                        f"پراکسی: {proxy} ({proxy_index}/{len(proxies)})"
                    )

                    keyboard = InlineKeyboardMarkup([
                        [InlineKeyboardButton("لغو", callback_data=f"cancel:{message_id}")]
                    ])

                    if message_content != previous_message:
                        await client.edit_message_text(
                            chat_id,
                            message_id,
                            message_content,
                            reply_markup=keyboard
                        )
                        previous_message = message_content
                    last_update_time = current_time

        print(f"Download completed with proxy {proxy}.")
        return filename

    except Exception as e:
        print(f"Error with proxy {proxy}: {e}")
        return None

async def handle_proxy_rotation(client, url, filename, chat_id, message_id):
    global proxies, proxy_index

    if not proxies:
        proxies = load_proxies()

    while True:
        result = await download_file(client, url, filename, chat_id, message_id)

        if result:  
            return result
        else:  
            proxy_index = (proxy_index + 1) % len(proxies)  
            print(f"Switching to proxy {proxy_index + 1}/{len(proxies)}")

async def download_document(client, document, file_name, chat_id, message_id):
    file_path = os.path.join(DOWNLOAD_DIRECTORY, file_name)
    total_size = int(document.file_size) if document.file_size else 0
    downloaded = 0
    start_time = time.time()
    last_update_time = 0  

    async def progress(current, total):
        nonlocal downloaded, last_update_time
        downloaded = current
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        if elapsed_time > 0:
            speed = (downloaded / (1024 * 1024)) / elapsed_time
            remaining_time = (total_size - downloaded) / (speed * 1024 * 1024) if speed > 0 else float('inf')
        else:
            speed = 0
            remaining_time = float('inf')

        
        if current_time - last_update_time >= 2:
            last_update_time = current_time
            message_content = (
                f"دانلود: {downloaded / (1024 * 1024):.2f} MB از {total / (1024 * 1024):.2f} MB\n"
                f"سرعت: {speed:.2f} MB/s\n"
                f"زمان باقی‌مانده: {remaining_time:.2f} ثانیه"
            )
            await client.edit_message_text(
                chat_id,
                message_id,
                message_content,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("لغو", callback_data=f"cancel:{message_id}")]]),
            )

    try:
        await client.download_media(document, file_path, progress=progress)
        return file_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None
