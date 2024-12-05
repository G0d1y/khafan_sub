import re

url_pattern = re.compile(r'https?://[^\s]+')


def handle_message(client , message):
    urls = url_pattern.findall(message.text)
    url_list = []
    if urls:
        for url in urls:
            url_list.append(url)

    return url_list
