from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# تعيين متغيرات البوت
API_ID = "20267178"
API_HASH = "5d0d025e0b607f4f51d76e764846040f"
BOT_TOKEN = "8155646143:AAGK22ulfCKrlRDqCFwk2h5mS76gKCgIK5c"
ADMIN_USER_ID = 7670571581  # تم تحديث ID الأدمن

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
    message.reply("#مرحبا بك في Wakeel Egypt. وكيلك الإلكتروني الأول في مصر. ما الخدمة التي تريدها؟", reply_markup=keyboard)

@bot.on_callback_query()
def handle_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    
    if data == "deposit" or data == "withdraw":
        user_data[chat_id]["transaction_type"] = data
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1xBet", callback_data="1xbet"),
             InlineKeyboardButton("Melbet", callback_data="melbet"),
             InlineKeyboardButton("Linebet", callback_data="linebet")]
        ])
        bot.send_message(chat_id, "#برجاء إختيار البرنامج.", reply_markup=keyboard)

    elif data in ["1xbet", "melbet", "linebet"]:
        user_data[chat_id]["platform"] = data
        bot.send_message(chat_id, "#@أكتب الID الخاص بحسابك.")

    elif data == "deposit":
        bot.send_message(chat_id, "#اختر طريقة الدفع.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("محفظة إلكترونية", callback_data="wallet"),
             InlineKeyboardButton("إنستاباي", callback_data="instapay")]
        ]))

    elif data == "withdraw":
        bot.send_message(chat_id, "#اختر طريقة الاستلام.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("محفظة إلكترونية", callback_data="wallet"),
             InlineKeyboardButton("إنستاباي", callback_data="instapay")]
        ]))

@bot.on_message(filters.text)
def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return

    # التحقق من المدخلات المسموح بها (أرقام فقط)
    def validate_numeric_input(input_text, error_message):
        if not input_text.isdigit():
            message.reply(error_message)
            return False
        return True

    if "platform" not in user_data[chat_id]:
        user_data[chat_id]["platform"] = message.text
        bot.send_message(chat_id, "#@أكتب الID الخاص بحسابك.")

    elif "id" not in user_data[chat_id]:
        user_data[chat_id]["id"] = message.text
        if not validate_numeric_input(message.text, "رقم الحساب خطأ"):
            return
        bot.send_message(chat_id, "#اختر طريقة الدفع.", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("محفظة إلكترونية", callback_data="wallet"),
             InlineKeyboardButton("إنستاباي", callback_data="instapay")]
        ]))

    elif "payment_method" not in user_data[chat_id]:
        user_data[chat_id]["payment_method"] = message.text
        if message.text == "محفظة إلكترونية":
            bot.send_message(chat_id, "#@أكتب المبلغ المراد إيداعه.")
        elif message.text == "إنستاباي":
            bot.send_message(chat_id, "#@أكتب المبلغ المراد إيداعه.")

    elif "amount" not in user_data[chat_id]:
        if not validate_numeric_input(message.text, "المبلغ خطأ"):
            return
        user_data[chat_id]["amount"] = message.text
        if user_data[chat_id]["payment_method"] == "محفظة إلكترونية":
            bot.send_message(chat_id, "#% قم بتحويل المبلغ المطلوب علي رقم ......ثم أرسل سكرين شوت بالتحويل.")
        else:
            bot.send_message(chat_id, "#% قم بتحويل المبلغ المطلوب علي عنوان دفع إنستاباي .....ثم أرسل سكرين شوت بالتحويل.")

    elif "wallet_id" not in user_data[chat_id]:
        if not validate_numeric_input(message.text, "رقم المحفظة خطأ"):
            return
        user_data[chat_id]["wallet_id"] = message.text
        bot.send_message(chat_id, "#% أدخل كود السحب من البرنامج.")

    elif "withdraw_code" not in user_data[chat_id]:
        user_data[chat_id]["withdraw_code"] = message.text
        bot.send_message(chat_id, "#برجاء الإنتظار .. جاري معالجه طلبك.")

@bot.on_message(filters.photo)
def handle_photo(client, message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id].get("transaction_type") == "deposit":
        message.reply("#برجاء الإنتظار .. جاري معالجه طلبك.")

bot.run()
