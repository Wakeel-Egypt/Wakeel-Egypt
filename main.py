from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import os

# قراءة متغيرات البيئة
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = 7670571581  # تأكد من تحديثه بمعرف الأدمن الصحيح

# التحقق من أن المتغيرات موجودة
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("تأكد من تعيين API_ID و API_HASH و BOT_TOKEN في متغيرات البيئة")

# تحويل API_ID إلى int
API_ID = int(API_ID)

# إنشاء العميل
bot = Client("payment_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

bot = Client("payment_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# تخزين بيانات المستخدمين
user_data = {}

@bot.on_message(filters.command("start"))
def start(client, message):
    user_data[message.chat.id] = {}
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("إيداع", callback_data="deposit"),
         InlineKeyboardButton("سحب", callback_data="withdraw")]
    ])
    message.reply("مرحبا بك في Wakeel Egypt. وكيلك الإلكتروني الأول في مصر. ما الخدمة التي تريدها؟", reply_markup=keyboard)

@bot.on_callback_query()
def handle_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    
    if data in ["deposit", "withdraw"]:
        user_data[chat_id]["transaction_type"] = data
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1xBet", callback_data="1xbet"),
             InlineKeyboardButton("Melbet", callback_data="melbet"),
             InlineKeyboardButton("Linebet", callback_data="linebet")]
        ])
        callback_query.message.edit("برجاء اختيار البرنامج.", reply_markup=keyboard)
    
    elif data in ["1xbet", "melbet", "linebet"]:
        user_data[chat_id]["platform"] = data
        callback_query.message.edit("أكتب الID الخاص بحسابك.")
    
    elif data in ["wallet", "instapay"]:
        user_data[chat_id]["payment_method"] = data
        transaction_type = user_data[chat_id]["transaction_type"]
        if transaction_type == "deposit":
            callback_query.message.edit("أدخل المبلغ المراد إيداعه.")
        else:
            callback_query.message.edit("أدخل المبلغ المراد سحبه.")

@bot.on_message(filters.text)
def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return
    
    if "platform" not in user_data[chat_id]:
        user_data[chat_id]["platform"] = message.text
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("محفظة إلكترونية", callback_data="wallet"),
             InlineKeyboardButton("إنستاباي", callback_data="instapay")]
        ])
        message.reply("اختر طريقة الدفع.", reply_markup=keyboard)
    
    elif "payment_method" not in user_data[chat_id]:
        user_data[chat_id]["id"] = message.text
        message.reply("برجاء اختيار طريقة الدفع.")
    
    elif "amount" not in user_data[chat_id]:
        user_data[chat_id]["amount"] = message.text
        transaction_type = user_data[chat_id]["transaction_type"]
        payment_method = user_data[chat_id]["payment_method"]
        if transaction_type == "deposit":
            msg = f"قم بتحويل مبلغ {message.text} على {'رقم المحفظة' if payment_method == 'wallet' else 'عنوان إنستاباي'} ****** ثم أرسل سكرين شوت بالتحويل."
        else:
            msg = f"قم بسحب مبلغ {message.text} على {'عنوان السحب' if payment_method == 'wallet' else 'عنوان إنستاباي'} ****** ثم أرسل كود السحب."
        message.reply(msg)
        
        # إرسال البيانات إلى الأدمن
        user_info = f"طلب جديد:\nالعملية: {transaction_type}\nالبرنامج: {user_data[chat_id]['platform']}\nID الحساب: {user_data[chat_id]['id']}\nطريقة الدفع: {payment_method}\nالمبلغ: {message.text}"
        bot.send_message(ADMIN_USER_ID, user_info)

@bot.on_message(filters.photo)
def handle_photo(client, message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id].get("transaction_type") == "deposit":
        message.reply("برجاء الإنتظار .. جارى معالجة طلبك.")

@bot.on_message(filters.text)
def handle_code(client, message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id].get("transaction_type") == "withdraw":
        message.reply("برجاء الإنتظار .. جارى معالجة طلبك.")

bot.run()
