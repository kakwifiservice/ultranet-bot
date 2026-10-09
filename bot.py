# -*- coding: utf-8 -*-

import os
import re

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# BOT TOKEN
# =========================================================

TOKEN = os.getenv("BOT_TOKEN", "").strip()

BOT_NAME = "Ultra Net KAK WiFi Internet Service Provider"


# =========================================================
# CUSTOMER SUPPORT
# =========================================================

SUPPORT_TEXT = """📞 Customer Support

📞 Phone — 09-777719577
📱 Telegram — @UltraNetKAKWiFi
📢 Channel — https://t.me/ultranetkak
👥 Support Group — https://t.me/+30B6ITGkrfg5YTA1
📱 Viber — 09-777719577

☎️ လိုင်းခွဲများ

1️⃣ Call Center / Customer Service
2️⃣ Billing / Cash
3️⃣ လိုင်းသစ်တပ်ဆင်လိုသူများ
4️⃣ KPay / WavePay ကိစ္စများ

⏰ Support Time
မနက် 9:00 AM – 12:00 PM
"""


# =========================================================
# SOCIAL MEDIA
# =========================================================

SOCIAL_TEXT = """📱 Social Media မှ ဆက်သွယ်မေးမြန်းရန်

ဆက်သွယ်မေးမြန်းလိုပါက
အောက်ပါ Social Media များမှ
ဆက်သွယ်မေးမြန်းနိုင်ပါတယ်ခင်ဗျာ။ 🙏

🔵 Facebook
Ko Aye Ko
Ultranet Internet Service

🎵 TikTok
https://tiktok.com/@ultranet.ko.aye.ko

📱 Telegram
@UltraNetKAKWiFi

⚠️ Facebook Link ကို နောက်ပိုင်းတွင်
ထပ်မံထည့်သွင်းပေးနိုင်ပါတယ်။
"""


# =========================================================
# OFFICE LOCATION
# =========================================================

LOCATION_TEXT = """📍 ရုံးတည်နေရာ / Location

🏢 Ultra Net KAK ရုံး

ဓိဌာန်အောင် ဘုရားလမ်း၊
အမှတ်(၄)ရပ်ကွက်၊
မြဝတီမြို့။

🙏 ရုံးသို့ လူကိုယ်တိုင်လာရောက်
ဆက်သွယ်မေးမြန်းနိုင်ပါတယ်ခင်ဗျာ။
"""


# =========================================================
# PAYMENT
# =========================================================

PAYMENT_TEXT = """💰 Payment ပြုလုပ်ပြီးပါက

KPay / Wave Money ဖြင့် ငွေလွှဲပြီးနောက်

🧾 ငွေလွှဲထားသော Screenshot နှင့်
🆔 မိမိဆောင်မည့်စက်၏ ID နံပါတ်ကို ပို့ပေးပါ။

ဥပမာ — KAKMWD-0000000

⚠️ KAKMWD-0000000 သည် နမူနာသာဖြစ်ပါသည်။
မိမိ၏ စက် ID အမှန်ကိုသာ ပို့ပေးပါ။

📱 Viber: 09-796000066
👤 Viber Name: KAK Internet pay

💵 Cash ဖြင့်ပေးချေလိုပါက
ရုံးသို့ လူကိုယ်တိုင်လာရောက်၍
ငွေပေးချေနိုင်ပါသည်။
"""


# =========================================================
# CABLE FEE
# =========================================================

CABLE_TEXT = """🔌 Cable Fee

• 250m အထိ — အခမဲ့
• 250m ကျော်ပါက — 1m = 1,000 Ks
• အကွာအဝေးကို ရုံး/အထိုင်ပုံးမှ
  Customer အိမ်အထိ တိုင်းတာပါမယ်။

ဥပမာ — 280m ဖြစ်ပါက

250m အခမဲ့
+
30m × 1,000 Ks
= 30,000 Ks ထပ်ဆောင်း ပေးရမည် ဖြစ်သည်။
"""


# =========================================================
# INSTALLATION TIME
# =========================================================

INSTALL_TEXT = """📅 တပ်ဆင်ချိန်

📝 ဒီနေ့ စာရင်းတင်ပြီးပါက
မနက်ဖြန် Survey ဆင်းစစ်ဆေးပေးပါမယ်။

📅 Survey ပြီးနောက် ၃ ရက်အတွင်း
တပ်ဆင်ပေးပါမယ်။
"""


# =========================================================
# PACKAGES
# =========================================================

PACKAGES = {
    "15": ("Home", "15 Mbps", 150000, 40000, 190000),
    "25": ("Home", "25 Mbps", 150000, 50000, 200000),
    "35": ("Home", "35 Mbps", 150000, 80000, 230000),
    "50": ("Business", "50 Mbps", 150000, 150000, 300000),
    "70": ("Business", "70 Mbps", 150000, 250000, 400000),
}


# =========================================================
# MAIN MENU
# =========================================================

def menu():
    return ReplyKeyboardMarkup(
        [
            ["📦 Package / Price", "🛠 Internet Problem"],
            ["💰 Payment", "📞 Customer Support"],
            ["🆔 Customer ID စစ်မယ်", "👤 လူနဲ့ဆက်သွယ်မယ်"],
            ["📍 ရုံးတည်နေရာ / Location", "📱 Social Media"],
            ["📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း"],
        ],
        resize_keyboard=True,
    )


# =========================================================
# COMPLAINT MENU
# =========================================================

def complaint_menu():
    return ReplyKeyboardMarkup(
        [
            ["🔧 Internet လုံးဝမရ"],
            ["🔴 LOS မီးနီ"],
            ["🐌 Internet နှေး"],
            ["🔌 Internet ခဏခဏပြတ်"],
            ["📶 WiFi ပြဿနာ"],
            ["⚡ Router / ONU ပြဿနာ"],
            ["📱 Device တစ်လုံးတည်း မရ"],
            ["🌐 Website / App တစ်ခုတည်း မရ"],
            ["🔙 Main Menu"],
        ],
        resize_keyboard=True,
    )


# =========================================================
# YES / NO MENU
# =========================================================

def yes_no_menu():
    return ReplyKeyboardMarkup(
        [
            ["🟢 ဟုတ်ပါတယ်", "🔴 မဟုတ်ပါဘူး"],
            ["❓ မသိပါဘူး"],
            ["🔙 Main Menu"],
        ],
        resize_keyboard=True,
    )


# =========================================================
# INSTALLATION PACKAGE MENU
# =========================================================

def installation_package_menu():
    return ReplyKeyboardMarkup(
        [
            ["15 Mbps", "25 Mbps"],
            ["35 Mbps", "50 Mbps"],
            ["70 Mbps"],
            ["🔙 Main Menu"],
        ],
        resize_keyboard=True,
    )


# =========================================================
# INSTALLATION CONFIRM MENU
# =========================================================

def installation_confirm_menu():
    return ReplyKeyboardMarkup(
        [
            ["✅ အတည်ပြုမယ်"],
            ["🔄 ပြန်ပြင်မယ်"],
            ["🔙 Main Menu"],
        ],
        resize_keyboard=True,
    )


# =========================================================
# TEXT NORMALIZER
# =========================================================

def normalize(text):
    return re.sub(r"\s+", "", text.lower().strip())


# =========================================================
# SAFE REPLY
# =========================================================

async def send_reply(message, text, update, reply_markup=None):

    chat = update.effective_chat

    if chat and chat.type == "channel":
        await message.reply_text(text)
        return

    if reply_markup is None:
        reply_markup = menu()

    await message.reply_text(
        text,
        reply_markup=reply_markup,
    )


# =========================================================
# RESET FLOW
# =========================================================

def reset_flow(context):

    keys = [
        "flow",
        "subflow",
        "device_type",
        "install_name",
        "install_phone",
        "install_address",
        "install_package",
        "install_note",
    ]

    for key in keys:
        context.user_data.pop(key, None)


# =========================================================
# PACKAGE DETAIL
# =========================================================

def package_text(speed):

    kind, speed_text, device, first_month, total = PACKAGES[speed]

    return f"""🏠 {speed_text} {kind} Package

🔹 စက်တန်ဖိုး — {device:,} Ks
🔹 ပထမလ လစဉ်ကြေး — {first_month:,} Ks
🔹 စတင်တပ်ဆင်ခ — {total:,} Ks

{CABLE_TEXT}

{INSTALL_TEXT}
"""


# =========================================================
# CUSTOMER ID START
# =========================================================

async def start_customer_id_flow(message, update, context):

    context.user_data["flow"] = "customer_id"

    await send_reply(
        message,
        """🆔 Customer ID စစ်ဆေးခြင်း

မိမိ၏ စက် ID ကို ပို့ပေးပါခင်ဗျာ။

မှန်ကန်တဲ့ပုံစံမှာ —

KAKMWD- + ဂဏန်း 7 လုံး

ဥပမာ —
KAKMWD-1234567

⚠️ အပေါ်က ID သည် နမူနာသာဖြစ်ပါတယ်။
မိမိ၏ စက် ID အမှန်ကိုသာ ပို့ပေးပါ။

မသိပါက
📞 Customer Support ကို ဆက်သွယ်နိုင်ပါတယ်။
""",
        update,
        ReplyKeyboardMarkup(
            [["🔙 Main Menu"]],
            resize_keyboard=True,
        ),
    )


# =========================================================
# CUSTOMER ID CHECK
# =========================================================

async def handle_customer_id_flow(
    message,
    update,
    context,
    raw,
):

    customer_id = raw.upper().strip()

    if re.fullmatch(r"KAKMWD-\d{7}", customer_id):

        reset_flow(context)

        await send_reply(
            message,
            f"""✅ Customer ID Format မှန်ပါတယ်။

🆔 Customer ID
{customer_id}

လက်ရှိအဆင့်မှာ ID Format ကိုသာ
စစ်ဆေးပေးနိုင်ပါတယ်ခင်ဗျာ။

နောက်ပိုင်းမှာ Customer ID နဲ့
Customer Information ကိုပါ
စစ်ဆေးနိုင်အောင် Database ချိတ်ဆက်ပေးနိုင်ပါတယ်။
""",
            update,
            menu(),
        )
        return

    await send_reply(
        message,
        """❌ Customer ID Format မမှန်သေးပါဘူး။

မှန်ကန်တဲ့ပုံစံက —

KAKMWD- + ဂဏန်း 7 လုံး

ဥပမာ —
KAKMWD-1234567

⚠️ ဥပမာ ID ကို မပို့ပါနဲ့။
မိမိ၏ စက် ID အမှန်ကိုသာ ပို့ပေးပါ။

ထပ်မံပို့ပေးပါခင်ဗျာ။
""",
        update,
        ReplyKeyboardMarkup(
            [["🔙 Main Menu"]],
            resize_keyboard=True,
        ),
    )


# =========================================================
# NEW INSTALLATION START
# =========================================================

async def start_installation_flow(message, update, context):

    reset_flow(context)

    context.user_data["flow"] = "install_name"

    await send_reply(
        message,
        """📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း

အဆင့် (1/5)

👤 မိမိ၏ အမည်ကို
ပို့ပေးပါခင်ဗျာ။
""",
        update,
        ReplyKeyboardMarkup(
            [["🔙 Main Menu"]],
            resize_keyboard=True,
        ),
    )


# =========================================================
# INSTALLATION SUMMARY
# =========================================================

def installation_summary(context):

    return f"""📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်း

အောက်ပါအချက်အလက်များ မှန်/မမှန်
စစ်ဆေးပေးပါခင်ဗျာ။

👤 အမည်
{context.user_data.get("install_name", "-")}

📞 ဖုန်းနံပါတ်
{context.user_data.get("install_phone", "-")}

📍 တပ်ဆင်မည့်နေရာ
{context.user_data.get("install_address", "-")}

📦 Package
{context.user_data.get("install_package", "-")}

📝 အခြားမှတ်ချက်
{context.user_data.get("install_note", "-")}

------------------------------

📅 တပ်ဆင်ချိန်
ဒီနေ့ စာရင်းပေးပြီးပါက
မနက်ဖြန် Survey ဆင်းစစ်ဆေးပေးပါမယ်။

Survey ပြီးနောက် ၃ ရက်အတွင်း
တပ်ဆင်ပေးပါမယ်။

🔌 Cable Fee
250m အထိ — အခမဲ့
250m ကျော်ပါက — 1m = 1,000 Ks

အကွာအဝေးကို Customer ကိုယ်တိုင်
တိုင်းတာရန် မလိုပါ။
Survey ဆင်းစစ်ဆေးသည့်အချိန်
ဝန်ထမ်းဘက်မှ တိုင်းတာပေးပါမယ်။

------------------------------

အားလုံးမှန်ကန်ပါက
✅ အတည်ပြုမယ် ကို နှိပ်ပါ။

အချက်အလက်တစ်ခုခု ပြန်ပြင်လိုပါက
🔄 ပြန်ပြင်မယ် ကို နှိပ်ပါ။
"""


# =========================================================
# INSTALLATION FLOW HANDLER
# =========================================================

async def handle_installation_flow(
    message,
    update,
    context,
    raw,
):

    flow = context.user_data.get("flow")

    # -----------------------------------------------------
    # NAME
    # -----------------------------------------------------

    if flow == "install_name":

        if len(raw.strip()) < 2:

            await send_reply(
                message,
                """❌ အမည်ကို မှန်ကန်စွာ
ပြန်ပို့ပေးပါခင်ဗျာ။
""",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["install_name"] = raw.strip()
        context.user_data["flow"] = "install_phone"

        await send_reply(
            message,
            """✅ အမည် ရရှိပါပြီ။

အဆင့် (2/5)

📞 ဆက်သွယ်ရန် ဖုန်းနံပါတ်ကို
ပို့ပေးပါခင်ဗျာ။

ဥပမာ —
09xxxxxxxxx
""",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # PHONE
    # -----------------------------------------------------

    if flow == "install_phone":

        phone = raw.strip().replace(" ", "").replace("-", "")

        if not re.fullmatch(r"(09\d{7,9}|\+959\d{7,9})", phone):

            await send_reply(
                message,
                """❌ ဖုန်းနံပါတ်ပုံစံ မမှန်သေးပါဘူး။

ဥပမာ —
09xxxxxxxxx

ပြန်ပို့ပေးပါခင်ဗျာ။
""",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["install_phone"] = phone
        context.user_data["flow"] = "install_address"

        await send_reply(
            message,
            """✅ ဖုန်းနံပါတ် ရရှိပါပြီ။

အဆင့် (3/5)

📍 တပ်ဆင်လိုသော နေရာ၏
လိပ်စာကို ပို့ပေးပါခင်ဗျာ။

ဥပမာ —
အမှတ်(၁)ရပ်ကွက်၊
မြဝတီမြို့။
""",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # ADDRESS
    # -----------------------------------------------------

    if flow == "install_address":

        if len(raw.strip()) < 3:

            await send_reply(
                message,
                """❌ တပ်ဆင်မည့်နေရာ လိပ်စာကို
ပြန်ပို့ပေးပါခင်ဗျာ။
""",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["install_address"] = raw.strip()
        context.user_data["flow"] = "install_package"

        await send_reply(
            message,
            """✅ တပ်ဆင်မည့်နေရာ ရရှိပါပြီ။

အဆင့် (4/5)

📦 မိမိတပ်ဆင်လိုသော Package ကို
ရွေးချယ်ပေးပါခင်ဗျာ။
""",
            update,
            installation_package_menu(),
        )
        return

    # -----------------------------------------------------
    # PACKAGE
    # -----------------------------------------------------

    if flow == "install_package":

        speed = None

        for key in PACKAGES:

            if f"{key}mbps" in normalize(raw):

                speed = key
                break

        if speed is None:

            await send_reply(
                message,
                """❌ Package ရွေးချယ်မှု မမှန်သေးပါဘူး။

အောက်ပါ Package များထဲမှ
တစ်ခုကို ရွေးချယ်ပေးပါခင်ဗျာ။
""",
                update,
                installation_package_menu(),
            )
            return

        kind, speed_text, device, first_month, total = PACKAGES[speed]

        context.user_data["install_package"] = (
            f"{speed_text} {kind} — "
            f"{total:,} Ks Initial Installation"
        )

        context.user_data["flow"] = "install_note"

        await send_reply(
            message,
            f"""✅ {speed_text} {kind} ကို ရွေးချယ်ပြီးပါပြီ။

အဆင့် (5/5)

📝 အခြားမှတ်ချက်ရှိပါက
ပို့ပေးပါခင်ဗျာ။

ဥပမာ —
အိမ်ရှေ့ဘက်ကနေ ကြိုးသွယ်ပေးပါ။

မှတ်ချက်မရှိပါက
“မရှိပါ” လို့ ပို့ပေးနိုင်ပါတယ်။
""",
            update,
            ReplyKeyboardMarkup(
                [["မရှိပါ"], ["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # NOTE
    # -----------------------------------------------------

    if flow == "install_note":

        if raw.strip():

            context.user_data["install_note"] = raw.strip()

        else:

            context.user_data["install_note"] = "မရှိပါ"

        context.user_data["flow"] = "install_confirm"

        await send_reply(
            message,
            installation_summary(context),
            update,
            installation_confirm_menu(),
        )
        return

    # -----------------------------------------------------
    # CONFIRM
    # -----------------------------------------------------

    if flow == "install_confirm":

        if raw == "✅ အတည်ပြုမယ်":

            summary = installation_summary(context)

            reset_flow(context)

            await send_reply(
                message,
                f"""✅ လိုင်းသစ်တပ်ဆင်ရန်
စာရင်းပေးသွင်းမှုကို အတည်ပြုပြီးပါပြီ။

{summary}

🙏 ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။

📞 Customer Support
09-777719577

ဒီစာရင်းကို Support Team မှ
ဆက်လက်စစ်ဆေးဆောင်ရွက်ပေးပါမယ်။
""",
                update,
                menu(),
            )
            return

        if raw == "🔄 ပြန်ပြင်မယ်":

            await start_installation_flow(
                message,
                update,
                context,
            )
            return

        await send_reply(
            message,
            """အောက်ပါခလုတ်များထဲမှ
တစ်ခုကို ရွေးချယ်ပေးပါခင်ဗျာ။
""",
            update,
            installation_confirm_menu(),
        )
        return


# =========================================================
# INTERNET PROBLEM MENU
# =========================================================

async def show_complaint_menu(message, update):

    await send_reply(
        message,
        """🔧 Internet / WiFi ပြဿနာ

အောက်ပါထဲမှ မိမိကြုံတွေ့နေရသော
ပြဿနာကို ရွေးချယ်ပေးပါခင်ဗျာ။ 🙏
""",
        update,
        complaint_menu(),
    )


# =========================================================
# /START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    reset_flow(context)

    message = update.effective_message

    if not message:
        return

    start_text = f"""မင်္ဂလာပါခင်ဗျာ။ 🙏

{BOT_NAME} မှ ကြိုဆိုပါတယ်။

အောက်က Menu ကနေ ရွေးချယ်နိုင်ပါတယ်။
"""

    await send_reply(
        message,
        start_text,
        update,
        menu(),
    )


# =========================================================
# INTERNET START
# =========================================================

async def start_internet_flow(message, update, context):

    context.user_data["flow"] = "internet_start"

    await send_reply(
        message,
        """မင်္ဂလာပါခင်ဗျာ။ 🙏

Internet ပြဿနာကို ကူညီစစ်ဆေးပေးပါမယ်။

အရင်ဆုံး ONU/Router မှာ
🔴 LOS မီးနီနေပါသလား?

🔴 LOS မီးနီနေပါတယ်
🟢 LOS မီးမနီပါဘူး
❓ မသိပါဘူး
""",
        update,
        yes_no_menu(),
    )


# =========================================================
# LOS FLOW
# =========================================================

async def start_los_flow(message, update, context):

    context.user_data["flow"] = "los"

    await send_reply(
        message,
        """🔴 LOS မီးနီနေပါက
Fiber Signal ပြဿနာ ဖြစ်နိုင်ပါတယ်။

အရင်ဆုံး Fiber ကြိုးမှာ—

• ကွေးလွန်းခြင်း
• ဖိမိခြင်း
• ဆွဲမိခြင်း
• ပျက်စီးခြင်း

ရှိ/မရှိ စစ်ပေးပါခင်ဗျာ။

⚠️ Fiber Connector ကို
မိမိဘာသာ ဖြုတ်တပ်ခြင်း မပြုလုပ်သေးပါနဲ့။

LOS မီး အခုထိ နီနေသေးပါသလား?

🔴 နီနေဆဲ
🟢 ပြန်ပျောက်သွားပြီ
""",
        update,
        ReplyKeyboardMarkup(
            [
                ["🔴 နီနေဆဲ", "🟢 ပြန်ပျောက်သွားပြီ"],
                ["❓ မသိပါဘူး"],
                ["🔙 Main Menu"],
            ],
            resize_keyboard=True,
        ),
    )


# =========================================================
# SPEED FLOW
# =========================================================

async def start_speed_flow(message, update, context):

    context.user_data["flow"] = "speed"

    await send_reply(
        message,
        """🐌 နားလည်ပါတယ်ခင်ဗျာ။ 🙏

Internet Speed နှေးနေတဲ့အခြေအနေကို
တစ်ဆင့်ချင်း ကူညီစစ်ဆေးပေးပါမယ်။

ဘယ်လိုအခြေအနေမှာ ဖြစ်နေလဲ?

1️⃣ Device အားလုံးမှာ နှေးပါတယ်
2️⃣ Device တစ်လုံးတည်းမှာ နှေးပါတယ်
3️⃣ ညဘက်မှာ ပိုနှေးပါတယ်
4️⃣ အချိန်တိုင်း နှေးပါတယ်
5️⃣ App / Website တစ်ခုမှာပဲ နှေးပါတယ်
""",
        update,
        ReplyKeyboardMarkup(
            [
                ["1️⃣ အားလုံးနှေး"],
                ["2️⃣ တစ်လုံးတည်းနှေး"],
                ["3️⃣ ညဘက်ပိုနှေး"],
                ["4️⃣ အချိန်တိုင်းနှေး"],
                ["5️⃣ App တစ်ခုတည်းနှေး"],
                ["🔙 Main Menu"],
            ],
            resize_keyboard=True,
        ),
    )


# =========================================================
# DISCONNECT FLOW
# =========================================================

async def start_disconnect_flow(message, update, context):

    context.user_data["flow"] = "disconnect"

    await send_reply(
        message,
        """🔌 Internet ခဏခဏပြတ်နေတဲ့အခြေအနေကို
ကူညီစစ်ဆေးပေးပါမယ်ခင်ဗျာ။ 🙏

လိုင်းပြတ်သွားတဲ့အချိန်
🔴 LOS မီးနီလာပါသလား?

🔴 ဟုတ်ပါတယ်
🟢 မဟုတ်ပါဘူး
❓ မသိပါဘူး
""",
        update,
        yes_no_menu(),
    )


# =========================================================
# WIFI FLOW
# =========================================================

async def start_wifi_flow(message, update, context):

    context.user_data["flow"] = "wifi"

    await send_reply(
        message,
        """📶 WiFi ပြဿနာကို ကူညီစစ်ဆေးပေးပါမယ်ခင်ဗျာ။ 🙏

WiFi Name (SSID) ကို
ဖုန်းမှာ တွေ့ရပါသလား?

🟢 တွေ့ပါတယ်
🔴 မတွေ့ပါဘူး
❓ မသိပါဘူး
""",
        update,
        yes_no_menu(),
    )


# =========================================================
# ROUTER FLOW
# =========================================================

async def start_router_flow(message, update, context):

    context.user_data["flow"] = "router"

    await send_reply(
        message,
        """⚡ Router / ONU ပြဿနာကို
ကူညီစစ်ဆေးပေးပါမယ်ခင်ဗျာ။ 🙏

အရင်ဆုံး Power မီး
လင်းနေပါသလား?

🟢 လင်းပါတယ်
🔴 မလင်းပါဘူး
❓ မသိပါဘူး
""",
        update,
        yes_no_menu(),
    )


# =========================================================
# SINGLE DEVICE FLOW
# =========================================================

async def start_single_device_flow(message, update, context):

    context.user_data["flow"] = "single_device"

    await send_reply(
        message,
        """📱 Device တစ်လုံးတည်းမှာ Internet မရတာဆိုရင်
အဲဒီ Device ဘက်က ပြဿနာဖြစ်နိုင်ပါတယ်။

အရင်ဆုံး—

1️⃣ WiFi ကို Disconnect လုပ်ပါ။
2️⃣ WiFi ကို ပြန် Connect လုပ်ပါ။
3️⃣ Internet ပြန်ရ/မရ စမ်းကြည့်ပါ။

📱 ဘယ် Device မှာ ဖြစ်နေတာလဲ?

📱 Phone
💻 Laptop / Computer
📺 TV
❓ မသိပါဘူး
""",
        update,
        ReplyKeyboardMarkup(
            [
                ["📱 Phone"],
                ["💻 Laptop / Computer"],
                ["📺 TV"],
                ["❓ မသိပါဘူး"],
                ["🔙 Main Menu"],
            ],
            resize_keyboard=True,
        ),
    )


# =========================================================
# APP / WEBSITE FLOW
# =========================================================

async def start_app_flow(message, update, context):

    context.user_data["flow"] = "app"

    await send_reply(
        message,
        """🌐 Website / App တစ်ခုတည်းမှာသာ
ပြဿနာဖြစ်နေပါက Internet လိုင်းတစ်ခုလုံး
ပြဿနာဖြစ်နေခြင်း မဟုတ်နိုင်ပါ။

အရင်ဆုံး အခြား Website / App တစ်ခုကို
ဖွင့်ကြည့်ပေးပါခင်ဗျာ။

🟢 အခြား App တွေ ရပါတယ်
🔴 အခြား App တွေလည်း မရပါဘူး
""",
        update,
        yes_no_menu(),
    )


# =========================================================
# INTERNET FLOW HANDLER
# =========================================================

async def handle_internet_flow(message, update, context, text):

    flow = context.user_data.get("flow")

    if flow == "internet_start":

        if "မသိ" in text:

            context.user_data["flow"] = "unknown_los"

            await send_reply(
                message,
                """မသိပါကလည်း ရပါတယ်ခင်ဗျာ။ 🙏

ONU / Router မှာရှိတဲ့ မီးတွေကို
အောက်ပါအတိုင်း ကြည့်ပေးပါ—

🟢 Power — မီးလင်း/မလင်း
🟢 PON — ပုံမှန်လင်း/မလင်း
🔴 LOS — မီးနီ/မနီ

မလုပ်တတ်ပါကလည်း
📞 Customer Support ကို ဆက်သွယ်နိုင်ပါတယ်။
""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["🔴 LOS နီနေပါတယ်"],
                        ["🟢 LOS မနီပါဘူး"],
                        ["❓ မသိပါဘူး"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        if "နီ" in text or "red" in text:
            await start_los_flow(message, update, context)
            return

        context.user_data["flow"] = "all_or_one"

        await send_reply(
            message,
            """ဟုတ်ကဲ့ခင်ဗျာ။ 🙏

အခု Internet မရတာက—

📱 Device အားလုံးမှာ မရတာလား?
📱 Device တစ်လုံးတည်းမှာ မရတာလား?
""",
            update,
            ReplyKeyboardMarkup(
                [
                    ["📱 Device အားလုံး မရပါ"],
                    ["📱 Device တစ်လုံးတည်း မရပါ"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    if flow == "unknown_los":

        if "နီ" in text:
            await start_los_flow(message, update, context)
            return

        if "မနီ" in text:

            context.user_data["flow"] = "all_or_one"

            await send_reply(
                message,
                """ဟုတ်ကဲ့ခင်ဗျာ။ 🙏

LOS မီးမနီပါက ဆက်စစ်ပေးပါမယ်။

Internet မရတာက—

📱 Device အားလုံးမှာ မရပါ
📱 Device တစ်လုံးတည်းမှာ မရပါ

ဘယ်အခြေအနေပါလဲ?
""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["📱 Device အားလုံး မရပါ"],
                        ["📱 Device တစ်လုံးတည်း မရပါ"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

    if flow == "all_or_one":

        if "တစ်လုံး" in text:
            await start_single_device_flow(message, update, context)
            return

        if "အားလုံး" in text:
            await start_router_flow(message, update, context)
            return

    if flow == "los":

        if "နီနေဆဲ" in text:

            reset_flow(context)

            await send_reply(
                message,
                """🔴 LOS မီး ဆက်နီနေသေးပါက
Fiber Signal ပြဿနာ ဖြစ်နိုင်ပါတယ်။

Support Team မှ စစ်ဆေးပေးရန်
လိုအပ်နိုင်ပါတယ်ခင်ဗျာ။

📞 Line 1 — Call Center / Customer Service
📞 09-777719577

👤 လူနဲ့ဆက်သွယ်မယ်
""",
                update,
                menu(),
            )
            return

        if "ပျောက်" in text:

            context.user_data["flow"] = "los_recovered"

            await send_reply(
                message,
                """🟢 LOS မီး ပြန်ပျောက်သွားပါပြီ။

အခု Internet ပြန်ရပါသလား?

🟢 ရပါပြီ
🔴 မရသေးပါဘူး
""",
                update,
                yes_no_menu(),
            )
            return

        if "မသိ" in text:

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

LOS မီးက ONU / Router ပေါ်မှာ
🔴 LOS ဆိုတဲ့စာတန်းနားက မီးပါ။

မီးနီနေပါက Fiber Signal ပြဿနာ
ဖြစ်နိုင်ပါတယ်။

မသေချာသေးပါက
📞 Customer Support
09-777719577 ကို ဆက်သွယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

    if flow == "los_recovered":

        reset_flow(context)

        if "မရ" in text:

            await send_reply(
                message,
                """နားလည်ပါတယ်ခင်ဗျာ။ 🙏

LOS မီးပြန်ပျောက်သွားပေမယ့်
Internet မရသေးပါက
Router / ONU ဘက်ကို ဆက်စစ်ဆေးရန်
လိုအပ်နိုင်ပါတယ်။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )

        else:

            await send_reply(
                message,
                """🟢 Internet ပြန်ရပါပြီဆိုရင်
အဆင်ပြေပါပြီခင်ဗျာ။ 🙏

နောက်ထပ် အကူအညီလိုပါက
Menu မှ ပြန်ရွေးချယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )

        return

    if flow == "router":

        if "မသိ" in text:

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

Router / ONU ရဲ့ Power မီးက
များသောအားဖြင့် ⚡ Power ဆိုတဲ့စာတန်းနားမှာ
ရှိပါတယ်။

မီးလင်းနေရင် 🟢
မလင်းရင် 🔴 ဖြစ်ပါတယ်။

မသေချာပါက
📞 09-777719577 ကို ဆက်သွယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        if "မလင်း" in text or "မရှိ" in text:

            reset_flow(context)

            await send_reply(
                message,
                """🔌 Power မီးမလင်းပါက—

1️⃣ Power Adapter ချိတ်ထားမှု စစ်ပါ။
2️⃣ မီးပလပ် / Socket အလုပ်လုပ်/မလုပ် စစ်ပါ။
3️⃣ Adapter ကို သေချာပြန်ချိတ်ပါ။

⚠️ Router / ONU ရဲ့ RESET ခလုတ်ကို
မနှိပ်ပါနဲ့။

မီးမလင်းသေးပါက—

📞 Customer Support
09-777719577

သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )
            return

        context.user_data["flow"] = "router_lights"

        await send_reply(
            message,
            """🟢 Power မီးလင်းနေပါက
PON / LOS မီးကို ဆက်စစ်ပေးပါမယ်။

🔴 LOS နီနေပါသလား?

🔴 နီနေပါတယ်
🟢 မနီပါဘူး
❓ မသိပါဘူး
""",
            update,
            yes_no_menu(),
        )
        return

    if flow == "router_lights":

        if "နီ" in text:
            await start_los_flow(message, update, context)
            return

        if "မနီ" in text:

            reset_flow(context)

            await send_reply(
                message,
                """🟢 LOS မနီပါက Fiber Signal ဘက်က
ပုံမှန်ဖြစ်နိုင်ပါတယ်။

အခု WiFi / Device ဘက်ကို
ဆက်စစ်ပေးပါခင်ဗျာ။

📶 WiFi ပြဿနာကို ရွေးပြီး
ဆက်စစ်နိုင်ပါတယ်။
""",
                update,
                complaint_menu(),
            )
            return

    if flow == "single_device":

        if "မသိ" in text:

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

မရတဲ့ Device က
Internet အသုံးပြုနေတဲ့ ဖုန်းဆိုရင် 📱 Phone
Computer / Laptop ဆိုရင် 💻 Laptop
TV ဆိုရင် 📺 TV ဖြစ်ပါတယ်။

မသေချာရင်
📞 Customer Support ကို ဆက်သွယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        if any(
            x in text
            for x in ["phone", "laptop", "computer", "tv"]
        ):

            context.user_data["flow"] = "single_device_result"

            await send_reply(
                message,
                """ဟုတ်ကဲ့ခင်ဗျာ။ 🙏

WiFi ကို—

1️⃣ Disconnect လုပ်ပါ။
2️⃣ ပြန် Connect လုပ်ပါ။
3️⃣ Internet ပြန်ရ/မရ စမ်းကြည့်ပါ။

အခု Internet ပြန်ရပါသလား?

🟢 ရပါပြီ
🔴 မရသေးပါဘူး
""",
                update,
                yes_no_menu(),
            )
            return

    if flow == "single_device_result":

        reset_flow(context)

        if "ရပါ" in text and "မရ" not in text:

            await send_reply(
                message,
                """🟢 အဆင်ပြေပါပြီခင်ဗျာ။ 🙏

WiFi ကို ပြန်ချိတ်ပြီး Internet ရပြီဆိုရင်
Device Connection ဘက်က ပြဿနာဖြစ်နိုင်ပါတယ်။

နောက်ထပ်အကူအညီလိုပါက
Menu မှ ပြန်ရွေးချယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )

        else:

            await send_reply(
                message,
                """နားလည်ပါတယ်ခင်ဗျာ။ 🙏

Device တစ်လုံးတည်းမှာ
Internet မရသေးပါက Device ဘက်ကို
ထပ်မံစစ်ဆေးရန် လိုအပ်နိုင်ပါတယ်။

📞 Customer Support
09-777719577 သို့
ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )

        return

    if flow == "speed":

        if "1" in text or "အားလုံး" in text:

            context.user_data["flow"] = "speed_test"

            await send_reply(
                message,
                """📈 Device အားလုံးမှာ နှေးနေပါက
Speed Test စစ်ပေးပါမယ်ခင်ဗျာ။

အရင်ဆုံး Speed Test လုပ်ပေးပါ။

Speed Test ရလဒ်မှာ
Download / Upload Speed ကို
ကြည့်ပေးပါ။

📸 ရလဒ် Screenshot ရှိပါက
ပို့ပေးနိုင်ပါတယ်။

Speed Test ပြီးပါက
ရလဒ်ကို ပြန်ပို့ပေးပါခင်ဗျာ။
""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["📸 Speed Test ရပြီးပါပြီ"],
                        ["❓ မသိပါဘူး"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        if "2" in text or "တစ်လုံး" in text:

            reset_flow(context)

            await send_reply(
                message,
                """📱 Device တစ်လုံးတည်းမှာ နှေးနေပါက
Device / WiFi ဘက်က ပြဿနာဖြစ်နိုင်ပါတယ်။

WiFi ကို Disconnect → Connect
ပြန်လုပ်ပြီး စမ်းကြည့်ပါခင်ဗျာ။

မရသေးပါက—

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

        if "3" in text or "ညဘက်" in text:

            context.user_data["flow"] = "speed_night"

            await send_reply(
                message,
                """🌙 ညဘက်မှာ ပိုနှေးတယ်ဆိုရင်
ဘယ်အချိန်လောက်မှာ စပြီး
နှေးလာတတ်ပါသလဲခင်ဗျာ?

ဥပမာ—
8:00 PM / 9:00 PM / 10:00 PM
စသဖြင့် အချိန်ကို ပြောပေးနိုင်ပါတယ်။
""",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        if "4" in text or "အချိန်တိုင်း" in text:

            context.user_data["flow"] = "speed_test"

            await send_reply(
                message,
                """📈 အချိန်တိုင်းနှေးနေပါက
Speed Test စစ်ပေးပါခင်ဗျာ။

Speed Test ရလဒ် Screenshot ရှိပါက
ပို့ပေးနိုင်ပါတယ်။

📸 Speed Test ရပြီးပါပြီ
ဆိုပြီး ပြန်ပို့ပေးပါ။
""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["📸 Speed Test ရပြီးပါပြီ"],
                        ["❓ မသိပါဘူး"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        if "5" in text or "app" in text or "website" in text:

            await start_app_flow(message, update, context)
            return

    if flow == "speed_test":

        if "မသိ" in text:

            reset_flow(context)

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

Speed Test မလုပ်တတ်ပါက
📞 Customer Support
09-777719577
သို့ ဆက်သွယ်နိုင်ပါတယ်။

မိမိသုံးနေတဲ့ Package Speed ကိုလည်း
Package / Price မှာ ပြန်ကြည့်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        reset_flow(context)

        await send_reply(
            message,
            """📈 Speed Test ရလဒ်ကို
Support Team မှ ဆက်လက်စစ်ဆေးပေးနိုင်ပါတယ်။

📞 Customer Support
09-777719577

📸 Speed Test Screenshot ရှိပါက
ပို့ပေးနိုင်ပါတယ်။
""",
            update,
            menu(),
        )
        return

    if flow == "speed_night":

        reset_flow(context)

        await send_reply(
            message,
            """ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။ 🙏

ညဘက် Internet နှေးတဲ့အချိန်ကို
Support Team မှ ဆက်လက်စစ်ဆေးပေးနိုင်ပါတယ်။

📞 Customer Support
09-777719577

⏰ Support Time
မနက် 9:00 AM – 12:00 PM
""",
            update,
            menu(),
        )
        return

    if flow == "disconnect":

        if "မသိ" in text:

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

လိုင်းပြတ်တဲ့အချိန်
ONU / Router ပေါ်မှာ
🔴 LOS မီးနီလာ/မလာ
ကို ကြည့်ပေးပါ။

မသေချာပါက
📞 Customer Support
09-777719577
သို့ ဆက်သွယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        if "နီ" in text or "ဟုတ်" in text:

            await start_los_flow(message, update, context)
            return

        context.user_data["flow"] = "disconnect_restart"

        await send_reply(
            message,
            """ဟုတ်ကဲ့ခင်ဗျာ။ 🙏

LOS မီးမနီဘဲ Internet ခဏခဏပြတ်နေပါက
Router / WiFi ဘက်ကို ဆက်စစ်ပါမယ်။

လိုင်းပြတ်ပြီးနောက်
Router / ONU ကို Restart လုပ်မှ
Internet ပြန်ရတာလား?

🔄 ဟုတ်ပါတယ်
❌ မဟုတ်ပါဘူး
""",
            update,
            yes_no_menu(),
        )
        return

    if flow == "disconnect_restart":

        reset_flow(context)

        if "ဟုတ်" in text:

            await send_reply(
                message,
                """🔄 Router / ONU ကို Restart လုပ်မှ
ပြန်ရတယ်ဆိုရင် Router / Connection ဘက်မှာ
ပြဿနာရှိနိုင်ပါတယ်။

⚠️ RESET ခလုတ်ကို မနှိပ်ပါနဲ့။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )

        else:

            await send_reply(
                message,
                """နားလည်ပါတယ်ခင်ဗျာ။ 🙏

LOS မနီဘဲ Internet ခဏခဏပြတ်နေပါက
WiFi / Router အခြေအနေကို
ဆက်လက်စစ်ဆေးရန် လိုအပ်နိုင်ပါတယ်။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )

        return

    if flow == "wifi":

        if "မသိ" in text:

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

WiFi Name (SSID) ဆိုတာ
ဖုန်းမှာ WiFi ရှာတဲ့အခါ ပေါ်လာတဲ့
WiFi နာမည်ပါ။

ဥပမာ—
Ultra Net XXXXX

အဲဒီနာမည်ကို တွေ့/မတွေ့
ကြည့်ပေးပါခင်ဗျာ။
""",
                update,
                yes_no_menu(),
            )
            return

        if "မတွေ့" in text or "မရှိ" in text:

            context.user_data["flow"] = "wifi_not_found"

            await send_reply(
                message,
                """🔴 WiFi Name မတွေ့ပါက—

1️⃣ Router / ONU Power မီး လင်း/မလင်း စစ်ပါ။
2️⃣ WiFi ကို ဖုန်းမှာ ပြန်ရှာပါ။
3️⃣ Router အနီးမှာ စမ်းကြည့်ပါ။

အခု WiFi Name ပြန်ပေါ်လာပါသလား?

🟢 ပေါ်လာပါပြီ
🔴 မပေါ်သေးပါဘူး
""",
                update,
                yes_no_menu(),
            )
            return

        context.user_data["flow"] = "wifi_password"

        await send_reply(
            message,
            """🟢 WiFi Name တွေ့တယ်ဆိုရင်
Password ထည့်ပြီး ချိတ်ကြည့်ပေးပါခင်ဗျာ။

Password ထည့်ပြီးနောက်
ဘာအခြေအနေ ဖြစ်ပါသလဲ?

🔴 Password မှားတယ်လို့ ပြတယ်
🔴 ချိတ်နေပြီး မချိတ်နိုင်ဘူး
🟢 WiFi ချိတ်ပြီး Internet မရဘူး
""",
            update,
            ReplyKeyboardMarkup(
                [
                    ["🔴 Password မှား"],
                    ["🔴 Connecting မရ"],
                    ["🟢 WiFi ချိတ်ပြီး Internet မရ"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    if flow == "wifi_not_found":

        reset_flow(context)

        if "ပေါ်လာ" in text and "မပေါ်" not in text:

            await send_reply(
                message,
                """🟢 WiFi Name ပြန်ပေါ်လာပါပြီဆိုရင်
WiFi Connection ကို ပြန်စမ်းကြည့်နိုင်ပါတယ်။

မရသေးပါက
📞 Customer Support
09-777719577
သို့ ဆက်သွယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )

        else:

            await send_reply(
                message,
                """🔴 WiFi Name မပေါ်သေးပါက
Router WiFi Broadcast ဘက်ကို
စစ်ဆေးရန် လိုအပ်နိုင်ပါတယ်။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )

        return

    if flow == "wifi_password":

        reset_flow(context)

        if "password" in text and "မှား" in text:

            await send_reply(
                message,
                """🔐 Password မှားတယ်လို့ ပြပါက
Password ကို ပြန်စစ်ပြီး
ထပ်မံချိတ်ကြည့်ပေးပါခင်ဗျာ။

Password မသေချာပါက
📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးနိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        if "connecting" in text or "ချိတ်နေ" in text:

            await send_reply(
                message,
                """📶 WiFi ကို တွေ့ပြီး
ချိတ်နေသော်လည်း မချိတ်နိုင်ပါက—

WiFi ကို Forget လုပ်ပြီး
Password ပြန်ထည့်ကာ
Connect လုပ်ကြည့်ပေးပါခင်ဗျာ။

မရသေးပါက
📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

        await send_reply(
            message,
            """🟢 WiFi ချိတ်ပြီး Internet မရပါက
WiFi ပြဿနာထက် Internet Connection ဘက်ကို
ဆက်စစ်ရန် လိုအပ်နိုင်ပါတယ်။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
            update,
            menu(),
        )
        return

    if flow == "app":

        reset_flow(context)

        if "ရပါတယ်" in text or (
            "ရ" in text and "မရ" not in text
        ):

            await send_reply(
                message,
                """🟢 အခြား App / Website တွေ ရတယ်ဆိုရင်
Internet လိုင်းတစ်ခုလုံး ပြဿနာမဟုတ်နိုင်ပါ။

မရတဲ့ App / Website ဘက်က
ပြဿနာဖြစ်နိုင်ပါတယ်။

App ကို Update လုပ်ခြင်း၊
Restart လုပ်ခြင်း စတာတွေ စမ်းကြည့်နိုင်ပါတယ်။

မပြေလည်သေးပါက
📞 Customer Support
09-777719577
သို့ ဆက်သွယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        await send_reply(
            message,
            """🔴 အခြား App / Website တွေလည်း
မရဘူးဆိုရင် Internet Connection ဘက်မှာ
ပြဿနာရှိနိုင်ပါတယ်။

Internet Problem Menu မှ
🔧 Internet လုံးဝမရ
ကို ရွေးပြီး ဆက်စစ်နိုင်ပါတယ်။

မပြေလည်ပါက
📞 Customer Support
09-777719577
""",
            update,
            complaint_menu(),
        )
        return


# =========================================================
# MAIN MESSAGE HANDLER
# =========================================================

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.effective_message

    if not message:
        return

    if not message.text:
        return

    raw = message.text.strip()
    text = normalize(raw)

    # =====================================================
    # MAIN MENU
    # =====================================================

    if raw == "🔙 Main Menu":

        reset_flow(context)

        await send_reply(
            message,
            """🏠 Main Menu

ဘာကိစ္စအတွက် ကူညီပေးရမလဲခင်ဗျာ? 🙏
""",
            update,
            menu(),
        )
        return

    # =====================================================
    # CUSTOMER ID BUTTON
    # =====================================================

    if raw == "🆔 Customer ID စစ်မယ်":

        await start_customer_id_flow(
            message,
            update,
            context,
        )
        return

    # =====================================================
    # CUSTOMER ID ACTIVE FLOW
    # =====================================================

    if context.user_data.get("flow") == "customer_id":

        await handle_customer_id_flow(
            message,
            update,
            context,
            raw,
        )
        return

    # =====================================================
    # NEW INSTALLATION BUTTON
    # =====================================================

    if raw == "📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း":

        await start_installation_flow(
            message,
            update,
            context,
        )
        return

    # =====================================================
    # INSTALLATION ACTIVE FLOW
    # =====================================================

    if context.user_data.get("flow", "").startswith("install_"):

        await handle_installation_flow(
            message,
            update,
            context,
            raw,
        )
        return

    # =====================================================
    # OFFICE LOCATION
    # =====================================================

    if raw == "📍 ရုံးတည်နေရာ / Location":

        reset_flow(context)

        await send_reply(
            message,
            LOCATION_TEXT,
            update,
            menu(),
        )
        return

    # =====================================================
    # SOCIAL MEDIA
    # =====================================================

    if raw == "📱 Social Media":

        reset_flow(context)

        await send_reply(
            message,
            SOCIAL_TEXT,
            update,
            menu(),
        )
        return

    # =====================================================
    # HUMAN SUPPORT
    # =====================================================

    if raw == "👤 လူနဲ့ဆက်သွယ်မယ်" or any(
        x in text
        for x in [
            "လူနဲ့ဆက်သွယ်",
            "customersupport",
        ]
    ):

        reset_flow(context)

        await send_reply(
            message,
            SUPPORT_TEXT,
            update,
            menu(),
        )
        return

    # =====================================================
    # CUSTOMER SUPPORT
    # =====================================================

    if raw == "📞 Customer Support":

        reset_flow(context)

        await send_reply(
            message,
            SUPPORT_TEXT,
            update,
            menu(),
        )
        return

    # =====================================================
    # PAYMENT
    # =====================================================

    if raw == "💰 Payment" or any(
        x in text
        for x in [
            "payment",
            "kpay",
            "wavepay",
            "wavemoney",
            "ငွေပေး",
        ]
    ):

        reset_flow(context)

        await send_reply(
            message,
            PAYMENT_TEXT,
            update,
            menu(),
        )
        return

    # =====================================================
    # PACKAGE DETAIL
    # =====================================================

    for speed in ["15", "25", "35", "50", "70"]:

        if f"{speed}mbps" in text:

            reset_flow(context)

            await send_reply(
                message,
                package_text(speed),
                update,
                menu(),
            )

            return

    # =====================================================
    # ALL PACKAGES
    # =====================================================

    if raw == "📦 Package / Price" or any(
        x in text
        for x in [
            "price",
            "package",
            "packages",
            "ဈေး",
            "စျေး",
            "ပက်ကေ့",
            "ပက်ကေ့ချ်",
        ]
    ):

        reset_flow(context)

        package_list = """📦 Ultra Net KAK Packages

🏠 Home

1️⃣ 15 Mbps — 190,000 Ks
2️⃣ 25 Mbps — 200,000 Ks
3️⃣ 35 Mbps — 230,000 Ks

🏢 Business

4️⃣ 50 Mbps — 300,000 Ks
5️⃣ 70 Mbps — 400,000 Ks

⚠️ အထက်ပါ Initial Installation ဈေးနှုန်းများတွင်
Device + First Month ပါဝင်ပါသည်။

🔌 Cable Fee

250m အထိ အခမဲ့။

250m ကျော်ပါက
1m = 1,000 Ks အပိုကြေး။

📅 ဒီနေ့ စာရင်းတင်ပြီးပါက
မနက်ဖြန် Survey ဆင်းစစ်ဆေးပေးပါမယ်။

📅 Survey ပြီးနောက် ၃ ရက်အတွင်း
တပ်ဆင်ပေးပါမယ်။

15 / 25 / 35 / 50 / 70 Mbps
လို့ ပြန်ပို့ရင် အသေးစိတ်ပြပေးပါမယ်။
"""

        await send_reply(
            message,
            package_list,
            update,
            menu(),
        )
        return

    # =====================================================
    # INTERNET PROBLEM
    # =====================================================

    if raw == "🛠 Internet Problem":

        reset_flow(context)

        await show_complaint_menu(
            message,
            update,
        )
        return

    # =====================================================
    # COMPLAINT BUTTONS
    # =====================================================

    if raw == "🔧 Internet လုံးဝမရ":
        await start_internet_flow(message, update, context)
        return

    if raw == "🔴 LOS မီးနီ":
        await start_los_flow(message, update, context)
        return

    if raw == "🐌 Internet နှေး":
        await start_speed_flow(message, update, context)
        return

    if raw == "🔌 Internet ခဏခဏပြတ်":
        await start_disconnect_flow(message, update, context)
        return

    if raw == "📶 WiFi ပြဿနာ":
        await start_wifi_flow(message, update, context)
        return

    if raw == "⚡ Router / ONU ပြဿနာ":
        await start_router_flow(message, update, context)
        return

    if raw == "📱 Device တစ်လုံးတည်း မရ":
        await start_single_device_flow(message, update, context)
        return

    if raw == "🌐 Website / App တစ်ခုတည်း မရ":
        await start_app_flow(message, update, context)
        return

    # =====================================================
    # CURRENT INTERNET FLOW
    # =====================================================

    flow = context.user_data.get("flow")

    if flow:

        await handle_internet_flow(
            message,
            update,
            context,
            text,
        )
        return

    # =====================================================
    # DIRECT INTERNET KEYWORDS
    # =====================================================

    if any(
        x in text
        for x in [
            "internetမရ",
            "အင်တာနက်မရ",
            "လိုင်းမရ",
            "လိုင်းပျက်",
            "internetပြတ်",
            "လိုင်းပြတ်",
        ]
    ):

        await start_internet_flow(
            message,
            update,
            context,
        )
        return

    # =====================================================
    # DIRECT SPEED KEYWORDS
    # =====================================================

    if any(
        x in text
        for x in [
            "internetနှေး",
            "အင်တာနက်နှေး",
            "လိုင်းနှေး",
            "speedမပြည့်",
            "buffering",
            "slow",
        ]
    ):

        await start_speed_flow(
            message,
            update,
            context,
        )
        return

    # =====================================================
    # DIRECT WIFI KEYWORDS
    # =====================================================

    if any(
        x in text
        for x in [
            "wifiမရ",
            "wifiမပေါ်",
            "wifiနှေး",
            "ဝိုင်ဖိုင်",
        ]
    ):

        await start_wifi_flow(
            message,
            update,
            context,
        )
        return

    # =====================================================
    # DIRECT LOS
    # =====================================================

    if "los" in text:

        await start_los_flow(
            message,
            update,
            context,
        )
        return

    # =====================================================
    # GREETING
    # =====================================================

    if any(
        x in text
        for x in [
            "hello",
            "hi",
            "မင်္ဂလာပါ",
        ]
    ):

        reset_flow(context)

        await send_reply(
            message,
            f"""မင်္ဂလာပါခင်ဗျာ။ 🙏

{BOT_NAME} မှ ကြိုဆိုပါတယ်။

Package, Payment, Internet Problem
သို့မဟုတ် Customer Support
အကြောင်း မေးနိုင်ပါတယ်။
""",
            update,
            menu(),
        )
        return

    # =====================================================
    # DEFAULT
    # =====================================================

    await send_reply(
        message,
        """မေးလိုတဲ့အကြောင်းအရာကို
ပြောပေးပါခင်ဗျာ။ 🙏

📦 Package / Price
🛠 Internet Problem
💰 Payment
📞 Customer Support
🆔 Customer ID စစ်မယ်
👤 လူနဲ့ဆက်သွယ်မယ်
📍 ရုံးတည်နေရာ / Location
📱 Social Media
📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း

Internet ပြဿနာဖြစ်ပါက
🛠 Internet Problem ကို နှိပ်ပြီး
သက်ဆိုင်ရာ ပြဿနာကို ရွေးချယ်နိုင်ပါတယ်။
""",
        update,
        menu(),
    )


# =========================================================
# RUN BOT
# =========================================================

def main():

    if not TOKEN:
        raise ValueError(
            "BOT_TOKEN environment variable မရှိသေးပါ။"
        )

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            answer,
        )
    )

    print(
        f"{BOT_NAME} Bot is running..."
    )

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()
