#!/usr/bin/env python3
# 💎 JANI LIFE SYSTEM (Render-Stable Edition)
# Works perfectly with python-telegram-bot==13.15

import os
import json
import pytz
import logging
from datetime import datetime
from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# ========== CONFIG ==========
TIMEZONE = "Asia/Karachi"
SUBSCRIBERS_FILE = "subscribers.json"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== SCHEDULE ==========
SCHEDULE = {
    "wake_up": ("05:00", "🌅 *Wake up + Hydrate* — 2 glasses of water, no phone for 15 min."),
    "fajr": ("05:45", "🕌 *Fajr Namaz* — spiritual start."),
    "exercise": ("06:00", "💪 *Exercise (15–30 min)* — walk + light workout."),
    "breakfast": ("06:30", "🍳 *Healthy breakfast* — energize your day."),
    "work": ("10:00", "⚙️ *AI Work Block* — focus deeply."),
    "dhuhr": ("13:30", "🕌 *Dhuhr Namaz* — recharge spiritually."),
    "trading": ("17:30", "💰 *Trading Session* — focus mode."),
    "isha": ("20:30", "🕌 *Isha + Dinner* — peace & gratitude."),
    "sleep": ("23:00", "😴 *Sleep Time* — phone away, lights off."),
}

# ========== HELPERS ==========
def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subs, f)

def add_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id not in subs:
        subs.append(chat_id)
        save_subscribers(subs)
        logger.info(f"✅ New subscriber: {chat_id}")

def remove_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        logger.info(f"❌ Removed subscriber: {chat_id}")

# ========== COMMANDS ==========
def start(update, context):
    chat_id = update.effective_chat.id
    add_subscriber(chat_id)
    update.message.reply_text(
        "🔥 Welcome to *JANI LIFE SYSTEM!* 🔔\n\nDaily billionaire-style reminders activated.\nUse /stop anytime to pause.",
        parse_mode="Markdown"
    )

def stop(update, context):
    chat_id = update.effective_chat.id
    remove_subscriber(chat_id)
    update.message.reply_text("Notifications stopped. Send /start to resume.")

# ========== REMINDER ==========
def send_reminder(bot, message):
    subs = load_subscribers()
    for chat_id in subs:
        try:
            bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"⚠️ Error sending to {chat_id}: {e}")

# ========== SCHEDULER ==========
def schedule_jobs(bot, scheduler):
    tz = pytz.timezone(TIMEZONE)
    for key, (hhmm, msg) in SCHEDULE.items():
        h, m = map(int, hhmm.split(":"))
        trigger = CronTrigger(hour=h, minute=m, timezone=tz)
        scheduler.add_job(send_reminder, trigger, args=[bot, msg], id=f"job_{key}")
        logger.info(f"📅 Scheduled: {key} at {hhmm}")

# ========== MAIN ==========
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    scheduler = BackgroundScheduler()
    schedule_jobs(updater.bot, scheduler)
    scheduler.start()

    logger.info("🚀 JANI LIFE SYSTEM started successfully!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
