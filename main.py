import time
import random
import os
import sys
import requests
import pyotp
from datetime import datetime
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==============================================================================
# 1. KHO TÀNG CONTENT (V14: GIÁ CẢ RÕ RÀNG - KHÔNG GÂY HIỂU LẦM)
# ==============================================================================
INTRO_STRUCTURES = [
    # --- NHÓM 1: CÂU GỐC (Trực diện) ---
    "{d} đang cần {a} {c} {b} thì ghé bên mình nhé.",
    "Bên mình chuyên {a} các gói {c} {b} nhất thị trường.",
    "Mách nhỏ {d} chỗ {a} {c} cực kỳ {b} đây.",
    "Hệ thống {a} {c} {b} hoạt động 24/7 cho {d}.",
    "Ké bài chút, bên em nhận {a} {c} {b} bảo hành trọn đời.",
    "Giải pháp {c} {b} giúp {d} tăng tương tác ngay lập tức.",
    "Dịch vụ {c} {b} - {a} nhiệt tình cho {d}.",
    "Xả kho {c} giá hủy diệt, {a} ngay trong ngày.",
    "Chuyên cung cấp {c} cho các shop, cam kết {b}.",
    "Hỗ trợ {d} xây dựng kênh với gói {c} siêu tiết kiệm.",

    # --- NHÓM 2: TRENDY ---
    "U là trời, {d} nào đang cần {a} {c} {b} thì bơi hết vào đây nha.",
    "Sơ hở là {a} {c}, đảm bảo {b} hết nước chấm cho {d}.",
    "Ét o ét! {d} ơi, bên mình đang {a} gói {c} siêu {b} nè.",
    "Chấn động! Deal {c} {b} sập sàn, {d} chốt đơn lẹ kẻo lỡ.",
    "Kiếp nạn thứ 82 là chưa tìm được chỗ {a} {c} {b}? Ghé em ngay!",
    "Mlem mlem, bảng giá {c} bên em bao {b}, nhìn là muốn chốt.",
    "Gét gô! Cùng {a} {c} để lên xu hướng nào {d} ơi.",
    "Xin vía tương tác! Bác nào cần {a} {c} thì chấm (.) em báo giá.",
    
    # --- NHÓM 3: GIỌNG THÂN THIỆN ---
    "{d} cần làm {c} cho kênh nhìn đỡ trống không ạ?",
    "Ai đang lo vụ {c} thì bên mình có giải pháp {b} nhé.",
    "Chia sẻ nhẹ cho {d} nào đang bí {c}.",
    "{d} mới làm kênh mà thiếu {c} thì ib em tư vấn.",
    "Làm kênh mà chưa có {c} nhìn hơi buồn đó {d} ơi.",
    "Trước em làm kênh cũng bí {c}, sau dùng bên này thấy ổn.",
    "Nhiều shop bên em đang dùng gói {c} này thấy khá ok.",
    "Kinh nghiệm cá nhân: làm {c} đều thì kênh lên ổn hơn.",
    "Ai quan tâm {c} thì em để info bên dưới nhé.",
    "Bác nào tò mò về {c} {b} có thể tham khảo thử.",
    "Chia sẻ để {d} nào cần thì dùng, không ép nhé.",
    
    # --- NHÓM 4: CÂU HỎI GỢI MỞ ---
    "{d} có đang gặp khó khi làm {c} không?",
    "Có ai từng đau đầu vì thiếu {c} chưa?",
    "{d} nào cần cải thiện {c} trong thời gian ngắn không?",
    "Hỏi thật, {d} có đang cần đẩy {c} không?",
]

INTRO_WORDS = {
    "a": ["hỗ trợ", "nhận kèo", "chạy", "xử lý", "buff", "cung cấp", "đẩy", "bơm", "boost", "setup"],
    "b": ["xịn sò", "keo lỳ", "uy tín", "rẻ tụt quần", "bao chất", "siêu tốc", "ổn áp", "ngon bổ rẻ", "đỉnh cao", "giá rẻ"],
    "c": ["tương tác", "follow/sub", "like dạo", "mắt live", "comment", "seeding", "đánh giá", "view"],
    "d": ["Anh em", "Bác nào", "Shop nào", "Chế nào", "Chủ shop", "Mấy ní", "Các sếp", "Ae thiện lành", "Mọi người"]
}

# --- 🔥 UPDATE: ĐƠN VỊ TÍNH RÕ RÀNG (/1K) ---
PRICE_BLOCKS = [
    # Mẫu 1
    ["🔥 BẢNG GIÁ LẺ:", "✅ Sub Face: 8k/1.000 sub", "✅ Follow Tik: 28k/1.000 fl", "✅ Tim Tik: 3k/1.000 tim"],
    # Mẫu 2
    ["⚡ FLASH SALE:", "🔸 1k Sub Phở Bò = 8 cành", "🔸 1k Fl TikTok = 28 cành", "🔸 1k Tym TikTok = 3 cành"],
    # Mẫu 3
    ["💎 SERVICE LIST:", "🔹 FB Follow >> 8k/1k", "🔹 Tik Follow >> 28k/1k", "🔹 Tik Heart >> 3k/1k"],
    # Mẫu 4
    ["🌟 DEAL HOT:", "+ Sub Face 8k/k", "+ Fl Tik 28k/k", "+ Tim Tik 3k/k"],
    # Mẫu 5
    ["🚀 COMBO:", "✔️ Sub xanh: 8.000đ/1k", "✔️ Fl TikTok: 28.000đ/1k", "✔️ Tim TikTok: 3.000đ/1k"],
    # Mẫu 6
    ["📦 GIÁ XƯỞNG:", "- Follow FB: 8k/1000", "- Follow TT: 28k/1000", "- Like TT: 3k/1000"],
    # Mẫu 7
    ["✨ UPDATE GIÁ: Sub FB 8k/1k | Fl Tik 28k/1k | Tim Tik 3k/1k. Bao tụt."],
    # Mẫu 8
    ["❤️ BẢNG GIÁ:", "★ 1k Theo dõi FB: 8k xu", "★ 1k Follow Tik: 28k xu", "★ 1k Tim video: 3k xu"],
    # Mẫu 9
    ["🔥 HOT: Sub FB chỉ 8k/1k - Follow Tik 28k/1k - Tim 3k/1k. BH trọn đời."],
    # Mẫu 10
    ["📌 MENU:", "➡️ Sub Phở Bò: 8k/1k", "➡️ Fl Tóp Tóp: 28k/1k", "➡️ Tim Tóp Tóp: 3k/1k"],
    # Mẫu 11
    ["Gửi bác báo giá (Gói 1000):", "1. Sub Face 8k", "2. Follow Tik 28k", "3. Tim Tik 3k"],
    # Mẫu 12
    ["⭐ GIÁ NIÊM YẾT ⭐", "▪️ FB Follow: 8k/1k", "▪️ TT Follow: 28k/1k", "▪️ TT Like: 3k/1k"],
    # Mẫu 13
    ["[ UPDATE PRICE ]", "• Sub FB: 8k/1.000", "• Fl Tik: 28k/1.000", "• Tim Tik: 3k/1.000"],
    # Mẫu 14
    ["✨ 𝐒𝐄𝐑𝐕𝐈𝐂𝐄 ✨", "👉 Sub Face: 8k/1k", "👉 Fl Tik: 28k/1k", "👉 Tim Tik: 3k/1k"],
    # Mẫu 15
    ["Báo giá nhanh:", "Face: 8k/1k sub", "Tik: 28k/1k fl", "Tik: 3k/1k tim"],
    # Mẫu 16
    ["💰 Bảng giá:", "💵 Sub FB: 8k/1k", "💵 Fl Tik: 28k/1k", "💵 Tim: 3k/1k"],
    # Mẫu 17
    ["- FB Follow: 8.000đ/1k", "- TT Follow: 28.000đ/1k", "- TT Heart: 3.000đ/1k"],
    # Mẫu 18
    ["🔥 DEAL SỐC:", "🔸 Sub FB: 8ca/1k", "🔸 Fl Tik: 28ca/1k", "🔸 Tim: 3ca/1k"],
    # Mẫu 19
    ["✨ Dịch vụ hot:", "Sub Face >> 8k/1k", "Fl Tik >> 28k/1k", "Tim Tik >> 3k/1k"],
    # Mẫu 20
    ["Giá cực yêu: Tăng 1000 follow fb 8k, tăng 1000 follow tiktok 28k, tăng 1000 tim 3k."]
]

CTA_LINES = [
    "👉 Vào việc ngay tại App Telegram, tìm: {bot}",
    "👉 Search Tele: {bot} là ra em nhé (Avatar đẹp trai).",
    "👉 Anh em qua Telegram tìm bot: {bot} để chốt đơn.",
    "👉 Nhắn tin qua Telegram: {bot} (Auto 24/7).",
    "👉 Bot tự động bên Tele: {bot} (Nạp là chạy).",
    "👉 Ghé Telegram: {bot} test thử nha mấy ní.",
    "👉 Cần gì cứ qua Tele: {bot} hú em.",
    "👉 Mời bác qua Tele: {bot} trải nghiệm thử.",
    "👉 Ai cần gấp thì qua Tele: {bot} em ưu tiên làm trước.",
    "👉 Bác nào chưa có Tele thì tải về tìm: {bot} nha.",
    "👉 Cách dùng: Vào Telegram -> Tìm {bot} -> Start.",
    "👉 Lên App Tele gõ: {bot} là thấy em liền.",
    "👉 Search user: {bot} trên Telegram nhé.",
    "👉 Tìm đúng ID Tele: {bot} (Tránh fake).",
    "👉 Gõ {bot} vào ô tìm kiếm Telegram là ra.",
    "👉 Tele: {bot}",
    "👉 Contact Tele: {bot}",
    "👉 Info Tele: {bot}",
    "👉 Support via Tele: {bot}",
    "👉 Telegram: {bot}",
    "👉 Nhanh tay qua Tele: {bot} nhận ưu đãi.",
    "👉 Ib lẹ qua Tele: {bot} em tư vấn free.",
    "👉 Chốt đơn tại Tele: {bot} nha ae.",
    "👉 Qua Tele: {bot} đặt đơn cho lẹ.",
    "👉 Xử lý nhanh tại Tele: {bot}.",
]

def gen_intro():
    s = random.choice(INTRO_STRUCTURES)
    return s.format(a=random.choice(INTRO_WORDS["a"]), b=random.choice(INTRO_WORDS["b"]), c=random.choice(INTRO_WORDS["c"]), d=random.choice(INTRO_WORDS["d"]))
def gen_price(): return "\n".join(random.choice(PRICE_BLOCKS))
def gen_cta(bot="@intro_like_bot"): return random.choice(CTA_LINES).format(bot=bot)

# ==============================================================================
# 2. CÁC HÀM HỖ TRỢ
# ==============================================================================

def gui_anh_tele(driver, caption="Ảnh chụp màn hình"):
    try:
        token = os.environ.get("TELEGRAM_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        if not token or not chat_id: return
        filename = "temp_screenshot.png"
        driver.save_screenshot(filename)
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        with open(filename, 'rb') as photo:
            requests.post(url, files={'photo': photo}, data={'chat_id': chat_id, 'caption': caption})
    except: pass

def bien_hinh_van_ban(text):
    confusables = {'a': ['а'], 'o': ['о'], 'I': ['l'], 'l': ['I'], 'e': ['е'], 'c': ['с'], 'p': ['р'], 'x': ['х'], 'y': ['у'], 'T': ['Т'], 'H': ['Н'], 'B': ['В'], 'K': ['К'], 'M': ['М'], 'A': ['А'], 'O': ['О'], 'E': ['Е'], 'C': ['С'], 'P': ['Р'], 'X': ['Х']}
    new_text = ""
    for char in text:
        if char in confusables: new_text += random.choice(confusables[char])
        else: new_text += char
    return new_text

def get_2fa_code(secret_key):
    totp = pyotp.TOTP(secret_key.replace(" ", ""))
    return totp.now()

def get_sleep_time_smart():
    tz_VN = pytz.timezone('Asia/Ho_Chi_Minh') 
    current_hour = datetime.now(tz_VN).hour
    print(f"   🕒 Giờ hiện tại (VN): {current_hour}h", flush=True)
    if 0 <= current_hour < 6:
        print("   🌙 Đêm rồi, ngủ 2-3 tiếng...", flush=True)
        return random.randint(7200, 10800) 
    else:
        # Ngủ ngày: 45p - 60p (CHUẨN AN TOÀN)
        return random.randint(2700, 3600)

def human_scroll(driver, distance):
    current_scroll = 0
    step_size = random.randint(30, 60)
    while current_scroll < distance:
        time.sleep(random.uniform(0.01, 0.05)) 
        driver.execute_script(f"window.scrollBy(0, {step_size})")
        current_scroll += step_size
        if random.random() < 0.05:
            time.sleep(random.uniform(0.5, 1.5))

def xu_ly_sau_login(driver):
    print(">>> 🛡️ Đang kiểm tra các bước xác minh/lưu trình duyệt...", flush=True)
    try:
        check_xpaths = [
            "//span[contains(text(), 'Lưu')]",      
            "//span[contains(text(), 'Tiếp tục')]",
            "//div[@role='button' and contains(., 'Lưu')]",
            "//div[@role='button' and contains(., 'Tiếp tục')]",
            "//button[@value='OK']"
        ]
        for _ in range(3):
            for xp in check_xpaths:
                try:
                    btns = driver.find_elements(By.XPATH, xp)
                    for btn in btns:
                        if btn.is_displayed():
                            print(f"   🔨 Bấm nút cản đường: {btn.text}", flush=True)
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(5) 
                            return 
                except: pass
            time.sleep(2)
    except Exception as e: print(f"   ! Lỗi xử lý sau login: {e}", flush=True)

def diet_popup(driver):
    try:
        popup_xpaths = ["//span[contains(text(), 'Lúc khác')]", "//span[contains(text(), 'Not now')]", "//span[contains(text(), 'Để sau')]", "//div[@aria-label='Đóng']", "//div[@aria-label='Close']"]
        for xp in popup_xpaths:
            btns = driver.find_elements(By.XPATH, xp)
            if len(btns) > 0:
                for btn in btns:
                    if btn.is_displayed():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(1)
    except: pass

def setup_driver():
    print(">>> 🛠️ Đang khởi tạo Driver (Profile: Việt Kiều Mỹ)...", flush=True)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=375,812")
    chrome_options.add_argument("--lang=vi-VN")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    mobile_emulation = { "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 }, "userAgent": ua }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    params = { "timezoneId": "Asia/Ho_Chi_Minh" }
    driver.execute_cdp_cmd("Emulation.setTimezoneOverride", params)
    return driver

# ==============================================================================
# 3. TƯƠNG TÁC DẠO (SAFE MODE)
# ==============================================================================
def tuong_tac_dao(driver):
    print("\n--- 🤸 BẮT ĐẦU CHẾ ĐỘ 'ĐI DẠO' ---", flush=True)
    try:
        scroll_times = random.randint(3, 5)
        interacted = False
        for i in range(scroll_times):
            diet_popup(driver)
            
            dist = random.randint(500, 800)
            human_scroll(driver, dist)
            time.sleep(random.randint(4, 8))
            
            # Tỷ lệ tương tác 60%
            if not interacted and random.random() > 0.4:
                main_like_xpaths = ["//div[@role='button' and contains(@aria-label, 'Thích')]", "//div[@role='button' and contains(@aria-label, 'thích')]", "//div[@role='button' and contains(@aria-label, 'Like')]", "//div[@role='button' and contains(@aria-label, 'like')]"]
                found_btn = None
                for xp in main_like_xpaths:
                    btns = driver.find_elements(By.XPATH, xp)
                    if len(btns) > 0:
                        for b in btns:
                            if b.is_displayed(): found_btn = b; break
                    if found_btn: break
                
                if found_btn:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", found_btn)
                    time.sleep(1)
                    
                    # 70% Thả Tim, 30% Like thường
                    if random.random() > 0.3: 
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(found_btn).click_and_hold().perform()
                            time.sleep(3) 
                            
                            reaction_xpaths = ["//div[@role='button' and @aria-label='Yêu thích']", "//div[@role='button' and @aria-label='Thương thương']", "//div[@role='button' and @aria-label='Haha']", "//div[@role='button' and @aria-label='Wow']", "//div[@role='button' and @aria-label='Buồn']", "//div[@role='button' and @aria-label='Phẫn nộ']"]
                            visible_reacts = []
                            for rxp in reaction_xpaths:
                                r_btns = driver.find_elements(By.XPATH, rxp)
                                for r in r_btns:
                                    if r.is_displayed(): visible_reacts.append(r)
                            
                            if len(visible_reacts) > 0:
                                chosen = random.choice(visible_reacts)
                                react_type = chosen.get_attribute("aria-label")
                                driver.execute_script("arguments[0].click();", chosen) 
                                actions.release().perform()
                                print(f"   + 😍 Đã thả cảm xúc: {react_type}", flush=True)
                                interacted = True
                            else:
                                actions.release().perform()
                                found_btn.click() 
                                interacted = True
                        except: pass
                    else: 
                        try:
                            found_btn.click()
                            print("   + 👍 Đã Like thường.", flush=True)
                            interacted = True
                        except: pass
    except Exception as e: print(f"   ! Lỗi đi dạo: {e}", flush=True)
    print("--- ✅ KẾT THÚC ĐI DẠO ---\n", flush=True)

# ==============================================================================
# 4. MAIN LOOP (SAFE MODE)
# ==============================================================================
def main():
    print(">>> 🚀 BOT KHỞI ĐỘNG...", flush=True)
    email = os.environ["FB_EMAIL"]
    password = os.environ["FB_PASS"]
    key_2fa = os.environ["FB_2FA_KEY"]
    driver = setup_driver()
    wait = WebDriverWait(driver, 30)

    try:
        # --- LOGIN ---
        print(">>> 📱 Vào Facebook...", flush=True)
        driver.get("https://m.facebook.com/")
        print(">>> 🔐 Nhập User/Pass...", flush=True)
        try:
            try: email_box = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            except: email_box = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            email_box.clear(); email_box.send_keys(email)
            pass_box = driver.find_element(By.NAME, "pass")
            pass_box.clear(); pass_box.send_keys(password)
        except Exception as e: gui_anh_tele(driver, f"❌ Lỗi điền form: {e}")

        print(">>> 🔎 Bấm nút Login...", flush=True)
        login_clicked = False
        login_xpaths = ["//span[contains(text(), 'Log in')]", "//span[contains(text(), 'Log In')]", "//span[contains(text(), 'Đăng nhập')]", "//button[@name='login']", "//div[@role='button' and (contains(., 'Log In') or contains(., 'Đăng nhập'))]", "//input[@value='Log In']", "//input[@type='submit']"]
        for xpath in login_xpaths:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(1)
                btn.click()
                login_clicked = True
                break
            except: continue
        if not login_clicked:
            try: driver.find_element(By.NAME, "pass").send_keys(Keys.ENTER)
            except: pass
        time.sleep(15)

        # --- 2FA LOGIC ---
        print(">>> 🕵️ Kiểm tra 2FA...", flush=True)
        try_btn = None
        try_xpaths = ["//div[@role='button' and contains(., 'Try another way')]", "//div[@role='button' and contains(., 'Thử cách khác')]"]
        for xp in try_xpaths:
            try:
                if len(driver.find_elements(By.XPATH, xp)) > 0:
                    try_btn = driver.find_element(By.XPATH, xp); break
            except: continue
            
        if try_btn:
            try_btn.click(); time.sleep(3)
            auth_app_xpaths = ["//div[@role='radio' and contains(@aria-label, 'Authentication app')]", "//div[contains(., 'Authentication app')]"]
            for axp in auth_app_xpaths:
                try: driver.find_element(By.XPATH, axp).click(); break
                except: continue
            time.sleep(2)
            continue_xpaths = ["//div[@role='button' and @aria-label='Continue']", "//div[@role='button' and @aria-label='Tiếp tục']"]
            for cxp in continue_xpaths:
                try: driver.find_element(By.XPATH, cxp).click(); break
                except: continue
            time.sleep(5)

        fa_input = None
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                if inp.get_attribute("type") in ["tel", "number"]: fa_input = inp; break
        except: pass
        if not fa_input:
            fa_xpaths = ["//input[@name='approvals_code']", "//input[@placeholder='Code']", "//input[@aria-label='Code']"]
            for xp in fa_xpaths:
                try: fa_input = driver.find_element(By.XPATH, xp); break
                except: continue

        if fa_input:
            otp = get_2fa_code(key_2fa)
            print(f">>> 🔥 Nhập OTP: {otp}", flush=True)
            gui_anh_tele(driver, f"🔥 Nhập OTP: {otp}")
            fa_input.click(); fa_input.send_keys(otp); time.sleep(2)
            submit_xpaths = ["//div[@role='button' and @aria-label='Continue']", "//div[@role='button' and @aria-label='Tiếp tục']", "//button[@type='submit']", "//button[@id='checkpointSubmitButton']"]
            for btn_xp in submit_xpaths:
                try: driver.find_element(By.XPATH, btn_xp).click(); break
                except: continue
            fa_input.send_keys(Keys.ENTER); time.sleep(10)
        
        xu_ly_sau_login(driver)
        gui_anh_tele(driver, "✅ LOGIN OK! Vào chế độ HUMAN SCROLL...")

        # ==========================================
        #           LOGIC SPAM
        # ==========================================
        XPATH_COMMENT_BTNS = ["//div[@role='button' and contains(@aria-label, 'comment')]", "//div[@role='button' and contains(@aria-label, 'Bình luận')]", "//div[@role='button' and contains(., 'Bình luận')]", "//span[contains(text(), 'Bình luận')]"]
        XPATH_INPUTS = ["//textarea[contains(@class, 'internal-input')]", "//textarea[contains(@placeholder, 'Viết bình luận')]", "//div[@role='textbox']"]
        XPATH_SEND = "//div[@role='button' and (@aria-label='Post a comment' or @aria-label='Đăng bình luận' or @aria-label='Gửi' or @aria-label='Post')]"

        count = 0
        fail_count = 0

        while True:
            try:
                count += 1
                print(f"\n--- 🔄 Lượt quét {count} ---", flush=True)
                driver.get("https://m.facebook.com/")
                time.sleep(5)
                
                # 1. ĐI DẠO
                tuong_tac_dao(driver)

                # 2. LAZY MODE (BẬT LẠI ĐỂ AN TOÀN)
                if random.random() < 0.2:
                    print(">>> 😴 LAZY MODE: Lượt này lười quá, đi ngủ!", flush=True)
                    delay = get_sleep_time_smart()
                    print(f"   + 💤 Ngủ {delay}s...", flush=True)
                    time.sleep(delay)
                    continue

                # 3. TÌM BÀI COMMENT
                found_btn = None
                for i in range(2): 
                    diet_popup(driver)
                    human_scroll(driver, random.randint(500, 700))
                    time.sleep(2)
                    for xp in XPATH_COMMENT_BTNS:
                        btns = driver.find_elements(By.XPATH, xp)
                        if len(btns) > 0:
                            for b in btns:
                                if b.is_displayed(): found_btn = b; break
                        if found_btn: break
                    if found_btn: break
                
                if found_btn:
                    fail_count = 0 
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", found_btn)
                        time.sleep(1)
                        print("   + 🖱️ Click nút Comment (JS Click)...", flush=True)
                        driver.execute_script("arguments[0].click();", found_btn)
                        time.sleep(3)
                        
                        input_box = None
                        for in_xp in XPATH_INPUTS:
                            try:
                                box = wait.until(EC.presence_of_element_located((By.XPATH, in_xp)))
                                if box.is_displayed(): input_box = box; break
                            except: continue
                        
                        if input_box:
                            input_box.click()
                            intro_text = gen_intro(); price_text = gen_price()
                            part1_obfuscated = bien_hinh_van_ban(f"{intro_text}\n{price_text}")
                            part2_cta = gen_cta(bot="@intro_like_bot")
                            final_content = f"{part1_obfuscated}\n{part2_cta}"
                            
                            print("   + Đang nhập liệu...", flush=True)
                            driver.execute_script("var elm = arguments[0]; elm.value = arguments[1]; elm.dispatchEvent(new Event('input', { bubbles: true })); elm.dispatchEvent(new Event('change', { bubbles: true }));", input_box, final_content)
                            input_box.send_keys(" ") 
                            time.sleep(2)
                            
                            send_btn = driver.find_element(By.XPATH, XPATH_SEND)
                            driver.execute_script("arguments[0].click();", send_btn)
                            time.sleep(5)
                            
                            page_source = driver.page_source
                            if "You're temporarily blocked" in page_source or "Bạn tạm thời bị chặn" in page_source:
                                gui_anh_tele(driver, "❌ BÁO ĐỘNG: BỊ CHẶN! TẮT BOT.")
                                return

                            print(f"   + ✅ Comment OK!", flush=True)
                            gui_anh_tele(driver, f"✅ Đã Comment: {final_content[:30]}...")
                            delay = get_sleep_time_smart()
                            print(f"   + 💤 Ngủ {delay}s...", flush=True)
                            time.sleep(delay)
                        else: print("   ! Không thấy ô nhập.", flush=True)
                    except Exception as e: print(f"   ! Lỗi thao tác: {e}", flush=True)
                else:
                    print("   ! Không thấy nút comment...", flush=True)
                    fail_count += 1
                    if fail_count >= 10: return
                    time.sleep(2)

            except Exception as e:
                print(f"❌ Lỗi vòng lặp: {e}", flush=True)
                time.sleep(10)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
