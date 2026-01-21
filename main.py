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
# 1. KHO TÀNG CONTENT
# ==============================================================================
INTRO_STRUCTURES = [
    "{d} đang cần {a} {c} {b} thì ghé bên mình nhé.",
    "Bên mình chuyên {a} các gói {c} {b} nhất thị trường.",
    "Có {d} nào đang tìm nguồn {c} {b} không ạ?",
    "Mách nhỏ {d} chỗ {a} {c} cực kỳ {b} đây.",
    "Hệ thống {a} {c} {b} hoạt động 24/7 cho {d}.",
    "Ké bài chút, bên em nhận {a} {c} {b} bảo hành trọn đời.",
    "Giải pháp {c} {b} giúp {d} tăng tương tác ngay lập tức.",
    "Không cần tìm đâu xa, ở đây có {c} {b} bao ngon.",
    "Dịch vụ {c} {b} - {a} nhiệt tình cho {d}.",
    "Xả kho {c} giá hủy diệt, {a} ngay trong ngày.",
    "Chuyên cung cấp {c} cho các shop, cam kết {b}.",
    "Nhận kèo {c} sll, {a} nhanh gọn lẹ.",
    "Mời {d} tham khảo bảng giá {c} {b} bên dưới.",
    "Hỗ trợ {d} xây dựng kênh với gói {c} siêu tiết kiệm."
]
INTRO_WORDS = {
    "a": ["hỗ trợ", "giúp", "nhận", "chạy", "xử lý", "buff", "cung cấp", "triển khai", "setup", "boost"],
    "b": ["uy tín", "giá rẻ", "siêu tốc", "ổn định", "chất lượng", "bảo hành", "giá xưởng", "an toàn", "ngon bổ rẻ"],
    "c": ["tương tác", "like sub", "follow", "mắt live", "comment", "seeding", "đánh giá", "view", "share"],
    "d": ["Anh em", "Bác nào", "Shop nào", "Bạn nào", "Chủ shop", "Mọi người", "Ae", "Các bác"]
}
PRICE_BLOCKS = [
    ["⭐ BẢNG GIÁ NIÊM YẾT:", "✅ Follow FB cá nhân: 8k/1k", "✅ Follow TikTok: 28k/1k", "✅ Tim TikTok: 3k/1k"],
    ["🔥 DEAL HỜI HÔM NAY:", "➡️ Tăng 1k Sub Phở Bò = 8k", "➡️ Tăng 1k Fl Tóp Tóp = 28k", "➡️ Tăng 1k Tym Tóp Tóp = 3k"],
    ["💎 SERVICE LIST:", "🔹 FB Follow >> 8k (Min 1k)", "🔹 Tik Follow >> 28k (Min 1k)", "🔹 Tik Heart >> 3k (Min 1k)"],
    ["⚡ Xả kho tương tác giá sỉ:", "+ Sub Face 8k/1k", "+ Fl Tik 28k/1k", "+ Tim Tik 3k/1k"]
]
CTA_LINES = [
    "👉 Vào việc ngay tại App Telegram, tìm: {bot}",
    "👉 Search Telegram: {bot} là ra em nhé.",
    "👉 Anh em qua Telegram tìm bot: {bot}",
    "👉 Nhắn tin qua Telegram: {bot}",
    "👉 Bot tự động bên Tele: {bot}",
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
    confusables = {'a': ['а'], 'o': ['о'], 'e': ['е'], 'c': ['с'], 'p': ['р'], 'x': ['х'], 'y': ['у'], 'T': ['Т'], 'H': ['Н'], 'B': ['В'], 'K': ['К'], 'M': ['М'], 'A': ['А'], 'O': ['О'], 'E': ['Е'], 'C': ['С'], 'P': ['Р'], 'X': ['Х']}
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
        # TEST MODE: Ngủ ngắn lại để bác đỡ phải chờ (10-15 phút)
        # Khi nào chạy thật thì chỉnh lại sau
        return random.randint(600, 900) 

def human_scroll(driver, distance):
    print("   + 📜 Đang lướt Newsfeed...", flush=True) # IN RA LOG ĐỂ BÁC THẤY
    current_scroll = 0
    step_size = random.randint(30, 60)
    while current_scroll < distance:
        time.sleep(random.uniform(0.01, 0.05)) 
        driver.execute_script(f"window.scrollBy(0, {step_size})")
        current_scroll += step_size
        if random.random() < 0.05:
            time.sleep(random.uniform(0.5, 1.5))

def setup_driver():
    print(">>> 🛠️ Đang khởi tạo Driver (Profile: Việt Kiều Mỹ)...", flush=True)
    chrome_options = Options()
    
    # --- CẤU HÌNH ---
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=375,812")
    
    # --- 🔥 ÉP TIẾNG VIỆT ---
    chrome_options.add_argument("--lang=vi-VN")
    
    # --- ANTI-DETECT ---
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # --- CỐ ĐỊNH THIẾT BỊ ---
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": ua
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # --- FAKE TIMEZONE VN & XÓA DẤU VẾT ---
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    params = { "timezoneId": "Asia/Ho_Chi_Minh" }
    driver.execute_cdp_cmd("Emulation.setTimezoneOverride", params)
    
    return driver

# ==============================================================================
# 3. TƯƠNG TÁC DẠO (AGGRESSIVE MODE)
# ==============================================================================
def tuong_tac_dao(driver):
    print("\n--- 🤸 BẮT ĐẦU CHẾ ĐỘ 'ĐI DẠO' ---", flush=True)
    try:
        scroll_times = random.randint(3, 5)
        interacted = False
        for i in range(scroll_times):
            
            # Human Scroll
            dist = random.randint(500, 800)
            human_scroll(driver, dist)
            time.sleep(random.randint(2, 4))
            
            # Logic: Tăng tỷ lệ tương tác lên 60%
            if not interacted and random.random() > 0.4:
                
                main_like_xpaths = [
                    "//div[@role='button' and contains(@aria-label, 'Thích')]", 
                    "//div[@role='button' and contains(@aria-label, 'thích')]",
                    "//div[@role='button' and contains(@aria-label, 'Like')]",
                    "//div[@role='button' and contains(@aria-label, 'like')]"
                ]
                
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
                    
                    # 🔥 [TEST] Tăng tỷ lệ Thả Tim lên 80% (0.2) thay vì 50% (0.5)
                    if random.random() > 0.2: 
                        try:
                            actions = ActionChains(driver)
                            actions.move_to_element(found_btn).click_and_hold().perform()
                            time.sleep(2) 
                            
                            reaction_xpaths = [
                                "//div[@role='button' and @aria-label='Yêu thích']", 
                                "//div[@role='button' and @aria-label='Thương thương']",
                                "//div[@role='button' and @aria-label='Haha']",
                                "//div[@role='button' and @aria-label='Wow']",
                                "//div[@role='button' and @aria-label='Buồn']",
                                "//div[@role='button' and @aria-label='Love']", 
                                "//div[@role='button' and @aria-label='Care']",
                                "//div[@role='button' and @aria-label='Sad']"
                            ]
                            
                            visible_reacts = []
                            for rxp in reaction_xpaths:
                                r_btns = driver.find_elements(By.XPATH, rxp)
                                for r in r_btns:
                                    if r.is_displayed(): visible_reacts.append(r)
                            
                            if len(visible_reacts) > 0:
                                chosen = random.choice(visible_reacts)
                                react_type = chosen.get_attribute("aria-label")
                                chosen.click()
                                actions.release().perform()
                                print(f"   + 😍 Đã thả cảm xúc: {react_type}", flush=True)
                                interacted = True
                            else:
                                actions.release().perform()
                                found_btn.click() # Không thấy bảng thì like thường
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
# 4. MAIN LOOP (AGGRESSIVE MODE: NO LAZY)
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
        
        gui_anh_tele(driver, "✅ LOGIN OK! Vào chế độ HUMAN SCROLL...")

        # ==========================================
        #           LOGIC SPAM
        # ==========================================
        XPATH_COMMENT_BTNS = ["//div[@role='button' and contains(@aria-label, 'comment')]", "//div[@role='button' and contains(@aria-label, 'bình luận')]", "//div[@role='button' and contains(., 'Bình luận')]", "//div[@role='button' and contains(., 'Comment')]", "//span[contains(text(), 'Bình luận')]", "//span[contains(text(), 'Comment')]"]
        XPATH_INPUTS = ["//textarea[contains(@class, 'internal-input')]", "//textarea[contains(@placeholder, 'Viết bình luận')]", "//textarea[contains(@placeholder, 'Write a comment')]", "//div[@role='textbox']"]
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

                # 🔥 [TEST] TẮT LAZY MODE: Luôn luôn comment
                # if random.random() < 0.2:
                #     print(">>> 😴 LAZY MODE: Ngủ...", flush=True)
                #     delay = get_sleep_time_smart()
                #     print(f"   + 💤 Ngủ {delay}s...", flush=True)
                #     time.sleep(delay)
                #     continue

                # 3. TÌM BÀI COMMENT
                found_btn = None
                for i in range(2): 
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
                        found_btn.click()
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
                            driver.find_element(By.XPATH, XPATH_SEND).click()
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
