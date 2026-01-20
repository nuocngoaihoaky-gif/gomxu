import time
import random
import os
import pyotp
import sys
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

    try:
        print(">>> 📱 Đang truy cập m.facebook.com...", flush=True)
        driver.get("https://m.facebook.com/")
        
        # --- LOGIN ---
        print(">>> 🔐 Đang nhập thông tin...", flush=True)
        
        try:
            # Tìm ô email (thử nhiều kiểu)
            try:
                email_box = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            except:
                email_box = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            
            # Xóa dữ liệu cũ trước khi nhập (Fix lỗi nhập đè)
            email_box.clear()
            email_box.send_keys(email)
            
            pass_box = driver.find_element(By.NAME, "pass")
            pass_box.clear()
            pass_box.send_keys(password)
            
            print("   + Đã điền Email/Pass.", flush=True)
        except Exception as e:
            print(f"   ! Cảnh báo nhập liệu: {e}", flush=True)

        # BẤM NÚT LOGIN
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
            print(">>> ⚠️ Không click được nút nào, thử Enter...", flush=True)
            try:
                driver.find_element(By.NAME, "pass").send_keys(Keys.ENTER)
            except:
                pass
        
        print(">>> ⏳ Đang chờ Facebook phản hồi (10s)...", flush=True)
        time.sleep(10) # Chờ mạng load

        # --- CHECK 2FA ---
        try:
            # Kiểm tra xem có ô nhập 2FA không
            input_code = driver.find_element(By.NAME, "approvals_code")
            print(">>> 🔥 Phát hiện màn hình 2FA!", flush=True)
            
            otp = get_2fa_code(key_2fa)
            print(f"   + Mã OTP: {otp}", flush=True)
            input_code.send_keys(otp)
            time.sleep(1)
            
            # Bấm gửi 2FA
            try:
                driver.find_element(By.XPATH, "//button[@type='submit' or @name='submit[Submit_code]']").click()
                print("   + Đã bấm gửi mã 2FA.", flush=True)
            except:
                driver.find_element(By.ID, "checkpointSubmitButton").click()
            
            time.sleep(8)
        except:
            print(">>> ℹ️ Không thấy ô nhập 2FA (Có thể vào thẳng hoặc LOGIN THẤT BẠI).", flush=True)

        # --- [QUAN TRỌNG] KIỂM TRA ĐÃ VÀO ĐƯỢC CHƯA ---
        print(">>> 📸 CHỤP ẢNH MÀN HÌNH ĐỂ DEBUG...", flush=True)
        driver.save_screenshot("debug_after_login.png")
        
        # Nếu vẫn còn thấy ô nhập mật khẩu -> Login thất bại
        if len(driver.find_elements(By.NAME, "pass")) > 0:
            print(">>> ❌ CẢNH BÁO: Vẫn thấy ô mật khẩu! Đăng nhập thất bại (Sai pass hoặc bị chặn).", flush=True)
            print(">>> 🛑 DỪNG BOT. HÃY KIỂM TRA ẢNH 'debug_after_login.png'", flush=True)
            return

        print(">>> ✅ Kiểm tra sơ bộ OK (Đã qua màn hình Login). Bắt đầu lướt...", flush=True)

        # --- CODE LƯỚT FEED & SPAM ---
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
                print(f"   + Tìm thấy {len(buttons)} nút comment.", flush=True)
                
                if len(buttons) > 0:
                    chosen_btn = random.choice(buttons)
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen_btn)
                    chosen_btn.click()
                    time.sleep(3)
                    
                    input_box = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_INPUT)))
                    input_box.click()
                    
                    intro = random.choice(INTRO_SENTENCES)
                    full_content = f"{intro}\n{PRICE_LIST_TEMPLATE}"
                    final_content = bien_hinh_van_ban(full_content)
                    
                    input_box.send_keys(final_content)
                    time.sleep(2)
                    
                    driver.find_element(By.XPATH, XPATH_SEND).click()
                    print(f"   + ✅ Đã comment!", flush=True)
                else:
                    print("   ! Không thấy nút comment (Hãy xem ảnh debug).", flush=True)
                    # Chụp ảnh khi không thấy nút comment để biết tại sao
                    driver.save_screenshot(f"debug_no_button_{count}.png")

                delay = random.randint(480, 720)
                print(f"   + 💤 Ngủ {delay}s...", flush=True)
                time.sleep(delay)

            except Exception as e:
                print(f"❌ Lỗi: {e}", flush=True)
                time.sleep(60)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
