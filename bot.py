import random
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- আপনার তথ্য ---
TOKEN = '8279329120:AAFSTnqycPkU1stcdFwqUVYiQLLyNQLZzDI'
ADMIN_ID = '7134813314'
API_USER = '212313'
API_KEY = 'b564b0ffd61fb5ee89a02dae5fe01cae'

# SMS পাঠানোর ফাংশন
def send_sms(phone, otp):
    # নম্বর থেকে '+' সাইন সরালে ভালো হয়
    phone = phone.replace("+", "")
    message = f"Your Verification Code is: {otp}. Thank you for joining our shop!"
    url = f"https://sendmysms.net/api.php?user={API_USER}&key={API_KEY}&to={phone}&msg={message}"
    try:
        r = requests.get(url)
        return True
    except:
        return False

# ১. /start কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"👋 হ্যালো {user.first_name}!\n"
        "আমাদের অফিসিয়াল ই-কমার্স স্টোরে আপনাকে স্বাগতম।\n\n"
        "কেনাকাটা শুরু করার আগে আপনার অ্যাকাউন্টটি ভেরিফাই করা প্রয়োজন।"
    )
    
    # প্রফেশনাল কন্টাক্ট বাটন (কিবোর্ডে থাকবে)
    contact_btn = [[KeyboardButton(text="📲 Verify Account (Share Number)", request_contact=True)]]
    keyboard = ReplyKeyboardMarkup(contact_btn, resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text(welcome_text, reply_markup=keyboard)

# ২. কন্টাক্ট রিসিভ এবং SMS পাঠানো
async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number
    otp = str(random.randint(112233, 998877))
    
    context.user_data['phone'] = phone
    context.user_data['otp'] = otp
    
    await update.message.reply_text("⏳ আপনার নম্বরে একটি ভেরিফিকেশন কোড পাঠানো হচ্ছে...", reply_markup=ReplyKeyboardRemove())
    
    if send_sms(phone, otp):
        await update.message.reply_text("✅ আপনার ফোনে ৬ ডিজিটের কোড পাঠানো হয়েছে। কোডটি নিচে লিখুন:")
        context.user_data['step'] = 'VERIFYING'
    else:
        await update.message.reply_text("❌ SMS পাঠাতে সমস্যা হয়েছে। দয়া করে অ্যাডমিনের সাথে যোগাযোগ করুন।")

# ৩. OTP চেক এবং মেইন মেনু
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_data = context.user_data

    if user_data.get('step') == 'VERIFYING':
        if text == user_data.get('otp'):
            user_data['verified'] = True
            user_data['step'] = None
            
            # প্রফেশনাল ইনলাইন মেনু (মেসেজের নিচে বাটন)
            keyboard = [
                [InlineKeyboardButton("🛒 Shop Now", callback_data='shop')],
                [InlineKeyboardButton("📦 My Orders", callback_data='orders'), InlineKeyboardButton("📞 Support", callback_data='support')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(f"🎉 অভিনন্দন! আপনার অ্যাকাউন্ট ভেরিফাইড।\nএখন আপনি কেনাকাটা করতে পারেন।", reply_markup=reply_markup)
            
            # অ্যাডমিনকে নোটিফিকেশন
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"📢 নতুন কাস্টমার!\nনাম: {update.effective_user.first_name}\nফোন: {user_data['phone']}")
        else:
            await update.message.reply_text("❌ ভুল কোড! সঠিক কোডটি আবার দিন।")

# ৪. ইনলাইন বাটন হ্যান্ডলার (Shop, Support)
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'shop':
        products = [
            [InlineKeyboardButton("👕 T-Shirt - 500৳", callback_data='buy_tshirt')],
            [InlineKeyboardButton("⌚ Smart Watch - 1500৳", callback_data='buy_watch')],
            [InlineKeyboardButton("⬅️ Back", callback_data='main_menu')]
        ]
        await query.edit_message_text("🛍️ আমাদের সেরা পণ্যসমূহ:\n(পছন্দের পণ্যের ওপর ক্লিক করুন)", reply_markup=InlineKeyboardMarkup(products))

    elif query.data.startswith('buy_'):
        item = query.data.split('_')[1]
        await query.message.reply_text(f"✅ {item} এর অর্ডার রিকোয়েস্ট পাঠানো হয়েছে। আমরা শীঘ্রই যোগাযোগ করব।")
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"🛒 নতুন অর্ডার!\nপণ্য: {item}\nকাস্টমার: {query.from_user.first_name}\nফোন: {context.user_data.get('phone')}")

# রান ফাংশন
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("বট সফলভাবে চালু হয়েছে...")
    app.run_polling()