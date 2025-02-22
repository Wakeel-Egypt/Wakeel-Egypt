
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
        [InlineKeyboardButton(" سحب ", callback_data="withdraw")],
        [InlineKeyboardButton(" تنزيل البرامج برابط مباشر ", callback_data="download_apps")]
    ])
    message.reply("مرحبا بك في Wakeel Egypt. وكيلك الإلكتروني الأول في مصر. ما الخدمة التي تريدها ؟\n\n",
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

    elif data == "download_apps":
        # إضافة أزرار البرامج التي يمكن تنزيلها
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("1xBet", url="https://affpa.top/L?tag=d_3405078m_70865c_&site=3405078&ad=70865")],
            [InlineKeyboardButton("Melbet", url="https://refpakrtsb.top/L?tag=d_3405089m_18775c_&site=3405089&ad=18775")],
            [InlineKeyboardButton("Linebet", url="https://lb-aff.com/L?tag=d_3405121m_66803c_&site=3405121&ad=66803")],
            [InlineKeyboardButton("888StarZ", url="https://app.appsflyer.com/org.starz888.client-Custom?pid=FromSite&c=d_4058907m_45159c_&tag=d_4058907m_45159c_&af_r=https%3A%2F%2Fwww.bkre23.c")],
            [InlineKeyboardButton("Megapari", url="https://refpaiozdg.top/L?tag=d_4029361m_54987c_&site=4029361&ad=54987")]
        ])
        callback_query.message.reply("إختر البرنامج الذي تريد تنزيله :", reply_markup=keyboard)

    # التعامل مع باقي البيانات الخاصة بالعمليات المالية
    elif data in ["1xbet", "melbet", "linebet"]:
        user_data[chat_id]["platform"] = data
        user_data[chat_id]["step"] = 2  # تحديد أن العميل في خطوة إدخال الID
        callback_query.message.reply("أكتب الID الخاص بحسابك ( أرقام فقط ) .")

    elif data in ["wallet", "instapay"]:
        user_data[chat_id]["payment_method"] = data
        user_data[chat_id]["step"] = 3  # تحديد أن العميل في خطوة إدخال البيانات الإضافية (رقم المحفظة أو عنوان إنستاباي)
        
        # تحديد الرسالة المناسبة بناءً على نوع العملية وطريقة الدفع
        transaction_type = user_data[chat_id]["transaction_type"]
        if transaction_type == "deposit":
            if data == "wallet":
                callback_query.message.reply("برجاء إدخال رقم المحفظة المرسل منها :")
            elif data == "instapay":
                callback_query.message.reply("برجاء إدخال عنوان إنستاباي المحول منه :")
        elif transaction_type == "withdraw":
            if data == "wallet":
                callback_query.message.reply("برجاء إدخال رقم المحفظة المحول إليها :")
            elif data == "instapay":
                callback_query.message.reply("برجاء إدخال عنوان إنستاباي المحول إليه :")

@bot.on_message(filters.text)
def handle_text(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return

    step = user_data[chat_id]["step"]
    
    if step == 2:  # إدخال الID
        if not message.text.isdigit():
            message.reply("رقم الحساب خطأ. يرجى إدخال ID الحساب كرقم .")
            return
        user_data[chat_id]["id"] = message.text
        user_data[chat_id]["step"] = 3
        
        payment_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(" محفظة إلكترونية ", callback_data="wallet")],
            [InlineKeyboardButton(" إنستاباي ", callback_data="instapay")]
        ])
        message.reply("برجاء اختيار طريقة الدفع :", reply_markup=payment_keyboard)
        
    elif step == 3:  # إدخال البيانات الإضافية (رقم المحفظة أو عنوان إنستاباي)
        payment_method = user_data[chat_id]["payment_method"]
        entered_value = message.text

        # التحقق من صحة المدخلات
        if payment_method == "wallet":  # المحفظة الإلكترونية
            if not entered_value.isdigit():
                message.reply("خطأ : رقم المحفظة يجب أن يحتوي على أرقام فقط .")
                return
        elif payment_method == "instapay":  # إنستاباي
            if not entered_value.isalnum():
                message.reply("خطأ: عنوان إنستاباي يجب أن يحتوي على حروف أو أرقام فقط ( لا يمكن إدخال صور ) .")
                return
        
        user_data[chat_id]["wallet_or_insta"] = entered_value
        user_data[chat_id]["step"] = 4  # الانتقال إلى خطوة إدخال المبلغ
        
        message.reply("أدخل المبلغ :")

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
            user_info += f"\nعنوان إنستاباي المحول منه: {user_data[chat_id]['wallet_or_insta']}"

        # إرسال الصورة للأدمن أيضًا
        bot.send_message(ADMIN_USER_ID, user_info)
        bot.send_photo(ADMIN_USER_ID, message.photo.file_id)

        # إضافة الزر في الرسالة بعد إرسال البيانات
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("طلب سحب/إيداع جديد", callback_data="new_request")]
        ])
        message.reply("تم إرسال طلبك بنجاح. سيتم متابعة المعاملة.", reply_markup=keyboard)

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

        # إضافة الزر في الرسالة بعد إرسال البيانات
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("طلب سحب/إيداع جديد", callback_data="new_request")]
        ])
        message.reply("تم إرسال طلبك بنجاح. سيتم متابعة المعاملة.", reply_markup=keyboard)

        # تعيين حالة العميل إلى "تم الإرسال"
        user_data[chat_id]["step"] = 0  # إيقاف إرسال أي رسائل أخرى


# التعامل مع الزر عند الضغط عليه
@bot.on_callback_query(filters.regex("new_request"))
def new_request(client, callback_query):
    chat_id = callback_query.message.chat.id
    # هنا نقوم بإعادة الأمر /start عند الضغط على الزر
    start(client, callback_query.message)

bot.run()


