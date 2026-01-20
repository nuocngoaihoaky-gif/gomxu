import time
import random
import os
import sys
import requests
import pyotp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CẤU HÌNH ---
INTRO_SENTENCES = [
    "Hỗ trợ ae tăng tương tác uy tín,",
    "Bên mình đang có deal ngon cho ae,",
    "Xả kho tương tác giá rẻ cho ae đây,",
    "Dịch vụ Buff Sub/Like ổn định nhất hiện nay,",
    "Ké tus bác xíu nha,",
    "Hello ae, ai cần tăng like ghé em nhé,",
    "Acc clone đi dạo, tiện tay share kèo ngon,",
    "Mới tìm được con bot này hay phết,",
]

# Phần này SẼ ĐƯỢC biến hình (Né spam)
PRICE_LIST_BODY = """
⭐ BẢNG GIÁ ƯU ĐÃI:
✅ 8K = 1.000 Follow Facebook
✅ 28K = 1.000 Follow TikTok
✅ 3K = 1.000 Tym TikTok
"""

# Phần này GIỮ NGUYÊN (Để khách tìm được Bot)
BOT_SIGNATURE = "\n👉 Hệ thống tự động 24/7 tại Bot TeIegram:  @intro_like_bot"

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
    except:
        pass

def bien_hinh_van_ban(text):
    confusables = {
        'a': ['a', 'а'], 'o': ['o', 'о'], 'e': ['e', 'е'],
        'i': ['i', 'і'], 'l': ['l', 'I'], 'k': ['k', 'κ'],
        'B': ['B', 'Β'], 'T': ['T', 'Τ'], 'H': ['H', 'Η'],
        'p': ['p', 'р'], 'c': ['c', 'с'], 'y': ['y', 'у'], 'x': ['x', 'х']
    }
    new_text = ""
    for char in text:
        if char in confusables:
            new_text += random.choice(confusables[char])
        else:
            new_text += char
    return new_text

def get_2fa_code(secret_key):
    totp = pyotp.TOTP(secret_key.replace(" ", ""))
    return totp.now()

def setup_driver():
    print(">>> 🛠️ Đang khởi tạo Driver...", flush=True)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=375,812") 
    mobile_emulation = { "deviceName": "iPhone X" }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    return webdriver.Chrome(options=chrome_options)

def main():
    print(">>> 🚀 BOT KHỞI ĐỘNG...", flush=True)
    email = os.environ["FB_EMAIL"]
    password = os.environ["FB_PASS"]
    key_2fa = os.environ["FB_2FA_KEY"]

    driver = setup_driver()
    wait = WebDriverWait(driver, 30)
    gui_anh_tele(driver, "🚀 Bot bắt đầu chạy...")

    try:
        print(">>> 📱 Vào Facebook...", flush=True)
        driver.get("https://m.facebook.com/")
        
        # --- LOGIN ---
        print(">>> 🔐 Nhập User/Pass...", flush=True)
        try:
            try:
                email_box = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            except:
                email_box = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            email_box.clear()
            email_box.send_keys(email)
            pass_box = driver.find_element(By.NAME, "pass")
            pass_box.clear()
            pass_box.send_keys(password)
        except Exception as e:
            gui_anh_tele(driver, f"❌ Lỗi điền form: {e}")

        # BẤM LOGIN
        print(">>> 🔎 Bấm nút Login...", flush=True)
        login_clicked = False
        login_xpaths = [
            "//span[contains(text(), 'Log in')]", "//span[contains(text(), 'Log In')]", 
            "//span[contains(text(), 'Đăng nhập')]", "//button[@name='login']",
            "//div[@role='button' and (contains(., 'Log In') or contains(., 'Đăng nhập'))]",
            "//input[@value='Log In']", "//input[@type='submit']"
        ]
        for xpath in login_xpaths:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(1)
                btn.click()
                login_clicked = True
                break
            except:
                continue
        
        if not login_clicked:
            try: driver.find_element(By.NAME, "pass").send_keys(Keys.ENTER)
            except: pass
        
        print(">>> ⏳ Chờ 15s...", flush=True)
        time.sleep(15)
        
        # --- XỬ LÝ 2FA & THIẾT BỊ ---
        print(">>> 🕵️ Kiểm tra 2FA...", flush=True)
        
        # CASE 1: TRY ANOTHER WAY
        try_btn = None
        try_xpaths = ["//div[@role='button' and contains(., 'Try another way')]", "//div[@role='button' and contains(., 'Thử cách khác')]"]
        for xp in try_xpaths:
            try:
                if len(driver.find_elements(By.XPATH, xp)) > 0:
                    try_btn = driver.find_element(By.XPATH, xp)
                    break
            except: continue
            
        if try_btn:
            try_btn.click()
            time.sleep(3)
            auth_app_xpaths = ["//div[@role='radio' and contains(@aria-label, 'Authentication app')]", "//div[contains(., 'Authentication app')]"]
            for axp in auth_app_xpaths:
                try:
                    driver.find_element(By.XPATH, axp).click()
                    break
                except: continue
            time.sleep(2)
            continue_xpaths = ["//div[@role='button' and @aria-label='Continue']", "//div[@role='button' and @aria-label='Tiếp tục']"]
            for cxp in continue_xpaths:
                try:
                    driver.find_element(By.XPATH, cxp).click()
                    break
                except: continue
            time.sleep(5)

        # CASE 2: NHẬP CODE
        fa_input = None
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                if inp.get_attribute("type") in ["tel", "number"]:
                    fa_input = inp
                    break
        except: pass

        if not fa_input:
            fa_xpaths = ["//input[@name='approvals_code']", "//input[@placeholder='Code']", "//input[@aria-label='Code']"]
            for xp in fa_xpaths:
                try:
                    fa_input = driver.find_element(By.XPATH, xp)
                    break
                except: continue

        if fa_input:
            otp = get_2fa_code(key_2fa)
            print(f">>> 🔥 Nhập OTP: {otp}", flush=True)
            gui_anh_tele(driver, f"🔥 Nhập OTP: {otp}")
            fa_input.click()
            fa_input.send_keys(otp)
            time.sleep(2)
            submit_xpaths = ["//div[@role='button' and @aria-label='Continue']", "//div[@role='button' and @aria-label='Tiếp tục']", "//button[@type='submit']", "//button[@id='checkpointSubmitButton']"]
            for btn_xp in submit_xpaths:
                try:
                    driver.find_element(By.XPATH, btn_xp).click()
                    break
                except: continue
            fa_input.send_keys(Keys.ENTER)
            time.sleep(10)

        # --- CHECK THÀNH CÔNG ---
        if len(driver.find_elements(By.NAME, "pass")) > 0:
            gui_anh_tele(driver, "❌ LOGIN THẤT BẠI!")
            return

        gui_anh_tele(driver, "✅ LOGIN OK! Vào chế độ SPAM...")

        # ==========================================
        #           LOGIC SPAM (FIX LOGIC TEXT)
        # ==========================================
        
        XPATH_COMMENT_BTNS = [
            "//div[@role='button' and contains(@aria-label, 'comment')]",
            "//div[@role='button' and contains(@aria-label, 'bình luận')]",
            "//div[@role='button' and contains(., 'Bình luận')]",
            "//div[@role='button' and contains(., 'Comment')]",
            "//span[contains(text(), 'Bình luận')]",
            "//span[contains(text(), 'Comment')]"
        ]
        
        XPATH_INPUTS = [
            "//textarea[contains(@class, 'internal-input')]",
            "//textarea[contains(@placeholder, 'Viết bình luận')]",
            "//textarea[contains(@placeholder, 'Write a comment')]",
            "//div[@role='textbox']"
        ]

        XPATH_SEND = "//div[@role='button' and (@aria-label='Post a comment' or @aria-label='Đăng bình luận' or @aria-label='Gửi' or @aria-label='Post')]"

        count = 0
        while True:
            try:
                count += 1
                print(f"\n--- 🔄 Lượt quét {count} ---", flush=True)
                
                # 1. Làm mới trang
                driver.get("https://m.facebook.com/")
                time.sleep(5)
                
                # 2. Lướt tìm bài
                for i in range(3):
                    driver.execute_script(f"window.scrollBy(0, 500)")
                    time.sleep(1)
                
                # 3. Quét tìm nút Comment
                found_btn = None
                for xp in XPATH_COMMENT_BTNS:
                    btns = driver.find_elements(By.XPATH, xp)
                    if len(btns) > 0:
                        for b in btns:
                            if b.is_displayed():
                                found_btn = b
                                print(f"   + Tìm thấy nút: {xp}", flush=True)
                                break
                    if found_btn: break
                
                if found_btn:
                    # --> TÌM THẤY
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", found_btn)
                        found_btn.click()
                        time.sleep(3)
                        
                        input_box = None
                        for in_xp in XPATH_INPUTS:
                            try:
                                box = wait.until(EC.presence_of_element_located((By.XPATH, in_xp)))
                                if box.is_displayed():
                                    input_box = box
                                    break
                            except: continue
                        
                        if input_box:
                            input_box.click()
                            
                            # --- LOGIC MỚI: Tách Username ra khỏi phần biến hình ---
                            intro = random.choice(INTRO_SENTENCES)
                            
                            # 1. Biến hình nội dung spam
                            spam_content = bien_hinh_van_ban(f"{intro}\n{PRICE_LIST_BODY}")
                            
                            # 2. Ghép với Username gốc (Không biến hình)
                            final_content = f"{spam_content}{BOT_SIGNATURE}"
                            
                            print("   + Đang nhập liệu (JS Injection)...", flush=True)
                            
                            # Dùng JS để nhập (Hỗ trợ Emoji + Tiếng Việt)
                            driver.execute_script("""
                                var elm = arguments[0];
                                elm.value = arguments[1];
                                elm.dispatchEvent(new Event('input', { bubbles: true }));
                                elm.dispatchEvent(new Event('change', { bubbles: true }));
                            """, input_box, final_content)
                            
                            input_box.send_keys(" ") 
                            time.sleep(2)
                            
                            driver.find_element(By.XPATH, XPATH_SEND).click()
                            
                            print(f"   + ✅ Đã comment thành công!", flush=True)
                            gui_anh_tele(driver, f"✅ Đã Comment: {final_content[:30]}...")
                            
                            delay = random.randint(600, 900)
                            print(f"   + 💤 Ngủ {delay}s...", flush=True)
                            time.sleep(delay)
                        else:
                            print("   ! Không thấy ô nhập.", flush=True)
                            
                    except Exception as e:
                        print(f"   ! Lỗi thao tác: {e}", flush=True)
                else:
                    print("   ! Không thấy nút comment. Thử lại ngay...", flush=True)
                    time.sleep(2)

            except Exception as e:
                print(f"❌ Lỗi vòng lặp: {e}", flush=True)
                time.sleep(10)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
