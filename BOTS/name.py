import re

def text_handler(client, message):
    user_response = message.text.strip()

    match = re.match(r"^(\d+)\s*@(.+)$", user_response)
    if not match:
        message.reply("لطفاً پیام را به فرمت صحیح وارد کنید:\n<episode_count>\n@<base_name>")
        return

    episode_count = int(match.group(1))
    base_name = match.group(2)

    resolutions = ["360p", "480p", "540p", "720p", "1080p"]

    episode_names = []

    for res in resolutions:
        for i in range(1, episode_count + 1):
            episode_name = f"@{base_name}.E{i:02}.{res}"
            episode_names.append(episode_name)
    
    return episode_names
