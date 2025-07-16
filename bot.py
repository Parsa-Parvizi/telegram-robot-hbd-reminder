from datetime import datetime, timedelta

def send_birthday_reminders():
    tomorrow = datetime.now().date() + timedelta(days=1)
    birthdays = get_birthdays_for_date(tomorrow)
    for b in birthdays:
        send_telegram_message(b.user.telegram_id, f"فردا تولد {b.friend_name} هست! 🎉")
