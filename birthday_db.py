import sqlite3
from datetime import date

def init_db():
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS birthdays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        birth_date TEXT
    )''')
    conn.commit()
    conn.close()

def add_birthday(user_id, name, birth_date):
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute("INSERT INTO birthdays (user_id, name, birth_date) VALUES (?, ?, ?)", (user_id, name, birth_date))
    conn.commit()
    conn.close()

def get_birthdays(user_id):
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute("SELECT name, birth_date FROM birthdays WHERE user_id=?", (user_id,))
    results = c.fetchall()
    conn.close()
    return results

def delete_birthday(user_id, name):
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    c.execute("DELETE FROM birthdays WHERE user_id=? AND name=?", (user_id, name))
    conn.commit()
    conn.close()

def get_tomorrows_birthdays():
    conn = sqlite3.connect("birthdays.db")
    c = conn.cursor()
    tomorrow = date.today().replace(year=2000).toordinal() + 1  # Compare by month/day only
    c.execute("SELECT user_id, name FROM birthdays")
    results = c.fetchall()
    conn.close()

    # Find people whose birth_date matches tomorrow
    from datetime import datetime
    final = []
    for user_id, name in results:
        birth = datetime.strptime(name if isinstance(name, str) else name.decode(), "%Y-%m-%d").date()
        if birth.replace(year=2000).toordinal() == tomorrow:
            final.append((user_id, name))
    return final
