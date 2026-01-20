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

PRICE_LIST_TEMPLATE = """
⭐ BẢNG GIÁ ƯU ĐÃI:
✅ 8K = 1.000 Follow Facebook
✅ 28K = 1.000 Follow TikTok
✅ 3K = 1.000 Tym TikTok
👉 Vào việc ngay tại Bot: @intro_like_bot
"""

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
        'a': ['a', 'а', 'ạ'], 'o': ['o', 'о', 'ọ'], 'e': ['e', 'е', 'ẹ'],
        'i': ['i', 'і', 'ị'], 'l': ['l', 'I', '|'], 'k': ['k', 'κ'],
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
    
    # Fake User-Agent giống ảnh bác gửi (Chrome Windows) để đồng bộ, hoặc Mobile tùy ý
    # Nhưng giữ Mobile cho nhẹ
    mobile_emulation = { "deviceName": "iPhone X" }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    return webdriver.Chrome(options=chrome_options)

def main():
    print(">>> 🚀 BOT KHỞI ĐỘNG...", flush=True)
    email = os.environ["FB_EMAIL"]
    password = os.environ["FB_PASS"]
    key_2fa = os.environ["FB_2FA_KEY"]

    driver = setup_driver()
    wait = WebDriverWait(driver, 20)
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
                break
            except:
                continue
        
        try: driver.find_element(By.NAME, "pass").send_keys(Keys.ENTER)
        except: pass
        
        print(">>> ⏳ Chờ 10s...", flush=True)
        time.sleep(10)
        
        # --- XỬ LÝ 2FA (CODE MỚI - FIX GIAO DIỆN BLOKS) ---
        print(">>> 🕵️ Đang quét màn hình 2FA...", flush=True)
        
        # 1. Tìm ô nhập 2FA (Quét tất cả input text/number)
        fa_input = None
        try:
            # Tìm tất cả thẻ input
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                # Lọc ra các ô input có thể nhập liệu (text, number, tel, password)
                inp_type = inp.get_attribute("type")
                if inp_type in ["text", "number", "tel", "password"]:
                    # Nếu là ô password chính thì bỏ qua, còn lại khả năng cao là ô 2FA
                    if inp.get_attribute("name") != "pass":
                        fa_input = inp
                        break
        except:
            pass
        
        # Nếu cách trên không được, thử XPath cụ thể
        if not fa_input:
            fa_xpaths = [
                "//input[@name='approvals_code']",
                "//input[@placeholder='Code']", 
                "//input[@aria-label='Code']",
                "//input[@type='tel']"
            ]
            for xp in fa_xpaths:
                try:
                    fa_input = driver.find_element(By.XPATH, xp)
                    break
                except:
                    continue

        if fa_input:
            otp = get_2fa_code(key_2fa)
            gui_anh_tele(driver, f"🔥 Tìm thấy ô nhập 2FA! Đang điền OTP: {otp}")
            print(f">>> 🔥 Nhập OTP: {otp}", flush=True)
            
            fa_input.click()
            fa_input.send_keys(otp)
            time.sleep(2)
            
            # 2. Bấm nút Continue (Dựa trên ảnh bác gửi: div role=button aria-label=Continue)
            print(">>> 🕵️ Tìm nút Continue...", flush=True)
            submit_success = False
            submit_xpaths = [
                "//div[@role='button' and @aria-label='Continue']",  # Chuẩn English
                "//div[@role='button' and @aria-label='Tiếp tục']",  # Chuẩn Tiếng Việt
                "//span[contains(text(), 'Continue')]",
                "//span[contains(text(), 'Tiếp tục')]",
                "//button[@type='submit']", 
                "//button[@id='checkpointSubmitButton']"
            ]
            
            for btn_xp in submit_xpaths:
                try:
                    btn = driver.find_element(By.XPATH, btn_xp)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(1)
                    btn.click()
                    print(f">>> ✅ Đã bấm nút: {btn_xp}", flush=True)
                    submit_success = True
                    break
                except:
                    continue
            
            if not submit_success:
                # Đường cùng thì Enter
                fa_input.send_keys(Keys.ENTER)
            
            time.sleep(10)
            gui_anh_tele(driver, "📸 Kết quả sau khi nhập 2FA")
        else:
            gui_anh_tele(driver, "⚠️ Không tìm thấy ô nhập 2FA (Có thể đã vào thẳng?)")

        # --- CHECK LẠI LẦN CUỐI ---
        if len(driver.find_elements(By.NAME, "pass")) > 0 or len(driver.find_elements(By.NAME, "login")) > 0:
            gui_anh_tele(driver, "❌ LOGIN THẤT BẠI: Bị đá về trang Login!")
            print(">>> 🛑 Dừng Bot.", flush=True)
            return

        gui_anh_tele(driver, "✅ LOGIN THÀNH CÔNG! Đi spam...")

        # --- SPAM ---
        XPATH_FEED_COMMENT_BTN = "//div[@role='button' and (contains(., 'Bình luận') or contains(., 'Comment'))]"
        XPATH_INPUT = "//textarea[contains(@class, 'internal-input')]"
        XPATH_SEND = "//div[@role='button' and (@aria-label='Post a comment' or @aria-label='Đăng bình luận' or @aria-label='Gửi')]"

        count = 0
        while True:
            try:
                count += 1
                print(f"\n--- 🔄 Lượt {count} ---", flush=True)
                driver.get("https://m.facebook.com/")
                time.sleep(5)
                
                scroll_times = random.randint(3, 5)
                for i in range(scroll_times):
                    driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)})")
                    time.sleep(1)
                
                buttons = driver.find_elements(By.XPATH, XPATH_FEED_COMMENT_BTN)
                
                if len(buttons) > 0:
                    chosen_btn = random.choice(buttons)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen_btn)
                    chosen_btn.click()
                    time.sleep(3)
                    
                    try:
                        input_box = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_INPUT)))
                        input_box.click()
                        
                        intro = random.choice(INTRO_SENTENCES)
                        full_content = f"{intro}\n{PRICE_LIST_TEMPLATE}"
                        final_content = bien_hinh_van_ban(full_content)
                        
                        input_box.send_keys(final_content)
                        time.sleep(2)
                        
                        driver.find_element(By.XPATH, XPATH_SEND).click()
                        print(f"   + ✅ Đã comment!", flush=True)
                        gui_anh_tele(driver, f"✅ Đã Comment thành công (Lượt {count})")
                    except Exception as e:
                        gui_anh_tele(driver, f"⚠️ Lỗi nhập comment: {e}")
                else:
                    gui_anh_tele(driver, f"⚠️ Không thấy nút comment (Lượt {count})")

                delay = random.randint(480, 720)
                print(f"   + 💤 Ngủ {delay}s...", flush=True)
                time.sleep(delay)

            except Exception as e:
                gui_anh_tele(driver, f"❌ Lỗi vòng lặp: {e}")
                time.sleep(60)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
