#!/usr/bin/env python3
import os
import asyncio
import random, string
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

BOT_TOKEN = os.getenv("BOT_TOKEN", "your-bot-token-here")
API_ID = int(os.getenv("API_ID", "12345"))  # Replace
API_HASH = os.getenv("API_HASH", "your-api-hash")  # Replace

app = Client("vpsfree_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

user_sessions = {}

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply(
        "**Welcome! Free VPS (Docker/LAN) Banaye:**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Create VPS", callback_data="vps_create")]
        ])
    )

@app.on_callback_query(filters.regex("^vps_create$"))
async def vps_create(client, callback: CallbackQuery):
    user_sessions[callback.from_user.id] = {}
    await callback.answer()
    await callback.message.edit(
        "RAM choose kare:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("1GB", callback_data="ram_1")],
            [InlineKeyboardButton("2GB", callback_data="ram_2")],
            [InlineKeyboardButton("4GB", callback_data="ram_4")]
        ])
    )

@app.on_callback_query(filters.regex("^ram_"))
async def ram_choose(client, callback: CallbackQuery):
    ram = callback.data.replace("ram_", "")
    user_sessions[callback.from_user.id]["ram"] = ram
    await callback.answer(f"{ram}GB RAM selected")
    await callback.message.edit(
        "Storage choose kare:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("20GB", callback_data="storage_20")],
            [InlineKeyboardButton("50GB", callback_data="storage_50")]
        ])
    )

@app.on_callback_query(filters.regex("^storage_"))
async def storage_choose(client, callback: CallbackQuery):
    storage = callback.data.replace("storage_", "")
    user_sessions[callback.from_user.id]["storage"] = storage
    uname = "user" + str(random.randint(100,999))
    pasw = ''.join(random.choices(string.ascii_letters+string.digits, k=8))
    user_sessions[callback.from_user.id]["username"] = uname
    user_sessions[callback.from_user.id]["password"] = pasw
    await callback.answer()
    await callback.message.edit(
        "Username/Password auto-generated:\n"
        f"`{uname}` / `{pasw}`\n\nCreate karu VPS?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 VPS Bana", callback_data="vps_run")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
        ])
    )

@app.on_callback_query(filters.regex("^vps_run$"))
async def vps_run(client, callback: CallbackQuery):
    data = user_sessions.get(callback.from_user.id)
    if not data:
        await callback.answer("Session expired.")
        return
    await callback.answer("VPS creation starting...")
    ssh_port = random.randint(2200, 2299)
    # Simulate container creation via shell script (real Docker must be installed)
    run_script = (
        f"docker run -d --name vps_{callback.from_user.id}_{random.randint(1,9999)} "
        f"--memory {data['ram']}g --storage-opt size={data['storage']}g "
        f"-p {ssh_port}:22 linuxserver/openssh-server "
        f"&& echo '{data['username']},{data['password']},{ssh_port}'"
    )
    # Only simulation. Docker CLI integration possible with subprocess for localhost.
    await callback.message.edit(
        f"**VPS Created (demo):**\n"
        f"SSH: `ssh {data['username']}@<your-server-ip> -p {ssh_port}`\n"
        f"Password: `{data['password']}`\n"
        f"RAM: {data['ram']}GB | Storage: {data['storage']}GB",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 New VPS", callback_data="vps_create")]
        ])
    )

@app.on_callback_query(filters.regex("^cancel$"))
async def cancel_cb(client, callback: CallbackQuery):
    await callback.answer("Cancelled.")
    await callback.message.edit("Operation cancelled.")

app.run()
  
