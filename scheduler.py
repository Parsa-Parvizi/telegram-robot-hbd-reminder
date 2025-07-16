from apscheduler.schedulers.background import BackgroundScheduler
from birthday_db import get_tomorrows_birthdays
import asyncio

def setup_scheduler(application):
    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job('cron', hour=21)
    def birthday_job():
        print("Checking birthdays...")
        birthdays = get_tomorrows_birthdays()
        for user_id, name in birthdays:
            asyncio.run(application.bot.send_message(
                chat_id=user_id,
                text=f"🎉 یادت نره! فردا تولد {name} هست!"
            ))

    scheduler.start()
