import random
import requests
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Flask Web Server (Render-এ বট জ্যান্ত রাখার জন্য) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is Running!"

def run_web():
    app_web.run(host='0.0.0.0', port=8080)

# --- আপনার বটের তথ্য ---
TOKEN = '8279329120:AAFSTnqycPkU1stcdFwqUVYiQLLyNQLZzDI'
ADMIN_ID = '7134813314'
API_USER = '212313'
API_KEY = 'b564b0ffd61fb5ee89a02dae5fe01cae'

# SMS পাঠানোর ফাংশন
def send_sms(phone, otp):
    phone = phone.replace("+", "")
    message = f"Your Verification Code is: {otp}"
    url = f"https://sendmysms.net/api.php?user={API_USER}&key={API_KEY}&to={phone}&msg={message}"
    try:
        requests.get(url)
        return True
    except:
        return False

# কমান্ড হ্যান্ডলারগুলো (Start, Contact, Message, etc.)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_btn = [[KeyboardButton(text="📲 Verify Account (Share Number)", request_contact=True)]]
    keyboard = ReplyKeyboardMarkup(contact_btn, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(f"👋 হ্যালো {update.effective_user.first_name}!\nকেনাকাটা করতে একাউন্ট ভেরিফাই করুন।", reply_markup=keyboard)

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.contact.phone_number
    otp = str(random.randint(112233, 998877))
    context.user_data['phone'] = phone
    context.user_data['otp'] = otp
    if send_sms(phone, otp):
        await update.message.reply_text("✅ কোড পাঠানো হয়েছে। কোডটি লিখুন:", reply_markup=ReplyKeyboardRemove())
        context.user_data['step'] = 'VERIFYING'

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('step') == 'VERIFYING':
        if update.message.text == context.user_data.get('otp'):
            context.user_data['verified'] = True
            await update.message.reply_text("🎉 ভেরিফাইড! কেনাকাটা করতে /shop লিখুন।")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"নতুন কাস্টমার: {context.user_data['phone']}")

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('verified'):
        await update.message.reply_text("🛍️ পণ্য দেখতে বাটন শীঘ্রই যোগ করা হবে।")
    else:
        await update.message.reply_text("আগে ভেরিফাই করুন।")

# মেইন ফাংশন
if __name__ == '__main__':
    # ওয়েব সার্ভার আলাদা থ্রেডে চালানো
    t = threading.Thread(target=run_web)
    t.start()
    
    # টেলিগ্রাম বট চালানো
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("shop", shop))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    print("বট এবং সার্ভার চালু হয়েছে...")
    app.run_polling()
