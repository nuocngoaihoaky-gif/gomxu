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
    
    # --- FIX LỖI MÀN HÌNH TRẮNG ---
    # Ép buộc kích thước cửa sổ để không bị lỗi render 0x0
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
    wait = WebDriverWait(driver, 30) # Tăng time chờ lên 30s
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

        # BẤM LOGIN (Sửa lại logic: Bấm được là thôi, không Enter nữa)
        print(">>> 🔎 Đang bấm nút Login...", flush=True)
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
                print(f">>> ✅ Đã bấm nút: {xpath}", flush=True)
                login_clicked = True
                break
            except:
                continue
        
        # Chỉ Enter nếu chưa bấm được nút nào (Tránh spam lệnh làm trắng trang)
        if not login_clicked:
            print(">>> ⚠️ Thử Enter...", flush=True)
            try: driver.find_element(By.NAME, "pass").send_keys(Keys.ENTER)
            except: pass
        
        print(">>> ⏳ Chờ 15s để load trang 2FA...", flush=True)
        time.sleep(15) # Tăng time chờ load
        
        # --- XỬ LÝ 2FA ---
        print(">>> 🕵️ Đang quét màn hình 2FA...", flush=True)
        
        # Thử tìm ô nhập bằng nhiều cách
        fa_input = None
        
        # Cách 1: Tìm ô input có type='number' hoặc 'tel' (Thường là ô 2FA)
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                if inp.get_attribute("type") in ["tel", "number"]:
                    fa_input = inp
                    break
        except: pass

        # Cách 2: Tìm theo placeholder hoặc name
        if not fa_input:
            fa_xpaths = [
                "//input[@name='approvals_code']",
                "//input[@placeholder='Code']", 
                "//input[@placeholder='Mã']",
                "//input[@aria-label='Code']"
            ]
            for xp in fa_xpaths:
                try:
                    fa_input = driver.find_element(By.XPATH, xp)
                    break
                except: continue

        if fa_input:
            otp = get_2fa_code(key_2fa)
            gui_anh_tele(driver, f"🔥 Tìm thấy ô 2FA! Nhập: {otp}")
            print(f">>> 🔥 Nhập OTP: {otp}", flush=True)
            
            fa_input.click()
            fa_input.send_keys(otp)
            time.sleep(2)
            
            # Tìm nút Tiếp tục
            print(">>> 🕵️ Bấm Tiếp tục...", flush=True)
            submit_success = False
            submit_xpaths = [
                "//div[@role='button' and @aria-label='Continue']",
                "//div[@role='button' and @aria-label='Tiếp tục']",
                "//button[@type='submit']", 
                "//button[@id='checkpointSubmitButton']"
            ]
            for btn_xp in submit_xpaths:
                try:
                    driver.find_element(By.XPATH, btn_xp).click()
                    submit_success = True
                    break
                except: continue
            
            if not submit_success: fa_input.send_keys(Keys.ENTER)
            
            time.sleep(10)
            gui_anh_tele(driver, "📸 Sau khi nhập 2FA")
        else:
            # NẾU KHÔNG THẤY Ô NHẬP -> IN RA HTML ĐỂ BIẾT TRANG GÌ
            print(">>> ⚠️ KHÔNG THẤY Ô 2FA. ĐANG Ở TRANG NÀO?", flush=True)
            try:
                # In tiêu đề và nội dung trang web ra log để đọc
                page_title = driver.title
                page_body = driver.find_element(By.TAG_NAME, "body").text[:500] # Lấy 500 chữ đầu
                print(f"   + Title: {page_title}", flush=True)
                print(f"   + Body Text: {page_body}", flush=True)
                
                gui_anh_tele(driver, f"⚠️ Lỗi tìm ô 2FA. Web hiện chữ: {page_body[:100]}...")
            except:
                pass

        # --- CHECK THÀNH CÔNG ---
        # Kiểm tra xem có bị đá về Login không
        if len(driver.find_elements(By.NAME, "pass")) > 0:
            gui_anh_tele(driver, "❌ LOGIN THẤT BẠI: Vẫn ở trang Login!")
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
                        gui_anh_tele(driver, f"✅ Đã Comment (Lượt {count})")
                    except Exception as e:
                        gui_anh_tele(driver, f"⚠️ Lỗi nhập: {e}")
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
