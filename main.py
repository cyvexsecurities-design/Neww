import os
import asyncio
from fastapi import FastAPI
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- Credentials ---
API_ID = 24878661
API_HASH = "7fd279b83c40a0d4228b89978685638a"
SESSION_STRING = "1BJWap1wBu7KoK4LTХ6xRVv6qIWtz1Yx6gN0TkS1I6BTTvac3SG5cUsn9PQ-TeSIR7vuNsBrcyGcEpHkIhusMh73w_MkCT_7JImSun_yH6RbrG0aAhWGfJEVtYPxmWeInd7H3byE8c78myqjWWL4TEVdZLluhgGB9VMkLdsr5UmybQWeERBTEcNGEORtKMs46MWLm0bRdpGSXTTaLasZSLj9zRitvdKOqmaqTYbF9-cGb0AaZbbp3Yq-nzSM-UD9vGHBwj9vjQbneEKErUht_ZstMUVkfSDYdP9xYIqmoJQJk6fR13JI19hbwtDX6-7-y9b-WVPwhnSvwGV7Tw_peua5LbAdwXW="

# --- Channels ---
SOURCE_CHANNEL = "@goldmasterclub"
TARGET_CHANNEL = "@forthgoldtrader"

# --- Init ---
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
app = FastAPI()

# --- Forward handler ---
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    try:
        await client.send_message(TARGET_CHANNEL, event.message)
        print(f"✅ Forwarded message ID {event.message.id}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

# --- Start Telethon on startup ---
@app.on_event("startup")
async def startup():
    asyncio.create_task(run_bot())

async def run_bot():
    await client.start()
    me = await client.get_me()
    print(f"🤖 Logged in as {me.username}")
    await client.run_until_disconnected()

# --- Health check ---
@app.get("/")
async def root():
    return {"status": "running"}
