from pyrogram import Client, filters
from .profile import app , user_state
from BOTS.name import text_handler
@app.on_message(filters.text)
async def text_hub(client, message):
    user_id = message.from_user.id
    state = user_state.get(user_id, {}).get("stage")
    if state == "awaiting_name":
        await text_handler(client, message)


app.run()