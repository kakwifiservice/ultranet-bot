# -*- coding: utf-8 -*-
"""Ultra Net KAK customer-support Telegram bot.
Python 3.14; python-telegram-bot 22.x
Set BOT_TOKEN and ADMIN_CHAT_ID as environment variables. Never paste the token into chat.
"""
import os
import re
import logging
import asyncio
from datetime import datetime, timedelta, timezone
from telegram import (
    Update, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes, filters,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("ultranet")

BOT_NAME = "Ultra Net KAK WiFi Internet Service Provider"
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "").strip()
BOT_USERNAME = "UltraNetKAKMM_bot"
CHANNEL_URL = "https://t.me/ultranetkak"
GROUP_URL = "https://t.me/+30B6ITGkrfg5YTA1"
SUPPORT_PHONE = "09-777719577"
SUPPORT_TELEGRAM = "@UltraNetKAKWiFi"
PAYMENT_VIBER = "09-796000066"
OFFICE_ADDRESS = "ဓိဌာန်အောင် ဘုရားလမ်း၊ အမှတ်(၄)ရပ်ကွက်၊ မြဝတီမြို့"
SUPPORT_HOURS = "နေ့စဉ် နံနက် ၉:၀၀ မှ နေ့လယ် ၁၂:၀၀ အထိ"

PACKAGES = {
    "15": {"speed": "15 Mbps", "monthly": 40000, "total": 190000, "kind": "အိမ်သုံး"},
    "25": {"speed": "25 Mbps", "monthly": 50000, "total": 200000, "kind": "အိမ်သုံး"},
    "35": {"speed": "35 Mbps", "monthly": 80000, "total": 230000, "kind": "အိမ်သုံး"},
    "50": {"speed": "50 Mbps", "monthly": 150000, "total": 300000, "kind": "လုပ်ငန်းသုံး"},
    "70": {"speed": "70 Mbps", "monthly": 250000, "total": 400000, "kind": "လုပ်ငန်းသုံး"},
}
DEVICE_FEE = 150000
CABLE_INFO = "ကြိုးခ: ရုံး/အထိုင်ပုံးမှ အိမ်အထိ ၂၅၀ မီတာအတွင်း အခမဲ့။ ၂၅၀ မီတာကျော်လျှင် ပိုသည့် ၁ မီတာလျှင် ၁,၀၀၀ ကျပ်။ ဥပမာ ၂၈၀ မီတာဆို ၃၀,၀၀၀ ကျပ် ထပ်ကျမည်။ မိမိဘာသာ မတိုင်းပါနှင့်၊ ဝန်ထမ်းက Survey လုပ်ချိန် တိုင်းပေးပါမည်။"

MAIN_MENU = [
    ["📦 Package / Price", "🌐 Internet Problem"],
    ["💳 Payment", "🆔 Customer ID စစ်မယ်"],
    ["📝 လိုင်းသစ်တပ်မယ်", "🔐 WiFi Password ပြောင်းမယ်"],
    ["☎️ Customer Support", "📍 Location"],
    ["🔗 Social Media", "ℹ️ ဝန်ဆောင်မှုအကြောင်း"],
]
MENU_MARKUP = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
YES_NO = ReplyKeyboardMarkup([["ဟုတ်ပါတယ်", "မဟုတ်ပါဘူး"], ["မသေချာပါဘူး", "မီနူးသို့ပြန်မယ်"]], resize_keyboard=True)

# Only these keys describe temporary conversations. Customer identity remains available
# until the user explicitly restarts or changes it.
TRANSIENT_KEYS = (
    "flow", "pending_complaint", "complaint_type", "complaint_step",
    "install", "install_step", "password_request", "password_step",
    "last_speed", "last_issue",
)

def reset_flow(context: ContextTypes.DEFAULT_TYPE, clear_identity: bool = False) -> None:
    for key in TRANSIENT_KEYS:
        context.user_data.pop(key, None)
    if clear_identity:
        context.user_data.pop("customer_id", None)
        context.user_data.pop("customer_phone", None)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def money(value: int) -> str:
    return f"{value:,} ကျပ်"

async def safe_reply(update: Update, text: str, reply_markup=None) -> None:
    if update.effective_message:
        await update.effective_message.reply_text(text, reply_markup=reply_markup)

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, message: str) -> bool:
    if not ADMIN_CHAT_ID:
        log.error("ADMIN_CHAT_ID is not configured; admin notification not sent")
        return False
    try:
        await context.bot.send_message(chat_id=int(ADMIN_CHAT_ID), text=message)
        return True
    except (ValueError, Exception):
        log.exception("Could not send admin notification")
        return False

def user_details(update: Update) -> str:
    user = update.effective_user
    chat = update.effective_chat

    if not user:
        return "Customer information unavailable"

    username = f"@{user.username}" if user.username else "မရှိပါ"
    full_name = user.full_name or "မရှိပါ"
    telegram_id = user.id
    chat_id = chat.id if chat else "မရှိပါ"

    return (
        f"👤 Customer: {full_name}\n"
        f"📱 Username: {username}\n"
        f"🆔 Telegram ID: {telegram_id}\n"
        f"💬 Chat ID: {chat_id}"
    )

TOKEN = BOT_TOKEN

async def send_complaint_report(update, context, problem, result):
    user = update.effective_user

    customer_id = context.user_data.get(
        "customer_id", "မရှိပါ"
    )
    customer_phone = context.user_data.get(
        "customer_phone", "မရှိပါ"
    )

    report = f"""🚨 Ultra Net KAK — Internet Complaint

👤 Customer: {user.full_name}
🆔 Customer ID: {customer_id}
📞 ဖုန်းနံပါတ်: {customer_phone}
🆔 Telegram ID: {user.id}
📱 Username: @{user.username or 'မရှိပါ'}

🔧 Complaint: {problem}
📋 စစ်ဆေးပြီးရလဒ်: {result}

📞 Support Team မှ ဆက်သွယ်စစ်ဆေးပေးပါ။
"""

    await notify_admin(context, report)

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

PAYMENT_TEXT = """🧾 Bill (ဘေလ်) ပေးဆောင်ခြင်း

🌐 Online (လိုင်း) ပေါ်မှ Bill (ဘေလ်) ဆောင်မည်ဆိုပါက

KPay / Wave Money ဖြင့် Bill (ဘေလ်) ဆောင်နိုင်ပါတယ်ခင်ဗျာ။

💳 KPay - 09-796 000 066

💳 Wave Money - 09-796 000 066

KPay / Wave Money ဖြင့် ငွေလွှဲပြီးနောက်

🧾 ငွေလွှဲထားသော Screenshot နှင့်

🆔 မိမိ Bill ဆောင်မည့်စက်၏ ID နံပါတ်ကို Viber 09-796 000 066 သို့ ပို့ပေးပါ။

ဥပမာ — KAKMWD-0000000

⚠️ KAKMWD-0000000 သည် နမူနာသာဖြစ်ပါသည်။
မိမိ၏ စက် ID အမှန်ကိုသာ ပို့ပေးပါ။

📱 Viber: 09-796 000 066
👤 Viber Name: KAK Internet pay

💵 Cash ဖြင့် Bill (ဘေလ်) ပေးဆောင်လိုပါက

ရုံးသို့ လူကိုယ်တိုင်လာရောက်၍
Bill (ဘေလ်) ပေးဆောင်နိုင်ပါသည်ခင်ဗျာ။ 🙏
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

━━━━━━━━━━━━━━━━━━

📝 လိုင်းသစ် တပ်ဆင်လိုပါက

အောက်ပါ Menu မှ
「📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း」
ကို နှိပ်ပြီး လိုင်းသစ်တပ်ဆင်ရန်
စာရင်းပေးသွင်းနိုင်ပါတယ်ခင်ဗျာ။

🙏 Ultra Net KAK ကို အသုံးပြုပေးတဲ့အတွက်
ကျေးဇူးအထူးတင်ရှိပါတယ်။
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
            ["🧾 Bill (ဘေလ်) ပေးဆောင်ခြင်း", "📞 Customer Support"],
            ["🆔 Customer ID စစ်မယ်", "👤 လူနဲ့ဆက်သွယ်မယ်"],
            ["📍 ရုံးတည်နေရာ / Location", "📱 Social Media"],
            ["📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း"],
            ["📍 WiFi နေရာပြောင်း"],
            ["♻️ WiFi ပြန်လည်အသုံးပြုရန်"],
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
            ["🔐 WiFi Password ပြောင်းရန်"],
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
            ["🔴 LOS နီနေပါတယ်"],
            ["🟢 LOS မနီပါဘူး"],
            ["❓ မသိပါဘူး"],
            ["🔙 Main Menu"],
        ],
        resize_keyboard=True,
    )

# =========================================================
# ROUTER POWER MENU
# =========================================================

def router_power_menu():
    return ReplyKeyboardMarkup(
        [
            ["🟢 လင်းပါတယ်"],
            ["🔴 မလင်းပါဘူး"],
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
📞 Customer Support
09-777719577

လိုင်းခွဲနံပါတ် (1) Customer Service ကို
ခေါ်ဆိုပေးပါခင်ဗျာ။ 🙏
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
        context.user_data["customer_id"] = customer_id

        pending = context.user_data.get("pending_complaint")

        # Complaint ရွေးထားမှ ဖုန်းနံပါတ်တောင်းမယ်
        if pending:
            context.user_data["flow"] = "complaint_phone"

            await send_reply(
                message,
                f"""✅ Customer ID မှန်ကန်ပါတယ်။

🆔 Customer ID: {customer_id}

📞 ဆက်သွယ်ရန် ဖုန်းနံပါတ်လေး ပေးပါခင်ဗျာ။

မြန်မာဖုန်းနံပါတ် 09 နဲ့ စပြီး
နံပါတ် 9 မှ 11 လုံးအထိ ထည့်ပေးပါ။

ဥပမာ — 09XXXXXXXXX""",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        # သီးခြား Customer ID စစ်ဆေးခြင်း
        reset_flow(context)

        await send_reply(
            message,
            f"""✅ Customer ID ပုံစံ မှန်ကန်ပါတယ်။

🆔 Customer ID: {customer_id}

📌 ဤ ID သည် ပုံစံမှန်ကန်ကြောင်းသာ
စစ်ဆေးပေးထားခြင်း ဖြစ်ပါတယ်။

စက်အချက်အလက်ကို အတည်ပြုလိုပါက
Customer Support ကို ဆက်သွယ်ပေးပါခင်ဗျာ။""",
            update,
            menu(),
        )
        return

    await send_reply(
        message,
        """❌ Customer ID ပုံစံ မမှန်ပါ။

KAKMWD- နောက်မှာ ဂဏန်း 7 လုံး
ပါရပါမယ်။

ဥပမာ — KAKMWD-1234567

မိမိ၏ Customer ID အမှန်ကို ပြန်ပို့ပေးပါ။""",
        update,
        ReplyKeyboardMarkup(
            [["🔙 Main Menu"]],
            resize_keyboard=True,
        ),
    )

# =========================================================
# INTERNET RELOCATION START
# =========================================================

async def start_relocation_flow(message, update, context):

    reset_flow(context)

    context.user_data["flow"] = "relocate_current_address"

    await send_reply(
        message,
        """🔄 Internet လိုင်း ရွှေ့ပြောင်းခြင်း

ရပါတယ်ခင်ဗျာ။ 🙏

အိမ်ပြောင်းပြီး Internet လိုင်းကို
ပြောင်းမဲ့လိပ်စာဆီ ရွှေ့လိုပါက
တစ်ပတ်ကြိုတင် စာရင်းပေးသွင်းပေးပါခင်ဗျာ။

အရင်ဆုံး လက်ရှိအသုံးပြုနေတဲ့
လိပ်စာကို ပို့ပေးပါ။
""",
        update,
        ReplyKeyboardMarkup(
            [["🔙 Main Menu"]],
            resize_keyboard=True,
        ),
    )

# =========================================================
# INTERNET RELOCATION FLOW HANDLER
# =========================================================

async def handle_relocation_flow(message, update, context, raw):

    flow = context.user_data.get("flow")
    text = raw.strip()

    if text == "🔙 Main Menu":
        reset_flow(context)
        await send_reply(
            message,
            "Main Menu သို့ ပြန်သွားပါပြီ။",
            update,
            menu(),
        )
        return

    # -----------------------------------------------------
    # CURRENT ADDRESS
    # -----------------------------------------------------

    if flow == "relocate_current_address":

        if len(text) < 3:
            await send_reply(
                message,
                "လက်ရှိအသုံးပြုနေတဲ့ လိပ်စာကို ပြန်ပို့ပေးပါခင်ဗျာ။",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["relocate_current_address"] = text
        context.user_data["flow"] = "relocate_new_address"

        await send_reply(
            message,
            """📍 လက်ရှိလိပ်စာ ရရှိပါပြီ။

အခု ပြောင်းမဲ့ လိပ်စာကို
ပို့ပေးပါခင်ဗျာ။
""",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # NEW ADDRESS
    # -----------------------------------------------------

    if flow == "relocate_new_address":

        if len(text) < 3:
            await send_reply(
                message,
                "ပြောင်းမဲ့ လိပ်စာကို ပြန်ပို့ပေးပါခင်ဗျာ။",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["relocate_new_address"] = text
        context.user_data["flow"] = "relocate_customer_id"

        await send_reply(
            message,
            """✅ ပြောင်းမဲ့ လိပ်စာ ရရှိပါပြီ။

🆔 Customer ID ကို ပို့ပေးပါခင်ဗျာ။

ဥပမာ —
KAKMWD-1234567
""",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # CUSTOMER ID
    # -----------------------------------------------------

    if flow == "relocate_customer_id":

        customer_id = text.upper().replace(" ", "")

        if not re.fullmatch(r"KAKMWD-\d{7}", customer_id):

            await send_reply(
                message,
                """❌ Customer ID ပုံစံ မမှန်သေးပါဘူး။

KAKMWD- နဲ့စပြီး
နောက်မှာ ဂဏန်း ၇ လုံး ပါရပါမယ်။

ဥပမာ —
KAKMWD-1234567
""",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["relocate_customer_id"] = customer_id
        context.user_data["flow"] = "relocate_phone1"

        await send_reply(
            message,
            """✅ Customer ID ရရှိပါပြီ။

📞 ဆက်သွယ်ရန် ဖုန်းနံပါတ်ကို
ပို့ပေးပါခင်ဗျာ။
""",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # PHONE 1
    # -----------------------------------------------------

    if flow == "relocate_phone1":

        phone = text.replace(" ", "").replace("-", "")

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

        context.user_data["relocate_phone1"] = phone
        context.user_data["flow"] = "relocate_phone2"

        await send_reply(
            message,
            """✅ ဖုန်းနံပါတ် ရရှိပါပြီ။

အခြားဆက်သွယ်ရန် ဖုန်းနံပါတ်
တစ်ခုရှိသေးပါသလားခင်ဗျာ။

ဖုန်းနံပါတ် ၂ ခုရှိပါက
တစ်ခုကို ဆက်သွယ်မရတဲ့အခါ
အခြားတစ်ခုကို ဆက်သွယ်နိုင်ပါတယ်။

ဒုတိယဖုန်းနံပါတ်ကို ပို့ပါ။
မရှိပါက “မရှိပါ” ကို နှိပ်ပါ။
""",
            update,
            ReplyKeyboardMarkup(
                [["မရှိပါ"], ["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # PHONE 2
    # -----------------------------------------------------

    if flow == "relocate_phone2":

        if text == "မရှိပါ":
            context.user_data["relocate_phone2"] = "မရှိပါ"
        else:
            phone = text.replace(" ", "").replace("-", "")

            if not re.fullmatch(r"(09\d{7,9}|\+959\d{7,9})", phone):

                await send_reply(
                    message,
                    """❌ ဖုန်းနံပါတ်ပုံစံ မမှန်သေးပါဘူး။

ဥပမာ —
09xxxxxxxxx

ဒုတိယဖုန်းနံပါတ်ကို ပြန်ပို့ပါ။
မရှိပါက “မရှိပါ” ကို နှိပ်ပါ။
""",
                    update,
                    ReplyKeyboardMarkup(
                        [["မရှိပါ"], ["🔙 Main Menu"]],
                        resize_keyboard=True,
                    ),
                )
                return

            context.user_data["relocate_phone2"] = phone

        context.user_data["flow"] = "relocate_confirm"

        summary = relocation_summary(context)

        await send_reply(
            message,
            summary,
            update,
            ReplyKeyboardMarkup(
                [
                    ["✅ အတည်ပြုမယ်"],
                    ["🔄 ပြန်ပြင်မယ်"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # CONFIRM
    # -----------------------------------------------------

    if flow == "relocate_confirm":

        if text == "🔄 ပြန်ပြင်မယ်":
            await start_relocation_flow(message, update, context)
            return

        if text == "✅ အတည်ပြုမယ်":

            summary = relocation_summary(context)

            await notify_admin(
                context,
                "🔄 Internet လိုင်းရွှေ့ပြောင်းရန် "
                "လျှောက်လွှာအသစ်\n\n"
                f"{summary}"
            )

            reset_flow(context)

            await send_reply(
                message,
                """✅ Internet လိုင်းရွှေ့ပြောင်းရန်
စာရင်းပေးသွင်းမှုကို အတည်ပြုပြီးပါပြီ။

နောက်တစ်နေ့မှာ Survey ဆင်းစစ်ဆေးပေးပါမယ်။

📞 Customer Support
09-777719577

အသေးစိတ် ဆက်သွယ်မေးမြန်းလိုပါက
လိုင်းခွဲနံပါတ် (1) Customer Service ကို
ခေါ်ဆိုပေးပါခင်ဗျာ။ 🙏

ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။
Ultra Net KAK WiFi Internet Service Provider
""",
                update,
                menu(),
            )
            return

        await send_reply(
            message,
            "အောက်ပါခလုတ်များထဲမှ တစ်ခုကို ရွေးချယ်ပေးပါခင်ဗျာ။",
            update,
            ReplyKeyboardMarkup(
                [
                    ["✅ အတည်ပြုမယ်"],
                    ["🔄 ပြန်ပြင်မယ်"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

# =========================================================
# INTERNET RELOCATION SUMMARY
# =========================================================

def relocation_summary(context):

    return f"""🔄 Internet လိုင်းရွှေ့ပြောင်းရန် စာရင်း

အောက်ပါအချက်အလက်များ မှန်/မမှန်
စစ်ဆေးပေးပါခင်ဗျာ။

🆔 Customer ID
{context.user_data.get("relocate_customer_id", "-")}

📍 လက်ရှိလိပ်စာ
{context.user_data.get("relocate_current_address", "-")}

📍 ပြောင်းမဲ့ လိပ်စာ
{context.user_data.get("relocate_new_address", "-")}

📞 ဖုန်းနံပါတ် (၁)
{context.user_data.get("relocate_phone1", "-")}

📞 ဖုန်းနံပါတ် (၂)
{context.user_data.get("relocate_phone2", "မရှိပါ")}

------------------------------

📅 စာရင်းပေးပြီးနောက်
နောက်တစ်နေ့မှာ Survey ဆင်းစစ်ဆေးပေးပါမယ်။
တစ်ပတ်ကြိုတင် စာရင်းပေးသွင်းရပါမယ်။

📦 ပြောင်းမဲ့ လိပ်စာမှာ
Distribution Box ရှိ/မရှိ၊
အသုံးပြုနိုင်တဲ့ Port ရှိ/မရှိ
ဝန်ထမ်းမှ စစ်ဆေးပေးပါမယ်။

Port ရှိပါက လိုင်းရွှေ့ပြောင်းနိုင်ပါတယ်။

💰 လိုင်းရွှေ့ပြောင်းခ
Level-1 — 30,000 Ks
Level-2 — 50,000 Ks

ဘယ် Level ဖြစ်မလဲဆိုတာကို
Survey ဆင်းစစ်ဆေးတဲ့ ဝန်ထမ်းမှ
အတည်ပြုပေးပါမယ်။

🔌 Cable Fee
100m အထိ — အခမဲ့
100m ကျော်ပါက — 1m = 500 Ks

------------------------------

အချက်အလက်အားလုံး မှန်ကန်ပြီး
လိုင်းရွှေ့ပြောင်းရန် သေချာပါက
✅ အတည်ပြုမယ် ကို နှိပ်ပါ။

ပြန်စတင်လိုပါက
🔄 ပြန်ပြင်မယ် ကို နှိပ်ပါ။
"""

# =========================================================
# NEW INSTALLATION START
# =========================================================

async def start_installation_flow(message, update, context):

    # Keep the package selected by the customer
    selected_package = context.user_data.get("install_package")

    reset_flow(context)

    # Restore the selected package after resetting other flow data
    if selected_package:
        context.user_data["install_package"] = selected_package

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

def installation_summary(context, customer=True):

    summary = f"""📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်း

👤 အမည်
{context.user_data.get("install_name", "-")}

📞 အဓိကဖုန်းနံပါတ် (၁)
{context.user_data.get("install_phone", "-")}

📞 အရန်ဖုန်းနံပါတ် (၂)
{context.user_data.get("install_phone2", "မရှိပါ")}

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
"""

    if customer:
        summary += """
------------------------------

အားလုံးမှန်ကန်ပါက
✅ အတည်ပြုမယ် ကို နှိပ်ပါ။

အချက်အလက်တစ်ခုခု ပြန်ပြင်လိုပါက
🔄 ပြန်ပြင်မယ် ကို နှိပ်ပါ။
"""

    return summary

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
    # DEVICE COUNT
    # -----------------------------------------------------

    if flow == "install_device_count":

        try:
            device_count = int(raw.strip())
        except ValueError:
            device_count = 0

        if device_count < 1:
            await send_reply(
                message,
                "❌ ဖုန်းအရေအတွက်ကို ဂဏန်းဖြင့် ပြန်ပို့ပေးပါခင်ဗျာ။",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["install_device_count"] = device_count
        context.user_data["flow"] = "install_package_type"

        extra_note = ""

        if device_count > 25:
            extra_note = """

⚠️ ဖုန်း ၂၅ လုံးထက်ပို အသုံးပြုပါက
တစ်ချိန်တည်း အသုံးပြုသူများလာသည့်အခါ
Internet နှေးခြင်း ဖြစ်နိုင်ပါတယ်။
"""

        await send_reply(
            message,
            f"""📱 အသုံးပြုမည့်ဖုန်း — {device_count} လုံး

📊 အဆင့် ၂ — Package အကြံပြုချက်

| Package | ခန့်မှန်းဖုန်းအရေအတွက် |
|---|---|
| 15 Mbps Home | 4 လုံးအထိ |
| 25 Mbps Home | 7–8 လုံး |
| 35 Mbps Home | 12 လုံးအထိ |
| 50 Mbps Business | 17–18 လုံး |
| 70 Mbps Business | 25 လုံးအထိ |

{extra_note}

အောက်ပါခလုတ်များမှ
အသုံးပြုလိုသည့်အမျိုးအစားကို ရွေးချယ်ပါခင်ဗျာ။
""",
            update,
            ReplyKeyboardMarkup(
                [
                    ["🏠 အိမ်သုံး"],
                    ["🏢 လုပ်ငန်းသုံး"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # PACKAGE TYPE SELECTION
    # -----------------------------------------------------

    if flow == "install_package_type":

        if raw == "🏠 အိမ်သုံး":

            context.user_data["flow"] = "install_home_speed"

            await send_reply(
                message,
                """🏠 Home Package ရွေးချယ်ခြင်း

အသုံးပြုလိုသည့် Internet Speed ကို
ရွေးချယ်ပေးပါခင်ဗျာ။""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["15 Mbps"],
                        ["25 Mbps"],
                        ["35 Mbps"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        elif raw == "🏢 လုပ်ငန်းသုံး":

            context.user_data["flow"] = "install_business_speed"

            await send_reply(
                message,
                """🏢 Business Package ရွေးချယ်ခြင်း

အသုံးပြုလိုသည့် Internet Speed ကို
ရွေးချယ်ပေးပါခင်ဗျာ။""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["50 Mbps"],
                        ["70 Mbps"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        else:
            await send_reply(
                message,
                "Home သို့မဟုတ် Business ကို ရွေးချယ်ပေးပါခင်ဗျာ။",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["🏠 Home"],
                        ["🏢 Business"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

    # -----------------------------------------------------
    # HOME SPEED SELECTION
    # -----------------------------------------------------

    speed = None

    if flow == "install_home_speed":

        home_packages = {
            "15 Mbps": "15",
            "25 Mbps": "25",
            "35 Mbps": "35",
        }

        if raw not in home_packages:
            await send_reply(
                message,
                "15 Mbps၊ 25 Mbps သို့မဟုတ် 35 Mbps ကို ရွေးချယ်ပါခင်ဗျာ။",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["15 Mbps"],
                        ["25 Mbps"],
                        ["35 Mbps"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        speed = home_packages[raw]

    # -----------------------------------------------------
    # BUSINESS SPEED SELECTION
    # -----------------------------------------------------

    elif flow == "install_business_speed":

        business_packages = {
            "50 Mbps": "50",
            "70 Mbps": "70",
        }

        if raw not in business_packages:
            await send_reply(
                message,
                "50 Mbps သို့မဟုတ် 70 Mbps ကို ရွေးချယ်ပါခင်ဗျာ။",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["50 Mbps"],
                        ["70 Mbps"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        speed = business_packages[raw]

    # -----------------------------------------------------
    # PACKAGE PRICE CONFIRMATION
    # -----------------------------------------------------

    if speed is not None:

        kind, speed_text, device_fee, monthly_fee, total = (
            PACKAGES[speed]
        )

        context.user_data["install_package"] = (
            f"{speed_text} {kind}"
        )

        await send_reply(
            message,
            f"""✅ Package ရွေးချယ်ပြီးပါပြီ။

📦 {speed_text} {kind}

🔹 စက်တန်ဖိုး — {device_fee:,} Ks
🔹 ပထမလ လစဉ်ကြေး — {monthly_fee:,} Ks
🔹 စတင်တပ်ဆင်ခ — {total:,} Ks

ယခု လိုင်းသစ်တပ်ဆင်ရန်
စာရင်းပေးသွင်းမှုကို ဆက်လက်လုပ်ဆောင်ပါမယ်။
""",
            update,
        )

        await start_installation_flow(
            message,
            update,
            context,
        )
        return

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
09123456789
+959123456789

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
        context.user_data["flow"] = "install_phone2"

        await send_reply(
            message,
            """✅ ပထမဖုန်းနံပါတ် ရရှိပါပြီ။

📞 အရန်ဖုန်းနံပါတ် (၂) ကိုလည်း
ထပ်မံပေးပို့ပေးပါခင်ဗျာ။

ပထမဖုန်းနံပါတ်ကို ဆက်သွယ်မရပါက
ဒီနံပါတ်မှတစ်ဆင့် ဆက်သွယ်နိုင်ရန် ဖြစ်ပါတယ်။

အရန်ဖုန်းနံပါတ် မရှိပါက
မရှိပါ ဟု ရိုက်ပို့နိုင်ပါတယ်။
""",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # -----------------------------------------------------
    # SECOND PHONE
    # -----------------------------------------------------

    if flow == "install_phone2":

        phone2 = raw.strip().replace(" ", "").replace("-", "")

        if phone2 != "မရှိပါ" and not re.fullmatch(
            r"(09\d{7,9}|\+959\d{7,9})",
            phone2,
        ):

            await send_reply(
                message,
                """❌ ဖုန်းနံပါတ်ပုံစံ မမှန်သေးပါဘူး။

ဥပမာ —
09123456789
+959123456789

အရန်ဖုန်းနံပါတ် မရှိပါက
မရှိပါ ဟု ရိုက်ပို့နိုင်ပါတယ်။
""",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["install_phone2"] = phone2
        context.user_data["flow"] = "install_address"

        await send_reply(
            message,
            """✅ ဖုန်းနံပါတ်များ ရရှိပါပြီ။

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

            # ADMIN REPORT - SHORT VERSION
            admin_report = f"""📝 လိုင်းသစ်တပ်ဆင်ရန် လျှောက်လွှာအသစ်

👤 အမည်
{context.user_data.get("install_name", "-")}

📞 အဓိကဖုန်းနံပါတ် (၁)
{context.user_data.get("install_phone", "-")}

📞 အရန်ဖုန်းနံပါတ် (၂)
{context.user_data.get("install_phone2", "မရှိပါ")}

📍 တပ်ဆင်မည့်နေရာ
{context.user_data.get("install_address", "-")}

📦 Package
{context.user_data.get("install_package", "-")}

📝 အခြားမှတ်ချက်
{context.user_data.get("install_note", "-")}
"""

            await notify_admin(context, admin_report)

            # RESET CUSTOMER FLOW
            reset_flow(context)

            # CUSTOMER THANK-YOU MESSAGE ONLY
            await send_reply(
                message,
                """✅ လိုင်းသစ်တပ်ဆင်ရန်
စာရင်းပေးသွင်းမှုကို အတည်ပြုပြီးပါပြီ။

📅 တပ်ဆင်ချိန်
ဒီနေ့ စာရင်းပေးပြီးပါက
မနက်ဖြန် Survey ဆင်းစစ်ဆေးပေးပါမယ်။

Survey ပြီးနောက် ၃ ရက်အတွင်း
တပ်ဆင်ပေးပါမယ်။

🙏 ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။

📞 Customer Support
09-777719577

လိုင်းသစ်တပ်ဆင်ရန် အသေးစိတ်
ဆက်သွယ်မေးမြန်းလိုပါက
လိုင်းခွဲနံပါတ် (1) Customer Service (ဝန်ဆောင်မှု) နှင့်
လိုင်းခွဲနံပါတ် (3) New Installation (လိုင်းသစ်တပ်ဆင်ခြင်း) တို့ကို
ခေါ်ဆိုပြီးလည်း စာရင်းပေးသွင်းနိုင်ပါတယ်ခင်ဗျာ။ 🙏

ဒီစာရင်းကို Support Team မှ
ဆက်လက်စစ်ဆေးဆောင်ရွက်ပေးပါမယ်။

Ultra Net KAK WiFi Internet Service Provider
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
တစ်ခုကို ရွေးချယ်ပေးပါခင်ဗျာ။""",
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

    context.user_data["flow"] = "speed_apps"
    context.user_data["speed_apps"] = []

    await send_reply(
        message,
        """🐌 Internet နှေးနေတဲ့အခြေအနေကို
တစ်ဆင့်ချင်း စစ်ဆေးပေးပါမယ်ခင်ဗျာ။ 🙏

📱 ဘယ် App / Service တွေမှာ
Internet နှေးနေတာလဲ?

အောက်က သက်ဆိုင်ရာ App တွေကို ရွေးပေးပါ။
ပြီးရင် “✅ ရွေးပြီးပါပြီ” ကို နှိပ်ပေးပါ။

တစ်ခုထက်ပိုပြီး ရွေးနိုင်ပါတယ်ခင်ဗျာ။""",
        update,
        ReplyKeyboardMarkup(
            [
                ["▶️ YouTube", "🎵 TikTok"],
                ["📘 Facebook", "💬 Viber"],
                ["🔎 Google / Website", "🎮 Game"],
                ["📱 App အားလုံး"],
                ["✅ ရွေးပြီးပါပြီ"],
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
        wifi_ssid_menu(),
    )

# =========================================================
# WIFI SSID MENU
# =========================================================

def wifi_ssid_menu():
    return ReplyKeyboardMarkup(
        [
            ["🟢 တွေ့ပါတယ်"],
            ["🔴 မတွေ့ပါဘူး"],
            ["❓ မသိပါဘူး"],
            ["🔙 Main Menu"],
        ],
        resize_keyboard=True,
    )

# =========================================================
# WIFI NAME RECHECK MENU
# =========================================================

def wifi_name_recheck_menu():
    return ReplyKeyboardMarkup(
        [
            ["🟢 ပေါ်လာပါပြီ"],
            ["🔴 မပေါ်သေးပါဘူး"],
            ["🔙 Main Menu"],
        ],
        resize_keyboard=True,
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
        router_power_menu(),
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

အခြား App တွေမှာ Internet ပုံမှန်ရပါသလား?
""",
        update,
        ReplyKeyboardMarkup(
            [
                ["🟢 အခြား App တွေ ရပါတယ်"],
                ["🔴 အခြား App တွေလည်း မရပါဘူး"],
                ["❓ မသိပါဘူး"],
                ["🔙 Main Menu"],
            ],
            resize_keyboard=True,
        ),
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
        if ("နီ" in text and "မနီ" not in text) or "red" in text:
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

ဘယ်အခြေအနေပါလဲ?""",
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

        
        
    if flow == "los":

        if "နီနေဆဲ" in text:
            await send_complaint_report(
                update,
                context,
                "LOS မီးနီနေဆဲ",
                "Fiber Signal ပြဿနာ ဖြစ်နိုင်သည်။ Customer ကို Line 1 မှ ဆက်သွယ်စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """🔴 LOS မီး ဆက်နီနေသေးပါက
Fiber Signal ပြဿနာ ဖြစ်နိုင်ပါတယ်။

Support Team မှ စစ်ဆေးပေးရန်
လိုအပ်နိုင်ပါတယ်ခင်ဗျာ။

📞 Customer Support
09-777719577

အသေးစိတ် ဆက်သွယ်မေးမြန်းလိုပါက
လိုင်းခွဲနံပါတ် (1) Customer Service ကို
ခေါ်ဆိုပေးပါခင်ဗျာ။ 🙏

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
            reset_flow(context)

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

LOS မီးက ONU / Router ပေါ်မှာ
🔴 LOS ဆိုတဲ့စာတန်းနားက မီးပါ။

မီးနီနေပါက Fiber Signal ပြဿနာ
ဖြစ်နိုင်ပါတယ်။

မသေချာသေးပါက
📞 Customer Support
09-777719577

လိုင်းခွဲနံပါတ် (1) Customer Service ကို
ခေါ်ဆိုပေးပါခင်ဗျာ။ 🙏
""",
                update,
                menu(),
            )
            return


    if flow == "los_recovered":

        if "မရ" in text:
            await send_complaint_report(
                update,
                context,
                "LOS မီးပြန်ပျောက်သော်လည်း Internet မရခြင်း",
                "LOS မီးပြန်ပျောက်သွားသော်လည်း Internet မရသေးပါ။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """နားလည်ပါတယ်ခင်ဗျာ။ 🙏

LOS မီးပြန်ပျောက်သွားပေမယ့်
Internet မရသေးတဲ့အတွက်
Support Team ထံ Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )

        else:
            reset_flow(context)

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

        answer = normalize(text)

        if "mainmenu" in answer or "🔙mainmenu" in answer:
            reset_flow(context)
            await send_reply(message, "Main Menu သို့ ပြန်သွားပါပြီ။", update, menu())
            return

        if "မသိ" in text:

            await send_complaint_report(
                update,
                context,
                "Router / ONU Power မီး",
                "Customer သည် Power မီး လင်း/မလင်း အခြေအနေကို မသိပါ။ Support Team မှ ဆက်သွယ်စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

Router / ONU ရဲ့ Power မီးက
များသောအားဖြင့် ⚡ Power ဆိုတဲ့စာတန်းနားမှာ ရှိပါတယ်။

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

            context.user_data["flow"] = "router_power_check"

            await send_reply(
                message,
                """🔌 Router / ONU ရဲ့ Power မီး မလင်းပါက—

1️⃣ Power Adapter ကို သေချာချိတ်ထားပါ။
2️⃣ မီးပလပ် / Socket အလုပ်လုပ်/မလုပ် စစ်ပါ။
3️⃣ Adapter ကို သေချာပြန်ချိတ်ပါ။

⚠️ RESET ခလုတ်ကို မနှိပ်ပါနဲ့။

အခု Power မီး ပြန်လင်းလာပါပြီလား?
""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["🟢 ပြန်လင်းလာပါပြီ"],
                        ["🔴 မလင်းသေးပါဘူး"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        
        if "လင်းပါတယ်" in text:

            context.user_data["flow"] = "router_lights"

            await send_reply(
                message,
                """🟢 Power မီး လင်းနေပါတယ်ခင်ဗျာ။ 🙏

Power မီးက ပုံမှန်လင်းနေတယ်ဆိုရင်
အခု PON / LOS မီးအခြေအနေကို
ဆက်စစ်ကြည့်ပေးပါမယ်။

🔴 LOS နီနေပါသလား?
""",
                update,
                yes_no_menu(),
            )
            return

        context.user_data["flow"] = "router_lights"

        await send_reply(
            message,
            """🟢 Power မီးလင်းနေပါက
PON / LOS မီးကို ဆက်စစ်ပေးပါမယ်။

🔴 LOS နီနေပါသလား?
""",
            update,
            yes_no_menu(),
        )
        return


    if flow == "router_power_check":

        answer = normalize(text)

        if "mainmenu" in answer or "🔙mainmenu" in answer:
            reset_flow(context)
            await send_reply(message, "Main Menu သို့ ပြန်သွားပါပြီ။", update, menu())
            return

        if "ပြန်လင်း" in text and "မလင်း" not in text:

            await send_complaint_report(
                update,
                context,
                "Router / ONU Power မီး",
                "Customer အဖြေအရ Power မီး ပြန်လင်းလာပါပြီ။ PON / LOS မီးအခြေအနေ ဆက်လက်စစ်ဆေးရန် Report ပို့ထားသည်။"
            )

            context.user_data["flow"] = "router_lights"

            await send_reply(
                message,
                """🟢 Power မီး ပြန်လင်းလာပါပြီခင်ဗျာ။ 🙏

အခု PON / LOS မီးအခြေအနေကို
ဆက်စစ်ကြည့်ပေးပါ။

🔴 LOS နီနေပါသလား?
""",
                update,
                yes_no_menu(),
            )
            return

        if "မလင်း" in text or "မသေး" in text:

            await send_complaint_report(
                update,
                context,
                "Router / ONU Power မီးမလင်းခြင်း",
                "Power Adapter၊ Power Socket နှင့် ချိတ်ဆက်မှုကို စစ်ဆေးပြီးနောက် Power မီး မလင်းသေးပါ။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """🔴 Power မီး မလင်းသေးတဲ့အတွက်
Support Team ထံ Report ပို့ပေးထားပါတယ်။

⚠️ RESET ခလုတ်ကို မနှိပ်ပါနဲ့။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )
            return

    if flow == "router_lights":

        if "မသိ" in text:

            await send_complaint_report(
                update,
                context,
                "Router / ONU မီးအခြေအနေ",
                "Customer သည် LOS မီးအခြေအနေကို မသိပါ။ "
                "Router / ONU မီးများ ပုံမှန်ဖြစ်သော်လည်း Internet မရကြောင်း "
                "Support Team မှ ဆက်သွယ်စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

Router / ONU မီးအခြေအနေကို
အဝေးမှ သေချာမစစ်ဆေးနိုင်ပါက
Support Team ထံ တင်ပြပေးထားပါတယ်။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

        if "မနီ" in text:

            await send_complaint_report(
                update,
                context,
                "Router / ONU မီးပုံမှန်ဖြစ်သော်လည်း Internet မရခြင်း",
                "Customer အဖြေအရ LOS မီး မနီပါ။ "
                "Router / ONU မီးများ ပုံမှန်ဖြစ်သော်လည်း Internet မရပါ။ "
                "Support Team မှ လိုင်းအခြေအနေ၊ WAN ချိတ်ဆက်မှုနှင့် "
                "Internet Service အခြေအနေကို ဆက်လက်စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """ဟုတ်ကဲ့ပါခင်ဗျာ။ 🙏

Router / ONU မီးများ ပုံမှန်ဖြစ်ပြီး
LOS မီးလည်း မနီပါဘူးဆိုပေမယ့်
Internet မရသေးတဲ့ပြဿနာကို
Support Team ထံ တင်ပြပေးထားပါတယ်။

🛠️ Support Team မှ လိုင်းအခြေအနေကို
ဆက်လက်စစ်ဆေးပေးပါမယ်။

⚠️ Router / ONU ကို RESET မလုပ်ပါနဲ့။

📞 Customer Support — 09-777719577

ကျေးဇူးတင်ပါတယ်။
Ultra Net KAK WiFi Internet Service Provider
""",
                update,
                menu(),
            )
            return

        if "နီ" in text:

            await start_los_flow(message, update, context)
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
📞 Customer Support — 09-777719577
ကို ဆက်သွယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        if any(
            x in text
            for x in [
                "phone", "laptop", "computer", "tv",
                "ဖုန်း", "လက်ပ်တော့", "ကွန်ပျူတာ", "တီဗီ"
            ]
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
""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["🟢 ရပါပြီ"],
                        ["🔴 မရသေးပါဘူး"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

    if flow == "single_device_result":

        if "mainmenu" in normalize(text):
            reset_flow(context)

            await send_reply(
                message,
                "Main Menu သို့ ပြန်သွားပါပြီ။",
                update,
                menu(),
            )
            return

        if "ရပါ" in text and "မရ" not in text:

            reset_flow(context)

            await send_reply(
                message,
                """🟢 အဆင်ပြေပါပြီခင်ဗျာ။ 🙏

WiFi ကို ပြန်ချိတ်ပြီး Internet ရပြီဆိုရင်
လက်ရှိ Device Connection ဘက်က
ပြဿနာဖြစ်နိုင်ပါတယ်။

နောက်ထပ် အကူအညီလိုပါက
Menu မှ ပြန်ရွေးချယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        if "မရ" in text:

            await send_complaint_report(
                update,
                context,
                "Device တစ်လုံးတည်း Internet မရ",
                "WiFi ပြန်ချိတ်ပြီးသော်လည်း Internet မရသေးပါ။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """နားလည်ပါတယ်ခင်ဗျာ။ 🙏

Device တစ်လုံးတည်းမှာ
Internet မရသေးတဲ့အတွက်
Support Team ထံ Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )
            return

    # =====================================================
    # NEW INTERNET SPEED COMPLAINT FLOW
    # =====================================================

    raw = message.text.strip()

    # APP SELECTION
    if flow == "speed_apps":

        app_options = [
            "▶️ YouTube",
            "🎵 TikTok",
            "📘 Facebook",
            "💬 Viber",
            "🔎 Google / Website",
            "🎮 Game",
            "📱 App အားလုံး",
        ]

        selected = context.user_data.get("speed_apps", [])

        if raw in app_options:

            if raw == "📱 App အားလုံး":
                selected = ["📱 App အားလုံး"]
            else:
                selected = [
                    item for item in selected
                    if item != "📱 App အားလုံး"
                ]

                if raw in selected:
                    selected.remove(raw)
                else:
                    selected.append(raw)

            context.user_data["speed_apps"] = selected

            selected_text = (
                "\n".join(selected)
                if selected
                else "မရွေးရသေးပါ"
            )

            await send_reply(
                message,
                "📱 ရွေးထားသော App / Service များ\n\n"
                f"{selected_text}\n\n"
                "နောက်ထပ် App တွေကိုလည်း ရွေးနိုင်ပါတယ်။\n"
                "ရွေးချယ်ပြီးပါက “✅ ရွေးပြီးပါပြီ” ကို နှိပ်ပါ။",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["▶️ YouTube", "🎵 TikTok"],
                        ["📘 Facebook", "💬 Viber"],
                        ["🔎 Google / Website", "🎮 Game"],
                        ["📱 App အားလုံး"],
                        ["✅ ရွေးပြီးပါပြီ"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        if raw == "✅ ရွေးပြီးပါပြီ":

            if not selected:
                await send_reply(
                    message,
                    "❗ App / Service အနည်းဆုံးတစ်ခု ရွေးပေးပါခင်ဗျာ။",
                    update,
                    ReplyKeyboardMarkup(
                        [
                            ["▶️ YouTube", "🎵 TikTok"],
                            ["📘 Facebook", "💬 Viber"],
                            ["🔎 Google / Website", "🎮 Game"],
                            ["📱 App အားလုံး"],
                            ["✅ ရွေးပြီးပါပြီ"],
                            ["🔙 Main Menu"],
                        ],
                        resize_keyboard=True,
                    ),
                )
                return

            context.user_data["flow"] = "speed_time"

            await send_reply(
                message,
                """⏰ ဘယ်အချိန်တွေမှာ Internet နှေးနေတာလဲခင်ဗျာ?

အောက်က သက်ဆိုင်ရာအချိန်ကို ရွေးပေးပါ။""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["⏱️ အချိန်တိုင်း နှေးပါတယ်"],
                        ["🌅 မနက်ပိုင်း"],
                        ["☀️ နေ့လယ်ပိုင်း"],
                        ["🌇 ညနေပိုင်း"],
                        ["🌙 ညပိုင်း"],
                        ["🔄 တစ်ခါတလေမှ နှေးပါတယ်"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        await send_reply(
            message,
            "App / Service ကို ရွေးပါ၊ ပြီးရင် “✅ ရွေးပြီးပါပြီ” ကို နှိပ်ပါ။",
            update,
            ReplyKeyboardMarkup(
                [
                    ["▶️ YouTube", "🎵 TikTok"],
                    ["📘 Facebook", "💬 Viber"],
                    ["🔎 Google / Website", "🎮 Game"],
                    ["📱 App အားလုံး"],
                    ["✅ ရွေးပြီးပါပြီ"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # TIME SELECTION
    if flow == "speed_time":

        time_options = [
            "⏱️ အချိန်တိုင်း နှေးပါတယ်",
            "🌅 မနက်ပိုင်း",
            "☀️ နေ့လယ်ပိုင်း",
            "🌇 ညနေပိုင်း",
            "🌙 ညပိုင်း",
            "🔄 တစ်ခါတလေမှ နှေးပါတယ်",
        ]

        if raw not in time_options:
            await send_reply(
                message,
                "အောက်က အချိန်ရွေးချယ်မှုတွေထဲက တစ်ခုကို ရွေးပေးပါခင်ဗျာ။",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["⏱️ အချိန်တိုင်း နှေးပါတယ်"],
                        ["🌅 မနက်ပိုင်း"],
                        ["☀️ နေ့လယ်ပိုင်း"],
                        ["🌇 ညနေပိုင်း"],
                        ["🌙 ညပိုင်း"],
                        ["🔄 တစ်ခါတလေမှ နှေးပါတယ်"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["speed_time"] = raw
        context.user_data["flow"] = "speed_customer_id"

        await send_reply(
            message,
            """🆔 Customer ID ကို ပို့ပေးပါခင်ဗျာ။

ဥပမာ — KAKMWD-1234567

Customer ID မသိပါက “❓ မသိပါဘူး” ကို နှိပ်ပြီး ဆက်လုပ်နိုင်ပါတယ်။""",
            update,
            ReplyKeyboardMarkup(
                [
                    ["❓ မသိပါဘူး"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # CUSTOMER ID
    if flow == "speed_customer_id":

        customer_id = raw.strip().upper()

        if "မသိ" in raw:
            context.user_data["speed_customer_id"] = "မသိပါ"

        elif (
            customer_id.startswith("KAKMWD-")
            and len(customer_id[7:]) == 7
            and customer_id[7:].isdigit()
        ):
            context.user_data["speed_customer_id"] = customer_id

        else:
            await send_reply(
                message,
                "❌ Customer ID ပုံစံ မမှန်ပါခင်ဗျာ။\n\n"
                "ဥပမာ — KAKMWD-1234567\n"
                "မသိပါက “❓ မသိပါဘူး” ကို နှိပ်ပါ။",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["❓ မသိပါဘူး"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["flow"] = "speed_phone"

        await send_reply(
            message,
            "📞 ဆက်သွယ်နိုင်မယ့် ဖုန်းနံပါတ်ကို ပို့ပေးပါခင်ဗျာ။\n\n"
            "ဥပမာ — 09123456789",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    # PHONE NUMBER
    if flow == "speed_phone":

        phone = raw.strip()

        if not re.fullmatch(r"09\d{7,9}", phone):
            await send_reply(
                message,
                "❌ ဖုန်းနံပါတ်ပုံစံ မမှန်ပါ။\n"
                "09 နဲ့စတဲ့ မြန်မာဖုန်းနံပါတ်ကို ပြန်ပို့ပေးပါ။\n"
                "ဥပမာ — 09123456789",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["speed_phone"] = phone
        context.user_data["flow"] = "speed_details"

        await send_reply(
            message,
            """📝 Internet နှေးတဲ့ပြဿနာနဲ့ ပတ်သက်ပြီး
ထပ်မံပြောပြချင်တာရှိပါက ရေးပို့ပေးနိုင်ပါတယ်။

ဥပမာ — ဗီဒီယိုဖွင့်ရင် အမြဲ Buffering ဖြစ်တယ်။

ထပ်ဖြည့်စရာမရှိပါက “မရှိပါ” လို့ ပို့ပေးပါ။""",
            update,
            ReplyKeyboardMarkup(
                [
                    ["မရှိပါ"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    # SUBMIT SPEED COMPLAINT TO ADMIN
    if flow == "speed_details":

        extra_details = (
            "မရှိပါ"
            if raw.strip() == "မရှိပါ"
            else raw.strip()
        )

        user = update.effective_user

        customer_id = context.user_data.get(
            "speed_customer_id",
            "မသိပါ",
        )
        phone = context.user_data.get(
            "speed_phone",
            "မရှိပါ",
        )
        apps = context.user_data.get(
            "speed_apps",
            [],
        )
        slow_time = context.user_data.get(
            "speed_time",
            "မသိပါ",
        )

        app_text = "\n".join(apps) if apps else "မသိပါ"

        admin_report = f"""🐌 Internet နှေးခြင်း တိုင်ကြားချက်အသစ်

👤 Telegram အမည်: {user.full_name}
📱 Username: @{user.username or 'မရှိပါ'}
🆔 Telegram ID: {user.id}

🆔 Customer ID: {customer_id}
📞 ဖုန်းနံပါတ်: {phone}

📱 နှေးနေသော App / Service:
{app_text}

⏰ နှေးနေသောအချိန်:
{slow_time}

📝 ထပ်မံဖော်ပြချက်:
{extra_details}

⚠️ Support Team မှ လိုင်းအခြေအနေကို စစ်ဆေးပေးရန်။
"""

        await notify_admin(context, admin_report)

        reset_flow(context)

        await send_reply(
            message,
            """ဟုတ်ကဲ့ပါခင်ဗျာ။ 🙏

လူကြီးမင်း ဖြေကြားပေးထားတဲ့ အချက်အလက်များအတွက် ကျေးဇူးတင်ပါတယ်။

လူကြီးမင်းရဲ့ Internet အနှေးပြဿနာကို
လိုင်းစစ်ဆေးရန် Support အဖွဲ့ထံ တင်ပြပေးလိုက်ပါပြီ။
Support အဖွဲ့မှ စစ်ဆေးပေးပါမယ်နော်။

📞 Customer Support — 09-777719577

Internet လိုင်းနှေးခြင်း၊ လိုင်းမကောင်းခြင်းများ ဖြစ်ပေါ်နေပါက
ရုံးချိန်အတွင်း မနက် ၉ နာရီမှ ည ၁၂ နာရီအထိ
အချိန်မရွေး အထက်ပါဖုန်းနံပါတ်သို့ ဆက်သွယ်ပြီး
လိုင်းအခြေအနေကို စစ်ဆေးမေးမြန်းနိုင်ပါတယ်။

ကျေးဇူးတင်ပါတယ်။
Ultra Net KAK WiFi Internet Service Provider
""",
            update,
            menu(),
        )
        return

    # SPEED TEST: Option 1 and Option 4
    if flow == "speed_test":

        speed_type = context.user_data.get(
            "speed_type",
            "Internet နှေးခြင်း",
        )

        if "မသိ" in text:

            result = (
                "Customer သည် Speed Test ကို မစစ်တတ်ပါ။ "
                "Support Team မှ ဆက်သွယ်စစ်ဆေးပေးရန် လိုအပ်သည်။"
            )

        elif "ရပြီးပါပြီ" in text:

            result = (
                "Customer က Speed Test ပြီးကြောင်း အတည်ပြုထားသည်။ "
                "Speed Test ရလဒ်ကို Support Team မှ ဆက်လက်စစ်ဆေးရန်။"
            )

        else:

            result = f"Customer ပေးပို့သော Speed Test ရလဒ်: {text}"

        await send_complaint_report(
            update,
            context,
            speed_type,
            result,
        )

        reset_flow(context)

        await send_reply(
            message,
            """ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။ 🙏

Internet နှေးခြင်းဆိုင်ရာ အချက်အလက်ကို
Support Team ထံ Report ပို့ပေးထားပါတယ်။

လိုအပ်ပါက Support Team မှ
ဆက်သွယ်စစ်ဆေးပေးပါမယ်။

📞 Customer Support
09-777719577
""",
            update,
            menu(),
        )
        return


    # SINGLE DEVICE: Option 2
    if flow == "speed_single_device_result":

        if "မရသေး" in text or "မရ" in text:

            result = (
                "WiFi Disconnect / Connect ပြန်လုပ်ပြီးသော်လည်း "
                "Internet နှေးနေဆဲဖြစ်သည်။"
            )

            response = """နားလည်ပါတယ်ခင်ဗျာ။ 🙏

WiFi ပြန်ချိတ်ပြီးသော်လည်း
Internet နှေးနေသေးတဲ့အတွက်
Support Team ထံ Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
"""

        elif "ရပါ" in text:

            result = (
                "WiFi Disconnect / Connect ပြန်လုပ်ပြီးနောက် "
                "Internet ပုံမှန်ပြန်ဖြစ်သွားသည်။"
            )

            response = """🟢 Internet ပုံမှန်ပြန်ဖြစ်သွားပါပြီခင်ဗျာ။ 🙏

ပြဿနာနှင့် ပြန်လည်စမ်းသပ်ရလဒ်ကို
Support Team ထံ Report ပို့ပေးထားပါတယ်။
"""

        else:
            return

        await send_complaint_report(
            update,
            context,
            "Device တစ်လုံးတည်း Internet နှေးခြင်း",
            result,
        )

        reset_flow(context)

        await send_reply(
            message,
            response,
            update,
            menu(),
        )
        return


    # NIGHT SLOW: Option 3
    if flow == "speed_night":

        await send_complaint_report(
            update,
            context,
            "ညဘက် Internet ပိုနှေးခြင်း",
            f"Customer ပြောသော အချိန်: {text}",
        )

        reset_flow(context)

        await send_reply(
            message,
            """ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။ 🙏

ညဘက် Internet နှေးတဲ့အချိန်ကို
Support Team ထံ Report ပို့ပေးထားပါတယ်။

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

        answer = normalize(text)

        # LOS မီးနီနေသည်
        if normalize("🔴 LOS နီနေပါတယ်") in answer:

            await send_complaint_report(
                update,
                context,
                "Internet ခဏခဏပြတ်ခြင်း",
                "Customer အဖြေအရ LOS မီးနီနေသည်။ RESET မနှိပ်ရန် အသိပေးပြီး Line 1 / Support Team မှ အမြန်စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """🔴 LOS မီးနီနေတယ်ဆိုရင်
Fiber လိုင်းအချက်ပြပြဿနာ ဖြစ်နိုင်ပါတယ်။

⚠️ Router / ONU ပေါ်က RESET ခလုတ်ကို
မနှိပ်ပါနဲ့ခင်ဗျာ။

Support Team ထံ Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

        # LOS မီးနီမဟုတ်ပါ
        if normalize("🟢 LOS မနီပါဘူး") in answer:

            await send_complaint_report(
                update,
                context,
                "Internet ခဏခဏပြတ်ခြင်း",
                "Customer အဖြေအရ LOS မီးနီမဟုတ်သော်လည်း Internet ခဏခဏပြတ်နေသည်။ Router / WiFi / Connection ဘက်ကို ဆက်လက်စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """🟢 LOS မီးနီမဟုတ်ဘဲ Internet
ခဏခဏပြတ်နေတယ်ဆိုရင် Connection
အခြေအနေကို ဆက်လက်စစ်ဆေးဖို့ လိုပါတယ်။

Support Team ထံ Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

        # မီးအခြေအနေ မသိပါ
        if "မသိ" in answer:

            await send_complaint_report(
                update,
                context,
                "Internet ခဏခဏပြတ်ခြင်း",
                "Customer သည် LOS မီးနီ/မနီ အခြေအနေကို မသိပါ။ Support Team မှ ဆက်သွယ်စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """❓ ရပါတယ်ခင်ဗျာ။ 🙏

LOS မီးအခြေအနေ မသေချာတဲ့အတွက်
Support Team ထံ Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

        await send_reply(
            message,
            "အောက်က ခလုတ် ၃ ခုထဲက တစ်ခုကို ရွေးပေးပါခင်ဗျာ။",
            yes_no_menu(),
        )
        return

    if flow == "disconnect_restart":

        if "ဟုတ်" in text:

            await send_complaint_report(
                update,
                context,
                "Internet ခဏခဏပြတ်ခြင်း",
                "Internet ပြန်ရရန် Router / ONU ကို Restart လုပ်ရသည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """🔄 Router / ONU ကို Restart လုပ်မှ
Internet ပြန်ရတယ်ဆိုရင် Connection ဘက်ကို
Support Team မှ ဆက်လက်စစ်ဆေးပေးပါမယ်။

⚠️ RESET ခလုတ်ကို မနှိပ်ပါနဲ့။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )

        else:

            await send_complaint_report(
                update,
                context,
                "Internet ခဏခဏပြတ်ခြင်း",
                "LOS မနီသော်လည်း Internet ခဏခဏပြတ်နေပြီး Router / WiFi ဘက်ကို စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """နားလည်ပါတယ်ခင်ဗျာ။ 🙏

LOS မနီဘဲ Internet ခဏခဏပြတ်နေပါက
WiFi / Router အခြေအနေကို
Support Team မှ ဆက်လက်စစ်ဆေးပေးပါမယ်။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )

        return

    
    if flow == "wifi":

        answer = normalize(text)

        if "မသိ" in answer:

            await send_reply(
                message,
                """ရပါတယ်ခင်ဗျာ။ 🙏

WiFi Name (SSID) ဆိုတာ
ဖုန်းမှာ WiFi ရှာတဲ့အခါ ပေါ်လာတဲ့
WiFi နာမည်ပါ။

ဥပမာ—
Ko Aye Ko XXXXX

အဲဒီနာမည်ကို တွေ့/မတွေ့
ကြည့်ပေးပါခင်ဗျာ။
""",
                update,
                wifi_ssid_menu(),
            )
            return

        if normalize("မတွေ့ပါဘူး") in answer or normalize("မရှိပါဘူး") in answer:

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
                wifi_name_recheck_menu(),
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
                wifi_name_recheck_menu(),
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

        if "ပေါ်လာ" in text and "မပေါ်" not in text:

            reset_flow(context)

            await send_reply(
                message,
                """🟢 WiFi Name ပြန်ပေါ်လာပါပြီဆိုရင်
WiFi Connection ကို ပြန်စမ်းကြည့်နိုင်ပါတယ်။

မရသေးပါက Internet Problem Menu မှ
ပြဿနာကို ထပ်ရွေးချယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )

        else:

            await send_complaint_report(
                update,
                context,
                "WiFi Name မပေါ်ခြင်း",
                "WiFi Name ကို ပြန်ရှာပြီး Router အနီးတွင် စမ်းကြည့်သော်လည်း မပေါ်သေးပါ။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """🔴 WiFi Name မပေါ်သေးတဲ့အတွက်
Support Team ထံ Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
သို့ ဆက်သွယ်ပေးပါခင်ဗျာ။
""",
                update,
                menu(),
            )

        return

    if flow == "wifi_password":

        if "password" in text and "မှား" in text:

            context.user_data["flow"] = "wifi_password_result"

            await send_reply(
                message,
                """🔐 WiFi Password မှားတယ်လို့ ပြပါက—

1️⃣ Password ကို သေချာပြန်စစ်ပါ။
2️⃣ Password ပြန်ထည့်ပြီး Connect လုပ်ပါ။

အခု WiFi ချိတ်ဆက်လို့ ရပါပြီလား?
""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["🟢 ရပါပြီ"],
                        ["🔴 မရသေးပါဘူး"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        if "connecting" in text or "ချိတ်နေ" in text:

            context.user_data["flow"] = "wifi_password_result"

            await send_reply(
                message,
                """📶 WiFi ကို Forget လုပ်ပြီး
Password ပြန်ထည့်ကာ Connect လုပ်ကြည့်ပါ။

အခု WiFi ချိတ်ဆက်လို့ ရပါပြီလား?
""",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["🟢 ရပါပြီ"],
                        ["🔴 မရသေးပါဘူး"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["flow"] = "wifi_password_result"

        await send_reply(
            message,
            """🟢 WiFi ချိတ်ပြီး Internet မရပါက—

WiFi ကို Disconnect လုပ်ပြီး
ပြန် Connect လုပ်ကြည့်ပါ။

Internet ပြန်ရပါပြီလား?
""",
            update,
            ReplyKeyboardMarkup(
                [
                    ["🟢 ရပါပြီ"],
                    ["🔴 မရသေးပါဘူး"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return


    if flow == "wifi_password_result":

        if "ရပါ" in text and "မရ" not in text:

            reset_flow(context)

            await send_reply(
                message,
                """🟢 WiFi ပြန်ချိတ်ဆက်လို့ ရသွားပါပြီခင်ဗျာ။ 🙏

နောက်ထပ်အကူအညီလိုပါက
Menu မှ ပြန်ရွေးချယ်နိုင်ပါတယ်။
""",
                update,
                menu(),
            )
            return

        await send_complaint_report(
            update,
            context,
            "WiFi Password / Connection ပြဿနာ",
            "Password ပြန်စစ်ခြင်း၊ WiFi Forget လုပ်ပြီး ပြန်ချိတ်ခြင်း သို့မဟုတ် Disconnect / Connect လုပ်ခြင်းတို့ ပြုလုပ်ပြီးသော်လည်း မပြေလည်သေးပါ။"
        )

        reset_flow(context)

        await send_reply(
            message,
            """🔴 စမ်းသပ်ပြီးသော်လည်း မပြေလည်သေးတဲ့အတွက်
Support Team ထံ Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
""",
            update,
            menu(),
        )
        return

    if flow == "app":

        answer = normalize(text)

        # UNKNOWN
        if "မသိ" in answer:

            await send_complaint_report(
                update,
                context,
                "Website / App ပြဿနာ",
                "Customer သည် အခြား App များတွင် Internet ရ/မရ မသိပါ။ Support Team မှ ဆက်သွယ်စစ်ဆေးရန် လိုအပ်သည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """❓ နားလည်ပါတယ်ခင်ဗျာ။ 🙏

အခြား App တွေမှာ Internet ရ/မရ
မသေချာတဲ့အတွက် Support Team ထံ
Report ပို့ပေးထားပါတယ်။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

        # OTHER APPS WORK
        if normalize("အခြား App တွေ ရပါတယ်") in answer:

            await send_complaint_report(
                update,
                context,
                "Website / App တစ်ခုတည်း ပြဿနာဖြစ်ခြင်း",
                "Customer အဖြေအရ အခြား App များတွင် Internet ပုံမှန်ရပြီး သက်ဆိုင်ရာ App / Website တစ်ခုတည်းတွင် ပြဿနာဖြစ်နေသည်။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """🟢 အခြား App တွေ ရတယ်ဆိုရင်
Internet လိုင်းတစ်ခုလုံး ပြတ်နေခြင်း
မဟုတ်နိုင်ပါဘူးခင်ဗျာ။

မရတဲ့ App / Website ကို
ပိတ်ပြီး ပြန်ဖွင့်ကြည့်ပါ။
App Update ရှိပါက Update လုပ်ကြည့်ပါ။

မပြေလည်သေးပါက Support Team ထံ
ဆက်သွယ်စစ်ဆေးနိုင်ပါတယ်။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

        # OTHER APPS ALSO DO NOT WORK
        if normalize("အခြား App တွေလည်း မရပါဘူး") in answer:

            await send_complaint_report(
                update,
                context,
                "Website / App ပြဿနာ",
                "Customer အဖြေအရ အခြား App များတွင်လည်း Internet အသုံးပြုမရပါ။"
            )

            reset_flow(context)

            await send_reply(
                message,
                """🔴 အခြား App တွေလည်း မရတဲ့အတွက်
Internet Connection ဘက်ကို
Support Team မှ ဆက်လက်စစ်ဆေးပေးပါမယ်။

Report ပို့ပေးထားပါတယ်ခင်ဗျာ။

📞 Customer Support
09-777719577
""",
                update,
                menu(),
            )
            return

# =========================================================
# MAIN MESSAGE HANDLER
# =========================================================

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user is None:
        return

    message = update.effective_message

    if not message:
        return

    # Group ထဲမှာ Bot က Customer Support အဖြေ မပေးပါ
    if update.effective_chat and update.effective_chat.type in ("group", "supergroup"):
        return

    if not message.text:
        return

    raw = message.text.strip()
    text = normalize(raw)
    
    # =====================================================
    # CUSTOMER WELCOME MESSAGE
    # =====================================================

    greeting_words = {
        "hi",
        "hello",
        "hey",
        "မင်္ဂလာပါ",
        "ဟယ်လို",
        "မေးချင်လို့ပါ",
    }

    if text.casefold() in greeting_words:
        welcome_text = """🙏 မင်္ဂလာပါခင်ဗျာ။ Ultra Net KAK Customer Support မှ ကြိုဆိုပါတယ်။

📌 Bot ကို ဘယ်လိုအသုံးပြုရမလဲ?

အဆင့် (၁) — Telegram Chat ရဲ့ အောက်ခြေမှာရှိတဲ့ Menu ခလုတ်ကို ရှာပြီး နှိပ်ပါ။

အဆင့် (၂) — Menu ထဲမှာ အောက်ပါဝန်ဆောင်မှုများကို တွေ့ရပါမယ်။

1. 📦 Package / Price — အင်တာနက် Package နှင့် ဈေးနှုန်းများ
2. 🛠 Internet Problem — အင်တာနက်ပြဿနာ တင်ပြရန်
3. 💳 Payment — ငွေပေးချေမှုဆိုင်ရာ အချက်အလက်များ
4. 📞 Customer Support — Customer Support အချက်အလက်များ
5. 🪪 Customer ID — Customer ID စစ်ဆေးရန်
6. 👨‍💻 လူနဲ့ဆက်သွယ်မယ် — ဝန်ထမ်းနှင့် ဆက်သွယ်ရန်
7. 📍 ရုံးတည်နေရာ (Location) — ရုံးတည်နေရာ ကြည့်ရန်
8. 🌐 Social Media — လူမှုကွန်ရက်များ ကြည့်ရန်
9. 📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း
10. 📍 WiFi နေရာပြောင်း
11. ♻️ WiFi ပြန်လည်အသုံးပြုရန်

အဆင့် (၃) — အင်တာနက်ပြဿနာများ မေးမြန်းလိုပါက Internet Problem ကို ရွေးချယ်ပါ။

ဥပမာ —
🔴 LOS မီးနီနေခြင်း
📶 Internet လုံးဝမရခြင်း
🐢 Internet နှေးခြင်း
🔌 Internet ခဏခဏပြတ်ခြင်း
📡 WiFi ပြဿနာများ
🔑 WiFi Password ပြောင်းလဲခြင်း

အဆင်မပြေပါက လူနဲ့ဆက်သွယ်မယ် ကို ရွေးချယ်ပြီး ဝန်ထမ်းထံ ဆက်သွယ်နိုင်ပါတယ်ခင်ဗျာ။

📞 Customer Support — 09-777719577

☎️ လူကိုယ်တိုင် ဆက်သွယ်လိုပါက လိုင်းခွဲနံပါတ် (1) — Customer Service ကို ခေါ်ဆိုဆက်သွယ်နိုင်ပါတယ်ခင်ဗျာ။ 🙏

🙏 **Ultra Net- Ko Aye Ko - WiFi ကို အသုံးပြုပေးတဲ့အတွက် ကျေးဇူးအထူးတင်ပါတယ်။**"""

        await send_reply(message, welcome_text, update)
        return

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
    # WIFI PASSWORD CHANGE FLOW
    # =====================================================

    if raw == "🔐 WiFi Password ပြောင်းရန်":
        context.user_data["flow"] = "password_change_customer_id"

        await send_reply(
            message,
            "🔐 WiFi Password ပြောင်းရန်\n\n"
            "🆔 Customer ID ကို ပို့ပေးပါခင်ဗျာ။\n\n"
            "ဥပမာ - KAKMWD-1234567",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    if context.user_data.get("flow") == "password_change_customer_id":
        customer_id = raw.strip().upper()

        if not (
            customer_id.startswith("KAKMWD-")
            and len(customer_id[7:]) == 7
            and customer_id[7:].isdigit()
        ):
            await send_reply(
                message,
                "❌ Customer ID ပုံစံ မမှန်ပါခင်ဗျာ။\n"
                "KAKMWD- နောက်မှာ ဂဏန်း ၇ လုံး ပါရပါမယ်။",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["customer_id"] = customer_id
        context.user_data["flow"] = "password_change_phone"

        await send_reply(
            message,
            "📞 ဆက်သွယ်ရမည့် ဖုန်းနံပါတ်ကို ပို့ပေးပါခင်ဗျာ။",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    if context.user_data.get("flow") == "password_change_phone":
        phone = raw.strip()

        if not (
            phone.startswith("09")
            and phone[2:].isdigit()
            and 9 <= len(phone) <= 11
        ):
            await send_reply(
                message,
                "❌ ဖုန်းနံပါတ် ပုံစံမမှန်ပါခင်ဗျာ။\n"
                "09 နဲ့ စတဲ့ ဖုန်းနံပါတ်ကို ပြန်ပို့ပေးပါ။",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["customer_phone"] = phone
        context.user_data["flow"] = "password_change_type"

        await send_reply(
            message,
            "🔐 ဘယ်လို Password မျိုး ပြောင်းချင်ပါသလဲခင်ဗျာ?",
            update,
            ReplyKeyboardMarkup(
                [
                    ["🔐 ပုံမှန် WiFi Password (အနည်းဆုံး 8 လုံး)"],
                    ["📷 QR Code အတွက် (အနည်းဆုံး 13 လုံး)"],
                    ["🔙 Main Menu"],
                ],
                resize_keyboard=True,
            ),
        )
        return

    if context.user_data.get("flow") == "password_change_type":
        if raw == "🔐 ပုံမှန် WiFi Password (အနည်းဆုံး 8 လုံး)":
            context.user_data["password_min_length"] = 8
            context.user_data["password_type"] = "ပုံမှန် WiFi Password"

        elif raw == "📷 QR Code အတွက် (အနည်းဆုံး 13 လုံး)":
            context.user_data["password_min_length"] = 13
            context.user_data["password_type"] = "QR Code အတွက် WiFi Password"

        else:
            await send_reply(
                message,
                "အပေါ်က Password အမျိုးအစား ၂ မျိုးထဲမှ တစ်ခုကို ရွေးပေးပါခင်ဗျာ။",
                update,
                ReplyKeyboardMarkup(
                    [
                        ["🔐 ပုံမှန် WiFi Password (အနည်းဆုံး 8 လုံး)"],
                        ["📷 QR Code အတွက် (အနည်းဆုံး 13 လုံး)"],
                        ["🔙 Main Menu"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["flow"] = "password_change_new_password"

        await send_reply(
            message,
            f"🔑 ပြောင်းချင်တဲ့ WiFi Password အသစ်ကို ရေးထည့်ပေးပါခင်ဗျာ။\n\n"
            f"အနည်းဆုံး {context.user_data['password_min_length']} လုံး ရှိရပါမယ်။",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return

    if context.user_data.get("flow") == "password_change_new_password":
        new_password = raw.strip()
        min_length = context.user_data.get("password_min_length", 8)

        if len(new_password) < min_length:
            await send_reply(
                message,
                f"❌ Password အရှည် မလုံလောက်ပါခင်ဗျာ။\n"
                f"အနည်းဆုံး {min_length} လုံး ရှိရပါမယ်။\n"
                "Password အသစ်ကို ပြန်ရေးထည့်ပေးပါ။",
                update,
                ReplyKeyboardMarkup(
                    [["🔙 Main Menu"]],
                    resize_keyboard=True,
                ),
            )
            return

        customer_id = context.user_data.get("customer_id", "မရှိပါ")
        phone = context.user_data.get("customer_phone", "မရှိပါ")
        password_type = context.user_data.get("password_type", "WiFi Password")

        await notify_admin(
            context,
            f"""🔐 WiFi Password ပြောင်းရန် တောင်းဆိုမှု

👤 Customer: {update.effective_user.full_name}
🆔 Customer ID: {customer_id}
📞 ဖုန်းနံပါတ်: {phone}
🆔 Telegram ID: {update.effective_user.id}
📱 Username: @{update.effective_user.username or 'မရှိပါ'}

📌 Password အမျိုးအစား: {password_type}
🔑 Password အသစ်: {new_password}

⚠️ Customer ကို ဆက်သွယ်ပြီး တောင်းဆိုချက်ကို ဆောင်ရွက်ပေးပါ။
"""
        )

        reset_flow(context)

        await send_reply(
            message,
            """✅ Password ပြောင်းလဲရန် တောင်းဆိုမှုကို လက်ခံရရှိပါပြီခင်ဗျာ။

ဝန်ဆောင်မှုအဖွဲ့မှ Password ပြောင်းလဲပေးပြီးပါက လူကြီးမင်းထံ ပြန်လည်ဆက်သွယ်ပေးပါမယ်။

ကျေးဇူးတင်ပါတယ်။ 🙏""",
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
    # COMPLAINT PHONE ACTIVE FLOW
    # =====================================================

    if context.user_data.get("flow") == "complaint_phone":
        phone = raw.strip()

        if re.fullmatch(r"09\d{7,9}", phone):
            context.user_data["customer_phone"] = phone
            pending = context.user_data.get("pending_complaint")

            if pending == "🔧 Internet လုံးဝမရ":
                await start_internet_flow(message, update, context)
            elif pending == "🔴 LOS မီးနီ":
                await start_los_flow(message, update, context)
            elif pending == "🐌 Internet နှေး":
                await start_speed_flow(message, update, context)
            elif pending == "🔌 Internet ခဏခဏပြတ်":
                await start_disconnect_flow(message, update, context)
            elif pending == "📶 WiFi ပြဿနာ":
                await start_wifi_flow(message, update, context)
            elif pending == "⚡ Router / ONU ပြဿနာ":
                await start_router_flow(message, update, context)
            elif pending == "📱 Device တစ်လုံးတည်း မရ":
                await start_single_device_flow(message, update, context)
            elif pending == "🌐 Website / App တစ်ခုတည်း မရ":
                await start_app_flow(message, update, context)
            else:
                reset_flow(context)
                await send_reply(
                    message,
                    "ဖုန်းနံပါတ်ကို လက်ခံရရှိပါပြီ။ Main Menu ကနေ ပြန်ရွေးပေးပါခင်ဗျာ။",
                    update,
                    menu(),
                )
            return

        await send_reply(
            message,
            "❌ ဖုန်းနံပါတ်ပုံစံ မမှန်ပါ။\n\n09 နဲ့စတဲ့ မြန်မာဖုန်းနံပါတ်ကို ပြန်ပို့ပေးပါ။\nဥပမာ — 09123456789",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return
    
    # =====================================================
    # INTERNET RELOCATION BUTTON
    # =====================================================

    if raw == "🔄 Internet လိုင်းရွှေ့ရန်":

        await start_relocation_flow(
            message,
            update,
            context,
        )
        return
    
    # =====================================================
    # WIFI RECONNECTION BUTTON
    # =====================================================

    if raw == "♻️ WiFi ပြန်လည်အသုံးပြုရန်":

        await start_reconnection_flow(
            message,
            update,
            context,
        )
        return

    # =====================================================
    # NEW INSTALLATION BUTTON
    # =====================================================

    if raw == "📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း":

        reset_flow(context)

        context.user_data["flow"] = "install_device_count"

        await send_reply(
            message,
            """📝 လိုင်းသစ်တပ်ဆင်ရန် စာရင်းပေးခြင်း

📱 အင်တာနက် အသုံးပြုမည့်
ဖုန်းအရေအတွက် ဘယ်နှစ်လုံးရှိပါသလဲခင်ဗျာ။

ဥပမာ — 4 / 8 / 12 / 18 / 25

အသုံးပြုမည့် ဖုန်းအရေအတွက်ကို
ဂဏန်းဖြင့် ပြန်ပို့ပေးပါခင်ဗျာ။
""",
            update,
            ReplyKeyboardMarkup(
                [["🔙 Main Menu"]],
                resize_keyboard=True,
            ),
        )
        return
    
    # =====================================================
    # WIFI RECONNECTION ACTIVE FLOW
    # =====================================================

    if context.user_data.get("flow", "").startswith("reconnect_"):

        await handle_reconnection_flow(
            message,
            update,
            context,
            raw,
        )
        return
    
    # =====================================================
    # INTERNET RELOCATION ACTIVE FLOW
    # =====================================================

    if context.user_data.get("flow", "").startswith("relocate_"):

        await handle_relocation_flow(
            message,
            update,
            context,
            raw,
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

    complaint_buttons = [
        "🔧 Internet လုံးဝမရ",
        "🔴 LOS မီးနီ",
        "🐌 Internet နှေး",
        "🔌 Internet ခဏခဏပြတ်",
        "📶 WiFi ပြဿနာ",
        "⚡ Router / ONU ပြဿနာ",
        "📱 Device တစ်လုံးတည်း မရ",
        "🌐 Website / App တစ်ခုတည်း မရ",
    ]

    
    if raw in complaint_buttons:
        if raw == "🐌 Internet နှေး":
            context.user_data.pop("pending_complaint", None)
            await start_speed_flow(message, update, context)
        else:
            context.user_data["pending_complaint"] = raw
            await start_customer_id_flow(message, update, context)
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

# =========================================================
# CHANNEL POST WITH CUSTOMER SUPPORT BUTTON
# =========================================================


async def post_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user is None:
        return

    if not ADMIN_CHAT_ID or str(update.effective_user.id) != ADMIN_CHAT_ID:
        await update.effective_message.reply_text(
            "ဒီလုပ်ဆောင်ချက်ကို Admin သာ အသုံးပြုနိုင်ပါတယ်။"
        )
        return

    if not context.args:
        await update.effective_message.reply_text(
            "ကြော်ငြာစာသားကို ထည့်ပေးပါ။\nဥပမာ — /post မင်္ဂလာပါ။ Ultra Net KAK မှ ကြိုဆိုပါတယ်။"
        )
        return

    post_text = update.effective_message.text.partition(" ")[2].strip()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "💬 သိလိုသမျှ မေးရန်",
            url="https://t.me/UltraNetKAKMM_bot"
        )]
    ])

    await context.bot.send_message(
        chat_id="@ultranetkak",
        text=post_text.replace("**", "*"),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await update.effective_message.reply_text(
        "✅ Channel မှာ ကြော်ငြာတင်ပြီးပါပြီ။"
    )

# =========================================================
# AUTOMATIC AD POSTING
# =========================================================

MYANMAR_TZ = timezone(timedelta(hours=6, minutes=30))

AD_TARGETS = [
    "@ultranetkak",
    -1004294645243,
]

AD_MESSAGES = [
    """🌐 Ultra Net KAK WiFi Internet Service Provider

🏠 အိမ်သုံးနှင့် 🏢 လုပ်ငန်းသုံး Internet Package များ ရရှိနိုင်ပါပြီ။

📞 Customer Support: 09-777719577
💬 Telegram: @UltraNetKAKWiFi

📢 Channel: https://t.me/ultranetkak
""",
    """📶 Internet မြန်နှုန်းကောင်းကောင်းနဲ့ ချိတ်ဆက်လိုပါသလား?

Ultra Net KAK မှ အိမ်သုံးနှင့် လုပ်ငန်းသုံး WiFi ဝန်ဆောင်မှုများ ပေးနေပါပြီ။

📞 09-777719577
💬 @UltraNetKAKWiFi
""",
]

AD_INDEX = 0

# =========================================================
# AUTOMATIC AD POSTING
# =========================================================

async def automatic_ad_job(application):
    global AD_INDEX

    if not AD_MESSAGES:
        log.error("AD_MESSAGES is empty.")
        return

    post_text = AD_MESSAGES[AD_INDEX % len(AD_MESSAGES)]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            "💬 သိလိုသမျှ မေးရန်",
            url="https://t.me/UltraNetKAKMM_bot",
        )]
    ])

    success = False

    for target in AD_TARGETS:
        try:
            await application.bot.send_message(
                chat_id=target,
                text=post_text,
                reply_markup=keyboard,
            )

            log.info(
                "Automatic advertisement sent to %s",
                target,
            )
            success = True

        except Exception:
            log.exception(
                "Automatic advertisement failed for %s",
                target,
            )

    if success:
        AD_INDEX = (AD_INDEX + 1) % len(AD_MESSAGES)


async def schedule_next_ad(application):

    while True:
        now = datetime.now(MYANMAR_TZ)

        today_9 = now.replace(
            hour=9,
            minute=0,
            second=0,
            microsecond=0,
        )

        today_17 = now.replace(
            hour=17,
            minute=0,
            second=0,
            microsecond=0,
        )

        if now < today_9:
            next_run = today_9

        elif now < today_17:
            next_run = today_17

        else:
            next_run = today_9 + timedelta(days=1)

        delay = (next_run - now).total_seconds()

        log.info(
            "Next automatic advertisement: %s Myanmar time",
            next_run.strftime("%Y-%m-%d %H:%M:%S"),
        )

        await asyncio.sleep(delay)

        await automatic_ad_job(application)

# =========================================================
# GET TELEGRAM CHAT ID
# =========================================================

async def chatid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat and update.effective_message:
        await update.effective_message.reply_text(
            f"Chat ID: {chat.id}\n"
            f"Chat Type: {chat.type}"
        )

# =========================================================
# CUSTOMER SUPPORT BUTTON FOR DISCUSSION GROUP
# =========================================================

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💬 သိလိုသမျှ မေးရန်",
                url="https://t.me/UltraNetKAKMM_bot"
            )
        ]
    ])

    await update.effective_message.reply_text(
        "မင်္ဂလာပါ။ Ultra Net KAK Customer Support ကို ဆက်သွယ်ရန် အောက်က Button ကို နှိပ်ပါ။",
        reply_markup=keyboard
    )

# =====================================================
# WIFI RECONNECTION START FLOW
# =====================================================

async def start_reconnection_flow(message, update, context):
    reset_flow(context)

    context.user_data["flow"] = "reconnect_duration"

    await send_reply(
        message,
        "♻️ WiFi ပြန်လည်အသုံးပြုရန်\n\n"
        "လိုင်းမသုံးဖြစ်တာ ဘယ်လောက်ကြာပြီလဲခင်ဗျာ?",
        update,
        reply_markup=ReplyKeyboardMarkup(
            [
                ["၁ လ", "၂ လ"],
                ["၃ လ", "၄ လ"],
                ["၅ လ", "၆ လနှင့်အထက်"],
            ],
            resize_keyboard=True,
        ),
    )

# =====================================================
# WIFI RECONNECTION HANDLE FLOW
# =====================================================

async def handle_reconnection_flow(message, update, context, raw):
    flow = context.user_data.get("flow", "")

    if flow == "reconnect_duration":
        durations = {
            "၁ လ": 1,
            "၂ လ": 2,
            "၃ လ": 3,
            "၄ လ": 4,
            "၅ လ": 5,
            "၆ လနှင့်အထက်": 6,
        }

        if raw not in durations:
            await send_reply(
                message,
                "အောက်ပါခလုတ်တွေထဲမှ ရွေးပေးပါခင်ဗျာ။",
                update,
                reply_markup=ReplyKeyboardMarkup(
                    [
                        ["၁ လ", "၂ လ"],
                        ["၃ လ", "၄ လ"],
                        ["၅ လ", "၆ လနှင့်အထက်"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

        context.user_data["reconnect_months"] = durations[raw]
        context.user_data["flow"] = "reconnect_customer_id"

        await send_reply(
            message,
            "🆔 Customer ID ရှိပါသလားခင်ဗျာ?",
            update,
            reply_markup=ReplyKeyboardMarkup(
                [["ရှိပါတယ်", "မရှိတော့ပါ / မသိတော့ပါ"]],
                resize_keyboard=True,
            ),
        )
        return

    if flow == "reconnect_customer_id":
        if raw == "ရှိပါတယ်":
            context.user_data["flow"] = "reconnect_customer_id_input"

            await send_reply(
                message,
                "Customer ID ကို ရိုက်ပေးပါခင်ဗျာ။\n"
                "ဥပမာ — KAKMWD-1234567",
                update,
            )
            return

        if raw == "မရှိတော့ပါ / မသိတော့ပါ":
            context.user_data["reconnect_customer_id"] = (
                "မရှိတော့ပါ / မသိတော့ပါ"
            )
            context.user_data["flow"] = "reconnect_phone"

            await send_reply(
                message,
                "📱 ဆက်သွယ်ရန် ဖုန်းနံပါတ်ကို ပေးပါခင်ဗျာ။",
                update,
            )
            return

        await send_reply(
            message,
            "Customer ID ရှိ/မရှိ ရွေးပေးပါခင်ဗျာ။",
            update,
            reply_markup=ReplyKeyboardMarkup(
                [["ရှိပါတယ်", "မရှိတော့ပါ / မသိတော့ပါ"]],
                resize_keyboard=True,
            ),
        )
        return

    if flow == "reconnect_customer_id_input":
        customer_id = raw.strip().upper()

        if not customer_id.startswith("KAKMWD-"):
            await send_reply(
                message,
                "Customer ID ပုံစံ မမှန်သေးပါခင်ဗျာ။\n"
                "ဥပမာ — KAKMWD-1234567",
                update,
            )
            return

        suffix = customer_id.removeprefix("KAKMWD-")

        if not suffix.isdigit() or len(suffix) != 7:
            await send_reply(
                message,
                "Customer ID ပုံစံ မမှန်သေးပါခင်ဗျာ။\n"
                "ဥပမာ — KAKMWD-1234567",
                update,
            )
            return

        context.user_data["reconnect_customer_id"] = customer_id
        context.user_data["flow"] = "reconnect_phone"

        await send_reply(
            message,
            "📱 ဆက်သွယ်ရန် ဖုန်းနံပါတ်ကို ပေးပါခင်ဗျာ။",
            update,
        )
        return

    if flow == "reconnect_phone":
        if len(raw.strip()) < 7:
            await send_reply(
                message,
                "ဖုန်းနံပါတ်ကို ပြန်စစ်ပြီး ပေးပါခင်ဗျာ။",
                update,
            )
            return

        context.user_data["reconnect_phone"] = raw.strip()
        months = context.user_data.get("reconnect_months", 0)

        if months <= 2:
            context.user_data["flow"] = "reconnect_confirm"

            await send_reply(
                message,
                "၆၀ ရက်အတွင်း ပြန်လည်အသုံးပြုရန် "
                "ပုံမှန် WiFi လစဉ်ကြေး တစ်လစာ ပေးသွင်းရပါမယ်ခင်ဗျာ။\n\n"
                "ပြန်လည်အသုံးပြုရန် အတည်ပြုပါသလား?",
                update,
                reply_markup=ReplyKeyboardMarkup(
                    [["✅ ပြန်သုံးမယ်"], ["❌ မလုပ်တော့ပါ"]],
                    resize_keyboard=True,
                ),
            )
        else:
            context.user_data["flow"] = "reconnect_light"

            await send_reply(
                message,
                "စက်ကို မီးဖွင့်ပြီး မီးအခြေအနေ စစ်ပေးပါခင်ဗျာ။\n\n"
                "မီးသုံးလုံး ပုံမှန်လင်းနေပါသလား?",
                update,
                reply_markup=ReplyKeyboardMarkup(
                    [
                        ["💡 မီးသုံးလုံး ပုံမှန်လင်းတယ်"],
                        ["🔴 ပုံမှန်မလင်းဘူး / မီးနီနေတယ်"],
                    ],
                    resize_keyboard=True,
                ),
            )
        return

    if flow == "reconnect_light":
        if raw == "💡 မီးသုံးလုံး ပုံမှန်လင်းတယ်":
            context.user_data["reconnect_light_status"] = (
                "မီးသုံးလုံး ပုံမှန်လင်းသည်"
            )

            context.user_data["flow"] = "reconnect_confirm"

            await send_reply(
                message,
                "ရက် ၆၀ ကျော်သွားသောကြောင့် WiFi ပြန်သုံးရန် "
                "လစဉ်ကြေး ၃ လစာ ကြိုတင်ပေးသွင်းရပါမယ်ခင်ဗျာ။\n\n"
                "ဒီ ၃ လစာဟာ အရင်မသုံးဖြစ်ခဲ့တဲ့ လတွေအတွက် မဟုတ်ပါဘူး။ "
                "ဝန်ဆောင်မှု ပြန်စတင်တဲ့နေ့မှစပြီး ၃ လစာတွက်မှာဖြစ်ပါတယ်။\n\n"
                "ပြန်လည်အသုံးပြုရန် အတည်ပြုပါသလား?",
                update,
                reply_markup=ReplyKeyboardMarkup(
                    [["✅ ပြန်သုံးမယ်"], ["❌ မလုပ်တော့ပါ"]],
                    resize_keyboard=True,
                ),
            )
            return

        elif raw == "🔴 ပုံမှန်မလင်းဘူး / မီးနီနေတယ်":
            context.user_data["reconnect_light_status"] = (
                "မီးပုံမှန်မလင်း / မီးနီနေသည်"
            )

            context.user_data["flow"] = "reconnect_confirm"

            await send_reply(
                message,
                "🔧 ONU / Router မီးပုံမှန်မလင်းဘူး၊ မီးနီနေတယ်ဆိုရင် "
                "ရုံးဘက်မှ ဆားဗစ်ဝန်ထမ်း လွှတ်ပေးဖို့ လိုအပ်ပါတယ်ခင်ဗျာ။\n\n"
                "💰 WiFi ပြန်သုံးရန် ရက် ၆၀ ကျော်သွားသောကြောင့် "
                "လစဉ်ကြေး ၃ လစာ ကြိုတင်ပေးသွင်းရပါမယ်။\n\n"
                "ဒီ ၃ လစာဟာ အရင်မသုံးဖြစ်ခဲ့တဲ့ လတွေအတွက် မဟုတ်ပါဘူး။ "
                "ဝန်ဆောင်မှု ပြန်စတင်တဲ့နေ့မှစပြီး ၃ လစာတွက်မှာဖြစ်ပါတယ်။\n\n"
                "လစဉ်ကြေးကို ဆားဗစ်ဝန်ထမ်းထံမှာလည်း "
                "ပေးသွင်းနိုင်ပါတယ်ခင်ဗျာ။\n\n"
                "ပြန်လည်အသုံးပြုရန် အတည်ပြုပါသလား?",
                update,
                reply_markup=ReplyKeyboardMarkup(
                    [["✅ ပြန်သုံးမယ်"], ["❌ မလုပ်တော့ပါ"]],
                    resize_keyboard=True,
                ),
            )
            return

        else:
            await send_reply(
                message,
                "အောက်ပါခလုတ်နှစ်ခုထဲမှ ရွေးပေးပါခင်ဗျာ။",
                update,
                reply_markup=ReplyKeyboardMarkup(
                    [
                        ["💡 မီးသုံးလုံး ပုံမှန်လင်းတယ်"],
                        ["🔴 ပုံမှန်မလင်းဘူး / မီးနီနေတယ်"],
                    ],
                    resize_keyboard=True,
                ),
            )
            return

    if flow == "reconnect_confirm":
        if raw == "❌ မလုပ်တော့ပါ":
            reset_flow(context)

            for key in (
                "reconnect_months",
                "reconnect_customer_id",
                "reconnect_phone",
                "reconnect_light_status",
            ):
                context.user_data.pop(key, None)

            await send_reply(
                message,
                "စာရင်းတင်ခြင်းကို ပယ်ဖျက်လိုက်ပါပြီခင်ဗျာ။",
                update,
                reply_markup=menu(),
            )
            return

        if raw != "✅ ပြန်သုံးမယ်":
            await send_reply(
                message,
                "ပြန်သုံးရန် အတည်ပြုပါက "
                "✅ ပြန်သုံးမယ် ကိုနှိပ်ပေးပါခင်ဗျာ။",
                update,
                reply_markup=ReplyKeyboardMarkup(
                    [["✅ ပြန်သုံးမယ်"], ["❌ မလုပ်တော့ပါ"]],
                    resize_keyboard=True,
                ),
            )
            return

        months = context.user_data.get("reconnect_months", 0)
        duration = "၆ လနှင့်အထက်" if months >= 6 else f"{months} လ"

        admin_text = (
            "♻️ WiFi ပြန်လည်အသုံးပြုရန် စာရင်းအသစ်\n\n"
            f"🆔 Customer ID: {context.user_data.get('reconnect_customer_id', 'မသိရသေးပါ')}\n"
            f"📱 ဖုန်းနံပါတ်: {context.user_data.get('reconnect_phone', 'မသိရသေးပါ')}\n"
            f"📅 မသုံးဖြစ်သည့်ကာလ: {duration}\n"
            f"💡 မီးအခြေအနေ: {context.user_data.get('reconnect_light_status', 'မစစ်ဆေးရသေးပါ')}\n"
            f"💰 သတ်မှတ်ချက်: {'ပုံမှန်တစ်လစာ' if months <= 2 else '၃ လစာ ကြိုတင်ပေးသွင်းရန်'}\n"
            "✅ ပြန်သုံးရန် အတည်ပြုပြီးပါပြီ။"
        )

        try:
            await notify_admin(context, admin_text)
        except Exception:
            pass

        reset_flow(context)

        for key in (
            "reconnect_months",
            "reconnect_customer_id",
            "reconnect_phone",
            "reconnect_light_status",
        ):
            context.user_data.pop(key, None)

        await send_reply(
            message,
            "🙏 ကျေးဇူးတင်ပါတယ်ခင်ဗျာ။\n\n"
            "📋 WiFi ပြန်လည်အသုံးပြုရန် စာရင်းကို လက်ခံရရှိပါပြီ။\n\n"
            "Customer Support Team မှ စစ်ဆေးပြီး ဆက်သွယ်ပေးပါမယ်။\n\n"
            "📞 Customer Support — 09-777719577\n\n"
            "☎️ လူကိုယ်တိုင် စာရင်းတင်လိုပါက "
            "လိုင်းခွဲနံပါတ် (1) — Customer Service ကို ခေါ်ဆိုနိုင်ပါတယ်။ 🙏",
            update,
            reply_markup=menu(),
        )
        return

# RUN BOT
# =========================================================

async def start_ad_scheduler(application):
    log.info("Starting automatic advertisement scheduler...")

    try:
        application.create_task(
            schedule_next_ad(application),
            name="automatic_ad_scheduler",
        )
        log.info("Automatic advertisement scheduler task created.")

    except Exception:
        log.exception("Failed to start automatic advertisement scheduler.")

# =========================================================
# MAIN
# =========================================================

def main():

    if not TOKEN:
        raise ValueError(
            "BOT_TOKEN environment variable မရှိသေးပါ။"
        )

    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(start_ad_scheduler)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("post", post_to_channel))
    app.add_handler(CommandHandler("chatid", chatid_command))
    app.add_handler(CommandHandler("support", support_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            answer,
        )
    )

    print(f"{BOT_NAME} Bot is running...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )

# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()
