
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    user_data[message.chat.id] = {"step": 0}  # بداية من الخطوة الأولى
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(" إيداع ", callback_data="deposit")],
        [InlineKeyboardButton(" سحب ", callback_data="withdraw")]
    ])
    message.reply("مرحبا بك في Wakeel Egypt. وكيلك الإلكتروني الأول في مصر. ما الخدمة التي تريدها؟\n\n",
                  reply_markup=keyboard)

@bot.on_callback_query()
def handle_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    data = callback_query.data

    if data == "deposit" or data == "withdraw":
        user_data[chat_id]["transaction_type"] = data
        user_data[chat_id]["step"] = 1  # تحديد أن العميل في خطوة اختيار البرنامج
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(" 1xBet ", callback_data="1xbet")],
            [InlineKeyboardButton(" Melbet ", callback_data="melbet")],
            [InlineKeyboardButton(" Linebet ", callback_data="linebet")]
        ])
        callback_query.message.reply("برجاء اختيار البرنامج :", reply_markup=keyboard)

    elif data in ["1xbet", "melbet", "linebet"]:
        user_data[chat_id]["platform"] = data
        user_data[chat_id]["step"] = 2  # تحديد أن العميل في خطوة إدخال الID
        callback_query.message.reply("أكتب الID الخاص بحسابك (أرقام فقط) .")

    elif data in ["wallet", "instapay"]:
        user_data[chat_id]["payment_method"] = data
        user_data[chat_id]["step"] = 3  # تحديد أن العميل في خطوة إدخال البيانات الإضافية (رقم المحفظة أو عنوان إنستاباي)
        callback_query.message.reply("برجاء إدخال رقم المحفظة المرسل منها/الاستلام أو عنوان إنستاباي المرسل منه/الاستلام:")

    elif data == "back":
        step = user_data[chat_id].get("step", 0)
        if step == 1:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(" إيداع ", callback_data="deposit")],
                [InlineKeyboardButton(" سحب ", callback_data="withdraw")]
            ])
            callback_query.message.reply("ما الخدمة التي تريدها؟", reply_markup=keyboard)
        elif step == 2:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(" 1xBet ", callback_data="1xbet")],
                [InlineKeyboardButton(" Melbet ", callback_data="melbet")],
                [InlineKeyboardButton(" Linebet ", callback_data="linebet")]
            ])
            callback_query.message.reply("برجاء اختيار البرنامج :", reply_markup=keyboard)
        elif step == 3:
            payment_keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(" محفظة إلكترونية ", callback_data="wallet")],
                [InlineKeyboardButton(" إنستاباي ", callback_data="instapay")]
            ])
            callback_query.message.reply("برجاء اختيار طريقة الدفع:", reply_markup=payment_keyboard)
        user_data[chat_id]["step"] -= 1  # العودة خطوة واحدة للخلف

@bot.on_message(filters.text)
def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return

    step = user_data[chat_id]["step"]
    
    if step == 2:  # إدخال الID
        if not message.text.isdigit():
            message.reply("رقم الحساب خطأ. يرجى إدخال ID الحساب كرقم.")
            return
        user_data[chat_id]["id"] = message.text
        user_data[chat_id]["step"] = 3
        
        payment_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(" محفظة إلكترونية ", callback_data="wallet")],
            [InlineKeyboardButton(" إنستاباي ", callback_data="instapay")]
        ])
        message.reply("برجاء اختيار طريقة الدفع :", reply_markup=payment_keyboard)
        
    elif step == 3:  # إدخال البيانات الإضافية (رقم المحفظة أو عنوان إنستاباي)
        user_data[chat_id]["wallet_or_insta"] = message.text
        user_data[chat_id]["step"] = 4  # الانتقال إلى خطوة إدخال المبلغ
        
        message.reply("أدخل المبلغ:")

    elif step == 4:  # إدخال المبلغ
        if not message.text.isdigit():
            message.reply("يرجى إدخال قيمة صحيحة للمبلغ (أرقام فقط) .")
            return
        user_data[chat_id]["amount"] = message.text
        transaction_type = user_data[chat_id]["transaction_type"]
        payment_method = user_data[chat_id]["payment_method"]
        
        if transaction_type == "deposit":
            msg = f"قم بتحويل مبلغ {message.text} على {'رقم المحفظة' if payment_method == 'wallet' else 'عنوان إنستاباي'} \n ****** \nثم أرسل سكرين شوت بالتحويل (صورة فقط حتي يتم إستكمال الطلب) ."
        else:
            msg = f"قم بسحب مبلغ {message.text}  على نقطة السحب بالبرنامج\n ******** \n ثم أرسل سكرين شوت لكود السحب (صورة فقط حتي يتم إستكمال الطلب) ."
        
        message.reply(msg)

        # تحديث خطوة العميل بحيث يصبح إرسال الصورة فقط هو المتاح
        user_data[chat_id]["step"] = 5  # الخطوة التي تسمح بإرسال الصور فقط


@bot.on_message(filters.photo)
def handle_photo(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return

    step = user_data[chat_id]["step"]
    
    # إذا كانت الصورة موجودة، استمر في المعالجة
    if user_data[chat_id].get("transaction_type") == "deposit":
        # إرسال البيانات إلى الأدمن بعد وصول الصورة
        user_info = f"طلب جديد:\nالعملية: {user_data[chat_id]['transaction_type']}\nالبرنامج: {user_data[chat_id]['platform']}\nID الحساب: {user_data[chat_id]['id']}\nطريقة الدفع: {user_data[chat_id]['payment_method']}\nالمبلغ: {user_data[chat_id]['amount']}"
        
        # إضافة رقم المحفظة أو عنوان إنستاباي للإيداع
        if user_data[chat_id]["payment_method"] == "wallet":
            user_info += f"\nرقم المحفظة المرسل منها: {user_data[chat_id]['wallet_or_insta']}"
        elif user_data[chat_id]["payment_method"] == "instapay":
            user_info += f"\nعنوان إنستاباي المرسل منه: {user_data[chat_id]['wallet_or_insta']}"

        # إرسال الصورة للأدمن أيضًا
        bot.send_message(ADMIN_USER_ID, user_info)
        bot.send_photo(ADMIN_USER_ID, message.photo.file_id)

        # إيقاف التفاعل مع العميل بعد إرسال طلبه
        message.reply("تم إرسال طلبك بنجاح. سيتم متابعة المعاملة.")

        # تعيين حالة العميل إلى "تم الإرسال"
        user_data[chat_id]["step"] = 0  # إيقاف إرسال أي رسائل أخرى
    
    # إذا كانت الصورة خاصة بالسحب، يتم إرسال جميع البيانات للأدمن
    elif user_data[chat_id].get("transaction_type") == "withdraw":
        # إرسال البيانات إلى الأدمن بعد وصول الصورة
        user_info = f"طلب سحب جديد:\nالعملية: {user_data[chat_id]['transaction_type']}\nالبرنامج: {user_data[chat_id]['platform']}\nID الحساب: {user_data[chat_id]['id']}\nطريقة الدفع: {user_data[chat_id]['payment_method']}\nالمبلغ: {user_data[chat_id]['amount']}"
        
        # إضافة رقم المحفظة أو عنوان إنستاباي للسحب
        if user_data[chat_id]["payment_method"] == "wallet":
            user_info += f"\nرقم المحفظة للاستلام: {user_data[chat_id]['wallet_or_insta']}"
        elif user_data[chat_id]["payment_method"] == "instapay":
            user_info += f"\nعنوان إنستاباي للاستلام: {user_data[chat_id]['wallet_or_insta']}"

        # إرسال الصورة للأدمن أيضًا
        bot.send_message(ADMIN_USER_ID, user_info)
        bot.send_photo(ADMIN_USER_ID, message.photo.file_id)

        # إيقاف التفاعل مع العميل بعد إرسال طلبه
        message.reply("تم إرسال طلبك بنجاح. سيتم متابعة المعاملة.")

        # تعيين حالة العميل إلى "تم الإرسال"
        user_data[chat_id]["step"] = 0  # إيقاف إرسال أي رسائل أخرى


bot.run()

