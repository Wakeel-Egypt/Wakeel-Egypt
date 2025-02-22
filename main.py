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
        [InlineKeyboardButton("💰 إيداع (نقل الأموال إلى حسابك)", callback_data="deposit")],
        [InlineKeyboardButton("💸 سحب (سحب الأموال إلى حسابك)", callback_data="withdraw")]
    ])
    message.reply("مرحبا بك في Wakeel Egypt. وكيلك الإلكتروني الأول في مصر. ما الخدمة التي تريدها؟\n\n"
                  "*يرجى اختيار إحدى الخيارات:*",
                  reply_markup=keyboard)

@bot.on_callback_query()
def handle_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data
    
    if data == "deposit" or data == "withdraw":
        user_data[chat_id]["transaction_type"] = data
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎲 1xBet", callback_data="1xbet")],
            [InlineKeyboardButton("🏆 Melbet", callback_data="melbet")],
            [InlineKeyboardButton("💻 Linebet", callback_data="linebet")]
        ])
        callback_query.message.edit("برجاء اختيار البرنامج:", reply_markup=keyboard)
    
    elif data in ["1xbet", "melbet", "linebet"]:
        user_data[chat_id]["platform"] = data
        callback_query.message.edit("أكتب الID الخاص بحسابك.")

    elif data in ["wallet", "instapay"]:
        user_data[chat_id]["payment_method"] = data
        transaction_type = user_data[chat_id]["transaction_type"]
        if transaction_type == "deposit":
            callback_query.message.edit("أكتب المبلغ المراد إيداعه.")
        else:
            callback_query.message.edit("أكتب المبلغ المراد سحبه.")

@bot.on_message(filters.text)
def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return

    # المرحلة الأولى - اختيار البرنامج
    if "platform" not in user_data[chat_id]:
        user_data[chat_id]["platform"] = message.text
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 محفظة إلكترونية", callback_data="wallet")],
            [InlineKeyboardButton("💵 إنستاباي", callback_data="instapay")]
        ])
        message.reply("برجاء اختيار طريقة الدفع:", reply_markup=keyboard)

    # المرحلة الثانية - اختيار طريقة الدفع
    elif "payment_method" not in user_data[chat_id]:
        user_data[chat_id]["id"] = message.text
        message.reply("برجاء اختيار طريقة الدفع.")
    
    # المرحلة الثالثة - إدخال المبلغ
    elif "amount" not in user_data[chat_id]:
        # التحقق من أن المدخل هو رقم فقط
        if not message.text.isdigit():
            message.reply("يرجى إدخال مبلغ صحيح (رقم فقط).")
            return
        user_data[chat_id]["amount"] = message.text
        transaction_type = user_data[chat_id]["transaction_type"]
        payment_method = user_data[chat_id]["payment_method"]
        
        # تحديد الرسالة حسب نوع العملية وطريقة الدفع
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
        message.reply("برجاء الإنتظار .. جاري معالجة طلبك.")

@bot.on_message(filters.text)
def handle_code(client, message):
    chat_id = message.chat.id
    if chat_id in user_data and user_data[chat_id].get("transaction_type") == "withdraw":
        message.reply("برجاء الإنتظار .. جاري معالجة طلبك.")

bot.run()
