from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات یادآور تولد فعاله 🎉")

app = ApplicationBuilder().token("توکن ربات تلگرامت").build()
app.add_handler(CommandHandler("start", start))

app.run_polling()
