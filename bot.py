import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters,
    ConversationHandler, CallbackContext
)
from birthday_db import init_db, add_birthday, get_birthdays, delete_birthday
from scheduler import setup_scheduler
from datetime import datetime

init_db()

TOKEN = os.getenv("BOT_TOKEN")
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# وضعیت‌های گفتگو
NAME, DATE = range(2)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! با دستور /add می‌تونی تولد کسی رو وارد کنی. 🎂")

def list_birthdays(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    entries = get_birthdays(user_id)
    if not entries:
        update.message.reply_text("🎂 لیست تولدها خالیه.")
    else:
        text = "\n".join([f"{name} — {birth}" for name, birth in entries])
        update.message.reply_text("📋 لیست تولدها:\n" + text)

def delete_entry(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if len(context.args) == 0:
        update.message.reply_text("اسم مخاطبی که می‌خوای حذف کنی رو بعد از /delete بنویس.")
        return
    name = " ".join(context.args)
    delete_birthday(user_id, name)
    update.message.reply_text(f"✅ تولد {name} حذف شد.")

# افزودن تولد (Conversation)
def add_start(update: Update, context: CallbackContext):
    update.message.reply_text("👤 اسم مخاطب رو بفرست:")
    return NAME

def get_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text
    update.message.reply_text("📅 تاریخ تولد رو بفرست (مثلاً 1402-01-15 یا 2023-04-04):")
    return DATE

def get_date(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    name = context.user_data["name"]
    birth_date = update.message.text

    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
        add_birthday(user_id, name, birth_date)

        # ارسال پیام موفقیت با دکمه لیست
        keyboard = [[KeyboardButton("/list")]]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text(
            f"✅ تولد {name} با موفقیت ثبت شد!",
            reply_markup=markup
        )
    except:
        update.message.reply_text("❌ فرمت تاریخ اشتباهه. لطفاً به صورت YYYY-MM-DD وارد کن.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("لغو شد.")
    return ConversationHandler.END

# هندلرها
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("list", list_birthdays))
dispatcher.add_handler(CommandHandler("delete", delete_entry))

add_conv = ConversationHandler(
    entry_points=[CommandHandler("add", add_start)],
    states={
        NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
        DATE: [MessageHandler(Filters.text & ~Filters.command, get_date)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
dispatcher.add_handler(add_conv)

# راه‌اندازی نوتیفیکیشن تولدها
setup_scheduler(updater)

# اجرای ربات
updater.start_polling()
updater.idle()
