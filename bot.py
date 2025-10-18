#!/usr/bin/env python3
"""
🔥 JANI LIFE SYSTEM 2.1 — Telegram Reminder Bot 🔔
- Send /start to activate daily billionaire routine alerts.
- Works automatically (Asia/Karachi timezone).
- Uses Render environment variables for BOT_TOKEN.
"""

import os
import json
import logging
from datetime import time as dtime
from functools import partial
import pytz

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# -------- CONFIG --------
TIMEZONE = "Asia/Karachi"
SUBSCRIBERS_FILE = "subscribers.json"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("⚠️ BOT_TOKEN missing! Add it in Render Environment Variables.")

# -------- LOGGING --------
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# -------- SCHEDULE --------
SCHEDULE = {
    "wake_up": ("05:00", "🌅 *Wake up + Hydrate* — 2 glasses of water. No phone for 15 min."),
    "fajr": ("05:45", "🕌 *Fajr Namaz* — spiritual start."),
    "exercise": ("06:00", "💪 *Exercise (15–30 min)* — light walk & stretch."),
    "english": ("07:00", "🗣️ *English Speaking (2h)* — shadowing, mimic, practice."),
    "ai_work_1": ("10:00", "⚙️ *AI Work Block #1* — deep focus creative tasks."),
    "dhuhr": ("13:30", "🕌 *Dhuhr Namaz* — gratitude reset."),
    "ai_work_2": ("14:00", "🧠 *AI Work Block #2* — project build time."),
    "asr": ("16:15", "🕌 *Asr Namaz* — calm reset."),
    "trading_prep": ("17:00", "📊 *Trading Prep* — setup & analysis."),
    "maghrib": ("17:40", "🕌 *Maghrib Namaz* — short break."),
    "trading_main": ("17:50", "💰 *Trading Session (5:50–8:30 PM)* — full focus."),
    "isha_dinner": ("20:30", "🕌🍽️ *Isha + Dinner* — peace time."),
    "family": ("21:00", "❤️ *Family / Friends time* — recharge & connect."),
    "instagram": ("21:45", "📱 *Instagram / Chill (30 min)* — controlled leisure."),
    "review": ("22:15", "🧠 *Daily Review* — 3 wins & plan tomorrow."),
    "reading": ("22:45", "📖 *Reading / Quran / Calm music* — relax mind."),
    "sleep": ("23:15", "😴 *Sleep* — lights off, no phone."),
}

# -------- STORAGE --------
def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r") as f:
        try:
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
        logger.info(f"✅ Added subscriber: {chat_id}")

def remove_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        logger.info(f"🗑️ Removed subscriber: {chat_id}")

# -------- TELEGRAM HANDLERS --------
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    add_subscriber(chat_id)
    msg = (
        "🔥 *JANI LIFE SYSTEM ACTIVATED!*\n\n"
        "You’ll now get daily billionaire routine alerts in Karachi timezone.\n"
        "Use /stop to unsubscribe anytime."
    )
    context.bot.send_message(chat_id=chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)

def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    remove_subscriber(chat_id)
    context.bot.send_message(chat_id=chat_id, text="❌ Notifications stopped. Send /start to re-enable.")

def help_cmd(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Use /start to register for daily alerts, /stop to unsubscribe.")

# -------- JOB ACTION --------
def send_reminder(bot, key, message):
    subs = load_subscribers()
    if not subs:
        logger.info("No subscribers to send to.")
        return
    for chat_id in subs:
        try:
            bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")

# -------- SCHEDULER --------
def schedule_jobs(updater: Updater, scheduler: BackgroundScheduler):
    tz = pytz.timezone(TIMEZONE)
    bot = updater.bot
    for key, (hhmm, msg) in SCHEDULE.items():
        hour, minute = map(int, hhmm.split(":"))
        trigger = CronTrigger(hour=hour, minute=minute, timezone=tz)
        scheduler.add_job(partial(send_reminder, bot, key, msg), trigger=trigger, id=f"job_{key}", replace_existing=True)
        logger.info(f"🕐 Scheduled: {key} at {hhmm} {TIMEZONE}")

# -------- MAIN --------
def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("help", help_cmd))

    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    schedule_jobs(updater, scheduler)
    scheduler.start()
    logger.info("✅ Scheduler started.")

    updater.start_polling()
    logger.info("🤖 Bot running... /start to activate.")
    updater.idle()

if __name__ == "__main__":
    main()

