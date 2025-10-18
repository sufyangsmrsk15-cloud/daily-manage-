import os
from telegram import Bot

# --- Load environment variables ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# --- Self-check for safety ---
if not BOT_TOKEN or not CHAT_ID:
    print("⚠️ Missing or invalid environment variables! Check TELEGRAM_BOT_TOKEN and CHAT_ID on Render.")
    exit()
else:
    print("✅ Environment variables loaded successfully!")

bot = Bot(token=BOT_TOKEN)


# --- Your Billionaire Routine Schedule ---
SCHEDULE = [
    ("05:00", "🌅 Wake up + Hydrate — 2 glass paani, no phone 💧"),
    ("05:15", "🕋 Gratitude + Quran recitation — calm focused start 🌙"),
    ("05:45", "🕌 Fajr Namaz — start with peace 🤲"),
    ("06:00", "🏃‍♂️ Exercise (15–30 min) — energy boost 💪"),
    ("06:30", "🥣 Shower + Healthy breakfast 🍳"),
    ("07:00", "🗣 English Speaking Practice (2h 30m) 🎤"),
    ("09:30", "☕ Tea / Journal / Light phone time"),
    ("10:00", "⚙️ AI Work Block #1 — deep creative focus"),
    ("11:30", "⚙️ AI Work Block #2 — execution time"),
    ("13:30", "🕌 Dhuhr Namaz — gratitude & reset 🌤️"),
    ("13:45", "🍱 Lunch + 20 min nap ⚡"),
    ("14:00", "⚙️ AI Work Block #3 — projects & improvement 🧠"),
    ("15:30", "👨‍👩‍👧 Family / chill time ❤️"),
    ("16:15", "🕌 Asr Namaz — mental refresh 🌅"),
    ("16:30", "💬 Mini English Refresh Session (30m)"),
    ("17:00", "📊 Trading prep / chart analysis"),
    ("17:40", "🕌 Maghrib Namaz 🌙"),
    ("17:50", "💰 Main Trading Session (5:50–8:30 PM)"),
    ("20:30", "🕌 Isha Namaz + Dinner 🍽️"),
    ("21:00", "👨‍👩‍👦 Family / Friends time ❤️"),
    ("21:45", "📱 Instagram / Chill (30 min) ⏳"),
    ("22:15", "📔 Daily review + tomorrow plan 🧠"),
    ("22:45", "📖 Quran / light reading / calm music 🎧"),
    ("23:15", "😴 Sleep — recharge for greatness 🌙")
]

async def send_message(message):
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print("Error sending message:", e)

async def scheduler():
    print("✅ JANI LIFE SYSTEM BOT STARTED SUCCESSFULLY!")
    sent_today = set()

    while True:
        now = datetime.now().strftime("%H:%M")
        for time_str, msg in SCHEDULE:
            key = f"{datetime.now().date()}_{time_str}"
            if now == time_str and key not in sent_today:
                await send_message(f"⏰ {time_str} - {msg}")
                sent_today.add(key)

        # Reset for next day at midnight
        if now == "00:00":
            sent_today.clear()

        await asyncio.sleep(30)  # check every 30 seconds

if __name__ == "__main__":
    asyncio.run(scheduler())
