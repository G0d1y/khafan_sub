import re

def text_handler(client, message):
    user_response = message.text.strip()

    lines = user_response.split("\n")

    if len(lines) < 3:
        print("The input does not have at least 3 lines.")
        return None

    persian_name = lines[2].strip()

    try:
        episode_count = int(lines[0].strip())
    except ValueError:
        print(f"Invalid episode count in the first line: {lines[0]}")
        return None

    match = re.match(r"^@(.+)$", lines[1].strip())
    if not match:
        print(f"Invalid base name format in the second line: {lines[1]}")
        return None

    base_name = match.group(1)

    resolutions = ["360p", "480p", "540p", "720p", "1080p"]

    episode_names = []
    for res in resolutions:
        for i in range(1, episode_count + 1):
            episode_name = f"@{base_name}.E{i:02}.{res}"
            episode_names.append(episode_name)
    
    return episode_names, persian_name, episode_count
