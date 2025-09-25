import os
import re
import asyncio
import httpx
from datetime import datetime
from fastapi import FastAPI
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import KeyboardButtonUrl

# --- Your Telegram API credentials ---
API_ID = 24878661
API_HASH = "7fd279b83c40a0d4228b89978685638a"
SESSION_STRING = "1BJWap1wBu7KoK4LTХ6xRVv6qIWtz1Yx6gN0TkS1I6BTTvac3SG5cUsn9PQ-TeSIR7vuNsBrcyGcEpHkIhusMh73w_MkCT_7JImSun_yH6RbrG0aAhWGfJEVtYPxmWeInd7H3byE8c78myqjWWL4TEVdZLluhgGB9VMkLdsr5UmybQWeERBTEcNGEORtKMs46MWLm0bRdpGSXTTaLasZSLj9zRitvdKOqmaqTYbF9-cGb0AaZbbp3Yq-nzSM-UD9vGHBwj9vjQbneEKErUht_ZstMUVkfSDYdP9xYIqmoJQJk6fR13JI19hbwtDX6-7-y9b-WVPwhnSvwGV7Tw_peua5LbAdwXW="  # 👈 Put session here

# --- Channel IDs ---
SOURCE_CHANNEL = "@goldmasterclub"
TARGET_CHANNEL = "@forthgoldtrader"

# --- Replacement Settings ---
REPLACE_WITH = "@aimanagementteambot"  # Replace any links/mentions with this


# =============== Helpers ===============
def clean_text(text: str):
    """Replace ANY http/https link or @mention with REPLACE_WITH."""
    if not text:
        return text
    text = re.sub(r"@\w+", REPLACE_WITH, text, flags=re.IGNORECASE)
    text = re.sub(r"https?://[^\s)>\]]+", REPLACE_WITH, text, flags=re.IGNORECASE)
    return text


def get_custom_button():
    """Custom button that always gets added."""
    return [KeyboardButtonUrl(text="💬 Join Our Bot", url="https://t.me/aimanagementteambot")]


def replace_button_links(reply_markup):
    """Replace button links and add custom button row."""
    try:
        if not reply_markup:
            return None
        new_rows = []
        for row in reply_markup.rows:
            new_buttons = []
            for button in row.buttons:
                if hasattr(button, "url") and button.url:
                    new_url = re.sub(r"https?://[^\s)>\]]+", REPLACE_WITH, button.url, flags=re.IGNORECASE)
                    new_buttons.append(KeyboardButtonUrl(text=button.text, url=new_url))
                else:
                    new_buttons.append(button)
            new_rows.append(type(row)(buttons=new_buttons))
        # Add custom button at the end
        new_rows.append(type(new_rows[0])(buttons=get_custom_button()))
        return type(reply_markup)(rows=new_rows)
    except Exception as e:
        print(f"⚠️ Error replacing button links: {e}")
        return reply_markup


# =============== Telethon Client ===============
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def forward_handler(event):
    """Forward new messages from source to target with replacements."""
    try:
        message = event.message
        reply_markup = replace_button_links(message.reply_markup) if message.reply_markup else None
        text_content = clean_text(message.text or message.message or message.raw_text)

        if message.grouped_id:  # Album/media group
            media_group = [message]
            async for m in client.iter_messages(SOURCE_CHANNEL, reverse=True, offset_id=message.id):
                if m.grouped_id == message.grouped_id:
                    media_group.append(m)
                else:
                    break
            media_group = sorted(media_group, key=lambda x: x.id)
            files = [m.media for m in media_group if m.media]
            await client.send_file(TARGET_CHANNEL, files, caption=text_content or "", buttons=reply_markup)

        elif message.media:
            await client.send_file(TARGET_CHANNEL, message.media, caption=text_content or "", buttons=reply_markup)

        elif text_content:
            await client.send_message(TARGET_CHANNEL, text_content, buttons=reply_markup)

        elif reply_markup:
            await client.send_message(TARGET_CHANNEL, "📢", buttons=reply_markup)

        print(f"✅ Forwarded message ID {message.id}")

    except Exception as e:
        print(f"⚠️ Error forwarding message: {e}")


# =============== FastAPI App ===============
app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_bot())
    asyncio.create_task(self_ping_loop())


@app.get("/")
async def root():
    return {"status": "running", "time": datetime.utcnow().isoformat()}


# =============== Bot + Self Ping ===============
async def run_bot():
    await client.start()
    me = await client.get_me()
    print(f"🤖 Logged in as {me.username}")
    await client.run_until_disconnected()


async def self_ping_loop():
    url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
    while True:
        try:
            async with httpx.AsyncClient() as http:
                await http.get(url)
            print(f"🔄 Self-ping {url}")
        except Exception as e:
            print(f"⚠️ Self-ping failed: {e}")
        await asyncio.sleep(300)  # 5 minutes
