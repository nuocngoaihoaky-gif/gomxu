import time
import random
import os
import pyotp
import sys # Import thêm sys để đảm bảo output chuẩn
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
    # In ngay dòng đầu tiên để biết Bot đã chạy
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
        print(">>> 🔐 Đang nhập thông tin đăng nhập...", flush=True)
        
        # 1. Nhập Email/Pass
        try:
            try:
                email_box = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            except:
                email_box = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            
            email_box.send_keys(email)
            driver.find_element(By.NAME, "pass").send_keys(password)
            print("   + Đã điền Email/Pass.", flush=True)
        except Exception as e:
            print(f"   ! Cảnh báo nhập liệu: {e}", flush=True)

        # 2. Tìm & Bấm Nút Login
        print(">>> 🔎 Đang quét tìm nút Login...", flush=True)
        login_success = False
        login_xpaths = [
            "//span[contains(text(), 'Log in')]", 
            "//span[contains(text(), 'Log In')]",
            "//span[contains(text(), 'Đăng nhập')]",
            "//button[@name='login']",
            "//div[@role='button' and (contains(., 'Log In') or contains(., 'Đăng nhập'))]",
            "//input[@value='Log In']",
            "//input[@type='submit']"
        ]

        for xpath in login_xpaths:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(1)
                btn.click()
                print(f">>> ✅ BINGO! Đã bấm nút Login: {xpath}", flush=True)
                login_success = True
                break
            except:
                continue
        
        if not login_success:
            print(">>> ⚠️ Không thấy nút Login, thử nhấn ENTER...", flush=True)
            try:
                driver.find_element(By.NAME, "pass").send_keys(Keys.ENTER)
                login_success = True
            except:
                print(">>> ❌ Không thể nhấn Enter.", flush=True)
        
        time.sleep(8) 

        # --- XỬ LÝ 2FA ---
        try:
            print(">>> ⏳ Đang kiểm tra 2FA...", flush=True)
            input_code = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "approvals_code"))
            )
            
            otp = get_2fa_code(key_2fa)
            print(f">>> 🔥 Tìm thấy ô 2FA! Nhập mã: {otp}", flush=True)
            input_code.send_keys(otp)
            time.sleep(1)
            
            xpath_2fa = [
                "//button[@type='submit']", "//input[@type='submit']",
                "//button[@id='checkpointSubmitButton']", "//button[@name='submit[Submit_code]']"
            ]
            for xp in xpath_2fa:
                try:
                    driver.find_element(By.XPATH, xp).click()
                    print(f">>> Đã bấm gửi 2FA bằng: {xp}", flush=True)
                    break
                except:
                    continue
            
            time.sleep(8)
            driver.get("https://m.facebook.com/")
        except:
            print(">>> 🚀 Vào thẳng (Không cần 2FA hoặc đã login xong).", flush=True)
        
        print(">>> ✅ LOGIN HOÀN TẤT. CHẾ ĐỘ: LƯỚT FEED & SPAM...", flush=True)

        # XPATH CẤU HÌNH
        XPATH_FEED_COMMENT_BTN = "//div[@role='button' and (contains(., 'Bình luận') or contains(., 'Comment'))]"
        XPATH_INPUT = "//textarea[contains(@class, 'internal-input')]"
        XPATH_SEND = "//div[@role='button' and (@aria-label='Post a comment' or @aria-label='Đăng bình luận' or @aria-label='Gửi')]"

        count = 0
        while True:
            try:
                count += 1
                print(f"\n==========================================", flush=True)
                print(f"--- 🔄 LƯỢT CHẠY THỨ: {count} ---", flush=True)
                print(f"==========================================", flush=True)
                
                # 1. Làm mới & Cuộn
                driver.get("https://m.facebook.com/")
                time.sleep(random.randint(5, 8))
                
                scroll_times = random.randint(3, 7)
                print(f"   + Đang lướt {scroll_times} lần màn hình...", flush=True)
                for i in range(scroll_times):
                    driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)})")
                    time.sleep(random.randint(1, 3))
                
                # 2. Tìm nút Comment
                try:
                    buttons = driver.find_elements(By.XPATH, XPATH_FEED_COMMENT_BTN)
                    num_btns = len(buttons)
                    print(f"   + Tìm thấy {num_btns} nút 'Bình luận' trên màn hình.", flush=True)
                    
                    if num_btns > 0:
                        chosen_btn = random.choice(buttons)
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen_btn)
                        time.sleep(1)
                        chosen_btn.click()
                        print("   + Đã click mở ô bình luận.", flush=True)
                        time.sleep(3)
                        
                        # 3. Nhập & Gửi
                        print("   + Đang đợi ô nhập hiện ra...", flush=True)
                        input_box = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_INPUT)))
                        input_box.click()
                        
                        intro = random.choice(INTRO_SENTENCES)
                        full_content = f"{intro}\n{PRICE_LIST_TEMPLATE}"
                        final_content = bien_hinh_van_ban(full_content)
                        
                        input_box.send_keys(final_content)
                        print("   + Đã nhập nội dung (đã biến hình).", flush=True)
                        time.sleep(2)
                        
                        send_btn = driver.find_element(By.XPATH, XPATH_SEND)
                        send_btn.click()
                        print(f"   + ✅ ĐÃ COMMENT THÀNH CÔNG!", flush=True)
                        
                    else:
                        print("   ! Không thấy nút comment nào (Có thể do mạng lag hoặc toàn quảng cáo).", flush=True)
                
                except Exception as e:
                    print(f"   ❌ Lỗi thao tác comment: {e}", flush=True)
                    try:
                        driver.save_screenshot(f"error_{count}.png")
                    except:
                        pass

                # 4. NGỦ
                delay = random.randint(480, 720)
                print(f"   + 💤 BOT ĐANG NGỦ {delay} GIÂY (~{delay/60:.1f} phút)...", flush=True)
                time.sleep(delay)

            except Exception as e:
                print(f"❌ LỖI VÒNG LẶP CHÍNH: {e}", flush=True)
                print("   + Tạm nghỉ 60s rồi thử lại...", flush=True)
                time.sleep(60)

    finally:
        driver.quit()
        print(">>> 🛑 DRIVER ĐÃ ĐÓNG.", flush=True)

if __name__ == "__main__":
    main()
