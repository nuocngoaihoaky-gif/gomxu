import os
import signal
import sys
from telebot import TeleBot, types

# --- 1. LẤY TOKEN TỪ MÔI TRƯỜNG ---
sys_core_token = os.environ.get("APP_KEY")  # Token Telegram Bot

if not sys_core_token:
    print("❌ Lỗi: Thiếu APP_KEY (Telegram Token)")
    sys.exit(1)

# --- 2. KHỞI TẠO BOT ---
service_node = TeleBot(sys_core_token)

# --- 3. NỘI DUNG /START ---
BROADCAST_MSG = """⛏️ TỶ PHÚ BẦU TRỜI - GIẢI TRÍ KIẾM TIỀN 2026

Biến thời gian rảnh rỗi thành thu nhập thật! Không cần nạp vốn, không rủi ro.

Cơ chế kiếm tiền đơn giản:
✈️ Bay máy bay: Dùng năng lượng miễn phí để thu thập Xu trên bầu trời.
💰 Tích lũy: Gom Xu càng nhiều, đổi thưởng càng lớn.
🎁 Nhiệm vụ: Làm task nhẹ nhàng (Join group, mời bạn) nhận thưởng nóng.
🏦 Rút tiền: Hỗ trợ quy đổi Xu về tài khoản ngân hàng/Momo nhanh chóng.

Tham gia cộng đồng "dân cày" MMO ngay hôm nay!

👉 Ấn nút Mở Mini App 🚀 để sử dụng miniApp
"""

# --- 4. TẠO BÀN PHÍM ---
main_dashboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)

web_module_config = types.WebAppInfo("https://typhubautroi.vercel.app/")
btn_main = types.KeyboardButton(text="Mở Mini App 🚀", web_app=web_module_config)
btn_channel = types.KeyboardButton(text="📢 Intro Like Channel")
btn_group = types.KeyboardButton(text="👥 Cộng Đồng Intro Like")

// main_dashboard.add(btn_main, btn_channel, btn_group)
main_dashboard.add(btn_main)

inline_start = types.InlineKeyboardMarkup()
inline_start.add(
    types.InlineKeyboardButton(
        text="Mở Mini App 🚀",
        url="https://t.me/TyPhuBauTroi_bot/MiniApp"
    )
)

# --- 5. TẮT BOT AN TOÀN ---
def grace_shutdown(sig, frame):
    service_node.stop_polling()
    sys.exit(0)

signal.signal(signal.SIGTERM, grace_shutdown)
signal.signal(signal.SIGINT, grace_shutdown)

# --- 6. HANDLER CƠ BẢN ---

@service_node.message_handler(commands=["start"])
def init_handshake(transaction):
    service_node.send_message(
        transaction.chat.id,
        "👋 Chào mừng bạn đến với INTRO LIKE!",
        reply_markup=main_dashboard
    )
    service_node.send_message(
        transaction.chat.id,
        BROADCAST_MSG,
        reply_markup=inline_start
    )

@service_node.message_handler(func=lambda m: m.text == "📢 Intro Like Channel")
def nav_channel(transaction):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text="👉 BẤM ĐỂ THAM GIA KÊNH",
            url="https://t.me/vienduatin"
        )
    )
    service_node.send_message(
        transaction.chat.id,
        "Truy cập kênh chính thức dưới đây:",
        reply_markup=markup
    )

@service_node.message_handler(func=lambda m: m.text == "👥 Cộng Đồng Intro Like")
def nav_group(transaction):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            text="👉 BẤM ĐỂ VÀO NHÓM",
            url="https://t.me/BAOAPPMIENPHI22"
        )
    )
    service_node.send_message(
        transaction.chat.id,
        "Tham gia cộng đồng thảo luận:",
        reply_markup=markup
    )

# --- 7. CHẠY BOT ---
if __name__ == "__main__":
    print("🤖 Bot Intro Like đang chạy (KHÔNG AI)...")
    try:
        service_node.infinity_polling()
    except Exception as e:
        print(f"❌ Bot bị Crash: {e}")
