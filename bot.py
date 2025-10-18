#!/usr/bin/env python3
"""
💎 JANI LIFE SYSTEM 3.1
Render-ready | Python 3.10
Automated billionaire-style routine reminder bot 💬
"""

import os
import json
import pytz
import logging
import asyncio
from functools import partial
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========== CONFIG ==========
TIMEZONE = "Asia/Karachi"
SUBSCRIBERS_FILE = "subscribers.json"

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ TELEGRAM_BOT_TOKEN not found in environment variables!")

# Logging setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== SCHEDULE ==========
SCHEDULE = {
    "wake_up": ("05:00", "🌅 *Wake up + Hydrate* — 2 glasses of water, no phone for 15 min."),
    "gratitude": ("05:15", "🧘 *Gratitude + Quran / Breathing* — calm focused start."),
    "fajr": ("05:45", "🕌 *Fajr Namaz* — spiritual start."),
    "exercise": ("06:00", "💪 *Exercise (15–30 min)* — walk + light workout."),
    "breakfast": ("06:30", "🍳 *Shower + Healthy breakfast* — energize your day."),
    "english_main": ("07:00", "🗣️ *English Speaking (2.5h)* — mimic, record, and shadow."),
    "tea_journal": ("09:30", "☕ *Tea / Journal / Light phone time* — refresh."),
    "ai_block_1": ("10:00", "⚙️ *AI Work Block #1* — deep learning & building."),
    "short_break": ("11:00", "🌿 *Short break* — stretch & breathe."),
    "ai_block_2": ("11:30", "⚙️ *AI Work Block #2* — execution mode."),
    "dhuhr": ("13:30", "🕌 *Dhuhr Namaz* — recharge spiritually."),
    "lunch_nap": ("13:30", "🍽️ *Lunch + Power Nap* — recharge body & mind."),
    "ai_block_3": ("14:00", "🧠 *AI Work Block #3* — improvement / projects."),
    "family_time": ("15:30", "❤️ *Family / Chill time* — connect with loved ones."),
    "asr": ("16:15", "🕌 *Asr Namaz* — focus reset."),
    "mini_english": ("16:30", "💬 *Mini English Session (30 min)* — daily refresh."),
    "trading_prep": ("17:00", "📊 *Trading Prep* — analyze charts before NY open."),
    "maghrib": ("17:40", "🕌 *Maghrib Namaz* — short break."),
    "trading": ("17:50", "💰 *Trading Session (Main)* — full focus till 8:30 PM."),
    "isha_dinner": ("20:30", "🕌🍽️ *Isha Namaz + Dinner* — peace & gratitude."),
    "friends": ("21:00", "❤️ *Family / Friends time* — relax."),
    "instagram": ("21:45", "📱 *Instagram / Chill (30 min max)* — control leisure."),
    "review": ("22:15", "🧠 *Daily Review + Plan Tomorrow* — journal 3 wins."),
    "reading": ("22:45", "📖 *Reading / Quran / Calm music* — prep for sleep."),
    "sleep": ("23:15", "😴 *Sleep Time* — lights off, phone away."),
}

# ========== HELPERS ==========
def hhmm_to_hm(s):
    h, m = s.split(":")
    return int(h), int(m)

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
        logger.info(f"✅ New subscriber added: {chat_id}")

def remove_subscriber(chat_id):
    subs = load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        save_subscribers(subs)
        logger.info(f"❌ Subscriber removed: {chat_id}")

# ========== COMMAND HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_subscriber(chat_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text="🔥 *Welcome to JANI LIFE SYSTEM!* 🔔\n\nDaily billionaire-style reminders activated.\nUse /stop anytime to pause.",
        parse_mode="Markdown",
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    remove_subscriber(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="Notifications stopped. Send /start to resume.")

# ========== REMINDER ==========
async def send_reminder(application, message):
    subs = load_subscribers()
    for chat_id in subs:
        try:
            await application.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"⚠️ Error sending to {chat_id}: {e}")

# ========== SCHEDULER ==========
def schedule_jobs(application, scheduler):
    tz = pytz.timezone(TIMEZONE)
    for key, (hhmm, msg) in SCHEDULE.items():
        hour, minute = hhmm_to_hm(hhmm)
        trigger = CronTrigger(hour=hour, minute=minute, timezone=tz)

        scheduler.add_job(
            func=lambda: asyncio.run(send_reminder(application, msg)),
            trigger=trigger,
            id=f"job_{key}",
            replace_existing=True,
        )
        logger.info(f"📅 Scheduled {key} at {hhmm} ({TIMEZONE})")

# ========== MAIN ==========
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))

    scheduler = BackgroundScheduler()
    schedule_jobs(app, scheduler)
    scheduler.start()

    logger.info("🚀 JANI LIFE SYSTEM started successfully!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

