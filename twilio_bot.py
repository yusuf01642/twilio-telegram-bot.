from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from twilio.rest import Client

# Bot Token ও Twilio
TELEGRAM_BOT_TOKEN = "7768089054:AAFKzxJ8-Pu3PXyfklL7YaTBNtbn-Hf7Qdg"
twilio_client = None
account_sid = ""
auth_token = ""

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔑 Login", callback_data="login")],
        [InlineKeyboardButton("📱 Buy Number", callback_data="buy_number")],
        [InlineKeyboardButton("✉️ Get SMS", callback_data="get_sms")],
        [InlineKeyboardButton("📁 My Numbers", callback_data="my_numbers")],
        [InlineKeyboardButton("⚡ Upgrade Your Plan", callback_data="upgrade")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅ You have active access!\nPlan: 1 Day\n⏳ Access remaining: Unlimited\n\nUse the menu below to proceed.", reply_markup=reply_markup)

# Button click handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global twilio_client
    query = update.callback_query
    await query.answer()

    if query.data == "login":
        await query.edit_message_text("Please send your `SID|TOKEN` in this format:", parse_mode="Markdown")

    elif query.data == "buy_number":
        if not twilio_client:
            await query.edit_message_text("❌ Please login first.")
            return
        numbers = twilio_client.available_phone_numbers("CA").local.list(limit=1)
        if numbers:
            number = twilio_client.incoming_phone_numbers.create(phone_number=numbers[0].phone_number)
            await query.edit_message_text(f"✅ Number bought successfully: `{number.phone_number}`", parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ No numbers available.")

    elif query.data == "get_sms":
        await query.edit_message_text("✉️ SMS Inbox feature coming soon!")

    elif query.data == "my_numbers":
        if not twilio_client:
            await query.edit_message_text("❌ Please login first.")
            return
        numbers = twilio_client.incoming_phone_numbers.list(limit=5)
        if not numbers:
            await query.edit_message_text("📭 You have no Twilio numbers.")
            return
        msg = "\n".join([f"• `{num.phone_number}`" for num in numbers])
        await query.edit_message_text(f"📁 Your Twilio Numbers:\n{msg}", parse_mode="Markdown")

    elif query.data == "upgrade":
        await query.edit_message_text("⚡ Upgrade plans coming soon.")

# Text message handler (for login)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global account_sid, auth_token, twilio_client
    try:
        text = update.message.text.strip()
        if '|' in text:
            sid, token = text.split('|')
            client = Client(sid, token)
            _ = client.api.accounts(sid).fetch()  # test credentials
            account_sid = sid
            auth_token = token
            twilio_client = client
            await update.message.reply_text("✅ Login successful!")
        else:
            await update.message.reply_text("❌ Invalid format. Please use: SID|TOKEN")
    except Exception as e:
        await update.message.reply_text(f"❌ Login failed: {str(e)}")

# Run the bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("✅ Bot is running...")
    app.run_polling()
