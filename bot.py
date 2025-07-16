import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from birthday_db import init_db, add_birthday, get_birthdays, delete_birthday
from scheduler import setup_scheduler

init_db()

TOKEN = os.getenv("BOT_TOKEN")
app = ApplicationBuilder().token(TOKEN).build()

# Conversation states
NAME, DATE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! با دستور /add می‌تونی تولد کسی رو وارد کنی. 📅")

async def list_birthdays(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    entries = get_birthdays(user_id)
    if not entries:
        await update.message.reply_text("🎂 لیست تولدها خالیه.")
    else:
        text = "\n".join([f"{name} — {birth}" for name, birth in entries])
        await update.message.reply_text("📋 لیست تولدها:\n" + text)

async def delete_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if len(context.args) == 0:
        await update.message.reply_text("اسم مخاطبی که می‌خوای حذف کنی رو بعد از دستور /delete بنویس.")
        return
    name = " ".join(context.args)
    delete_birthday(user_id, name)
    await update.message.reply_text(f"✅ تولد {name} حذف شد.")

# Add birthday (Conversation)
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 اسم مخاطب رو بفرست:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📅 تاریخ تولد رو بفرست (مثلاً 1402-01-15 یا 2023-04-04):")
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    birth_date = update.message.text
    try:
        # تست فرمت تاریخ
        from datetime import datetime
        datetime.strptime(birth_date, "%Y-%m-%d")
        add_birthday(update.effective_user.id, name, birth_date)
        await update.message.reply_text(f"✅ تولد {name} با موفقیت ذخیره شد.")
    except:
        await update.message.reply_text("❌ فرمت تاریخ اشتباهه. لطفاً به صورت YYYY-MM-DD وارد کن.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد.")
    return ConversationHandler.END

# دستورات
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("list", list_birthdays))
app.add_handler(CommandHandler("delete", delete_entry))

# مکالمه افزودن تولد
add_conv = ConversationHandler(
    entry_points=[CommandHandler("add", add_start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
app.add_handler(add_conv)

# فعال‌سازی زمان‌بندی نوتیفیکیشن
setup_scheduler(app)

# اجرای ربات
app.run_polling()
