import time
import random
import os
import sys
import requests # Thư viện để gửi tin nhắn Telegram
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

# --- HÀM GỬI TELEGRAM ---
def gui_anh_tele(driver, caption="Ảnh chụp màn hình"):
    try:
        token = os.environ.get("TELEGRAM_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id:
            print(">>> ⚠️ Chưa cấu hình Telegram Token/Chat ID", flush=True)
            return

        # 1. Chụp ảnh lưu tạm
        filename = "temp_screenshot.png"
        driver.save_screenshot(filename)
        
        # 2. Gửi ảnh
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        with open(filename, 'rb') as photo:
            files = {'photo': photo}
            data = {'chat_id': chat_id, 'caption': caption}
            requests.post(url, files=files, data=data)
            
        print(f">>> 📡 Đã gửi ảnh về Tele: {caption}", flush=True)
        
    except Exception as e:
        print(f">>> ❌ Lỗi gửi Telegram: {e}", flush=True)

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
    
    # Báo cáo mở máy
    gui_anh_tele(driver, "🚀 Bot bắt đầu chạy trên GitHub!")

    try:
        print(">>> 📱 Đang truy cập m.facebook.com...", flush=True)
        driver.get("https://m.facebook.com/")
        
        # --- LOGIN ---
        print(">>> 🔐 Đang nhập thông tin...", flush=True)
        
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
            
            # CHỤP ẢNH SAU KHI ĐIỀN
            gui_anh_tele(driver, "🔐 Đã điền User/Pass, chuẩn bị bấm Login")
            
        except Exception as e:
            print(f"   ! Lỗi nhập liệu: {e}", flush=True)
            gui_anh_tele(driver, f"❌ Lỗi không thấy ô nhập: {e}")

        # BẤM LOGIN
        print(">>> 🔎 Đang bấm nút Login...", flush=True)
        login_success = False
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
                print(f">>> ✅ Đã Click nút: {xpath}", flush=True)
                login_success = True
                break
            except:
                continue
        
        if not login_success:
            print(">>> ⚠️ Thử Enter...", flush=True)
            try:
                driver.find_element(By.NAME, "pass").send_keys(Keys.ENTER)
            except:
                pass
        
        print(">>> ⏳ Đang chờ 10s...", flush=True)
        time.sleep(10)
        
        # CHỤP ẢNH KẾT QUẢ LOGIN
        gui_anh_tele(driver, "📸 Kết quả sau khi bấm Login (Check xem vào được chưa?)")

        # --- 2FA ---
        try:
            input_code = driver.find_element(By.NAME, "approvals_code")
            print(">>> 🔥 Phát hiện màn hình 2FA!", flush=True)
            gui_anh_tele(driver, "🔥 Đang ở màn hình 2FA, đang lấy mã...")
            
            otp = get_2fa_code(key_2fa)
            input_code.send_keys(otp)
            time.sleep(1)
            
            try:
                driver.find_element(By.XPATH, "//button[@type='submit' or @name='submit[Submit_code]']").click()
            except:
                driver.find_element(By.ID, "checkpointSubmitButton").click()
            
            time.sleep(8)
            gui_anh_tele(driver, "✅ Đã nhập xong 2FA")
        except:
            pass # Không có 2FA hoặc lỗi

        # --- CHECK LẠI LẦN CUỐI ---
        if len(driver.find_elements(By.NAME, "pass")) > 0:
            gui_anh_tele(driver, "❌ LOGIN THẤT BẠI: Vẫn còn ô nhập mật khẩu!")
            print(">>> 🛑 Dừng Bot.", flush=True)
            return

        gui_anh_tele(driver, "✅ LOGIN THÀNH CÔNG! Bắt đầu đi spam...")

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
