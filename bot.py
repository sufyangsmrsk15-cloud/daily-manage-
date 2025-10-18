#!/usr/bin/env python3
import os
import json
import pytz
import logging
from datetime import time as dtime
from functools import partial
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- Config ---
TIMEZONE = "Asia/Karachi"
SUBSCRIBERS_FILE = "subscribers.json"
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN not found in environment variables!")

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JANI_BOT")

# --- Schedule ---
SCHEDULE = {
    "wake_up": ("05:00", "🌅 *Wake up + Hydrate* — 2 glasses of water. No phone for first 15 min."),
    "gratitude": ("05:15", "🧘 *Gratitude + Quran / Breathing* — calm, focused start."),
    "fajr": ("05:45", "🕌 *Fajr Namaz* — spiritual start."),
    "exercise": ("06:00", "💪 *Exercise (15–30 min)* — walk + light workout."),
    "english_main": ("07:00", "🗣️ *English Practice (Main session — 2.5h)* — mimic, record, shadowing."),
    "ai_block": ("10:00", "⚙️ *AI Work Block #1* — creative focus."),
    "trading_start": ("17:50", "💰 *Trading Session (Main)* — 5:50 PM to 8:30 PM, full focus."),
    "sleep_time": ("23:15", "😴 *Sleep time* — phone away, lights off.")
}

def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subs, f)

def add_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id not in subs:
        subs.append(chat_id)
        save_subscribers(subs)
        logger.info(f"Added subscriber: {chat_id}")

def remove_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        logger.info(f"Removed subscriber: {chat_id}")

# --- Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_subscriber(chat_id)
    await update.message.reply_text(
        "🔥 *JANI LIFE SYSTEM reminders activated!*\n\n"
        "You’ll now receive daily alerts in Karachi timezone.\n"
        "Use /stop anytime to pause alerts.",
        parse_mode=ParseMode.MARKDOWN,
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    remove_subscriber(chat_id)
    await update.message.reply_text("Notifications stopped. Use /start to resume.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Commands:\n/start – Subscribe\n/stop – Unsubscribe")

# --- Reminder ---
async def send_reminder(app, msg):
    subs = load_subscribers()
    if not subs:
        return
    for chat_id in subs:
        try:
            await app.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Failed to send to {chat_id}: {e}")

# --- Scheduler ---
async def setup_scheduler(app):
    tz = pytz.timezone(TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=tz)
    for key, (hhmm, msg) in SCHEDULE.items():
        hour, minute = map(int, hhmm.split(":"))
        scheduler.add_job(
            partial(send_reminder, app, msg),
            CronTrigger(hour=hour, minute=minute, timezone=tz),
            id=f"job_{key}",
            replace_existing=True,
        )
        logger.info(f"📅 Scheduled: {key} at {hhmm}")
    scheduler.start()
    logger.info("✅ Scheduler started successfully.")

# --- Main ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("help", help_cmd))
    await setup_scheduler(app)
    logger.info("🚀 Bot running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

