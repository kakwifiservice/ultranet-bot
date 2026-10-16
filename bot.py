# -*- coding: utf-8 -*-
"""Ultra Net KAK customer-support Telegram bot.
Python 3.14; python-telegram-bot 22.x
Set BOT_TOKEN and ADMIN_CHAT_ID as environment variables. Never paste the token into chat.
"""
import os
import re
import logging
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

            await notify_admin( context, f"📝 လိုင်းသစ်တပ်ဆင်ရန် လျှောက်လွှာအသစ်\n\n{summary}" 
            )
            
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

    if flow == "unknown_los":

        if "နီ" in text and "မနီ" not in text:
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
09-777719577 ကို ဆက်သွယ်နိုင်ပါတယ်။
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

            await send_complaint_report(
                update,
                context,
                "Router / ONU Power မီး",
                "Customer အဖြေအရ Router / ONU Power မီး လင်းနေသည်။ Router / ONU အခြေအနေကို စစ်ဆေးရန် Report ပို့ထားသည်။"
            )

            context.user_data["flow"] = "router_lights"

            await send_reply(
                message,
                """🟢 Power မီး လင်းနေပါတယ်ခင်ဗျာ။ 🙏

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
📞 Customer Support ကို ဆက်သွယ်နိုင်ပါတယ်။
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

🟢 ရပါပြီ
🔴 မရသေးပါဘူး
""",
                update,
                yes_no_menu(),
            )
            return

    if flow == "single_device_result":

        if "ရပါ" in text and "မရ" not in text:

            reset_flow(context)

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

    if flow == "speed":

        if "1" in text or "အားလုံး" in text:

            context.user_data["flow"] = "speed_test"
            context.user_data["speed_type"] = "Device အားလုံး Internet နှေးခြင်း"

            await send_reply(
                message,
                """📈 Device အားလုံးမှာ Internet နှေးနေပါက

Speed Test စစ်ပေးပါမယ်ခင်ဗျာ။

Download / Upload Speed ကို ကြည့်ပေးပါ။
ရလဒ်ကို စာဖြင့် ပြန်ပို့နိုင်ပါတယ်။

မစစ်တတ်ပါက ❓ မသိပါဘူး ကို ရွေးပါ။
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

            context.user_data["flow"] = "speed_single_device_result"

            await send_reply(
                message,
                """📱 Device တစ်လုံးတည်းမှာ Internet နှေးနေပါက—

1️⃣ WiFi ကို Disconnect လုပ်ပါ။
2️⃣ ပြန် Connect လုပ်ပါ။
3️⃣ Internet Speed ပြန်စမ်းကြည့်ပါ။

အခု Internet ပုံမှန်ပြန်ဖြစ်ပါသလား?
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

        if "3" in text or "ညဘက်" in text:

            context.user_data["flow"] = "speed_night"

            await send_reply(
                message,
                """🌙 ညဘက်မှာ ပိုနှေးတယ်ဆိုရင်
ဘယ်အချိန်လောက်မှာ စပြီး နှေးလာတတ်ပါသလဲခင်ဗျာ?

ဥပမာ - 8:00 PM / 9:00 PM / 10:00 PM
အချိန်ကို ပြောပေးပါ။
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
            context.user_data["speed_type"] = "အချိန်တိုင်း Internet နှေးခြင်း"

            await send_reply(
                message,
                """📈 အချိန်တိုင်း Internet နှေးနေပါက
Speed Test ရလဒ်ကို စစ်ဆေးပေးပါမယ်။

Download / Upload Speed ကို ပြန်ပို့ပေးပါ။
မစစ်တတ်ပါက ❓ မသိပါဘူး ကို ရွေးပါ။
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
        CommandHandler(
            "post",
            post_to_channel,
        )
    )

    app.add_handler(
        CommandHandler(
            "support",
            support_command,
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
