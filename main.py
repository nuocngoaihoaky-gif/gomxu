import time
import random
import os
import pyotp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")
    # Giả lập iPhone X
    mobile_emulation = { "deviceName": "iPhone X" }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    return webdriver.Chrome(options=chrome_options)

def main():
    email = os.environ["FB_EMAIL"]
    password = os.environ["FB_PASS"]
    key_2fa = os.environ["FB_2FA_KEY"]

    driver = setup_driver()
    wait = WebDriverWait(driver, 15)

    try:
        print(">>> 📱 Đang vào m.facebook.com...")
        driver.get("https://m.facebook.com/")
        
        # --- LOGIN ---
        print(">>> 🔐 Đang đăng nhập...")
        
        # Nhập Email/Pass
        try:
            # Thử tìm input email bằng name hoặc type
            try:
                wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(email)
            except:
                 driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys(email)
            
            driver.find_element(By.NAME, "pass").send_keys(password)
        except Exception as e:
            print("! Không tìm thấy ô nhập liệu (Có thể đã login từ trước?)")

        # --- TÌM NÚT LOGIN (ĐÃ SỬA) ---
        login_success = False
        login_xpaths = [
            # 1. Kiểu Span text (Phổ biến trên GHA)
            "//span[contains(text(), 'Log in')]", 
            "//span[contains(text(), 'Log In')]",
            "//span[contains(text(), 'Đăng nhập')]",
            # 2. Kiểu Button chuẩn
            "//button[@name='login']",
            # 3. Kiểu Div Role Button
            "//div[@role='button' and (contains(., 'Log In') or contains(., 'Đăng nhập'))]",
            # 4. Kiểu Input Submit
            "//input[@value='Log In']",
            "//input[@value='Đăng nhập']"
        ]

        for xpath in login_xpaths:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(1)
                btn.click()
                print(f">>> ✅ Đã bấm nút Login: {xpath}")
                login_success = True
                break
            except:
                continue
        
        # Nếu không bấm được nút nào -> Nhấn Enter
        if not login_success:
            print(">>> ⚠️ Không thấy nút Login, thử nhấn Enter...")
            try:
                driver.find_element(By.NAME, "pass").send_keys("\n")
            except:
                pass
        
        time.sleep(5) # Chờ load sau login

        # --- 2FA ---
        try:
            print(">>> ⏳ Check 2FA...")
            input_code = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "approvals_code"))
            )
            
            otp = get_2fa_code(key_2fa)
            print(f">>> 🔥 Nhập 2FA: {otp}")
            input_code.send_keys(otp)
            time.sleep(1)
            
            # Tìm nút gửi 2FA
            xpath_2fa = [
                "//button[@type='submit']", "//input[@type='submit']",
                "//button[@id='checkpointSubmitButton']", "//button[@name='submit[Submit_code]']"
            ]
            for xp in xpath_2fa:
                try:
                    driver.find_element(By.XPATH, xp).click()
                    break
                except:
                    continue
            
            time.sleep(5)
            driver.get("https://m.facebook.com/")
        except:
            print(">>> 🚀 Vào thẳng (Không hỏi 2FA)")
        
        print(">>> ✅ Login xong. Chế độ: SPAM DẠO TỐC ĐỘ CAO (8-12p)...")

        # XPATH COMMENT (Dựa trên ảnh bác gửi)
        XPATH_FEED_COMMENT_BTN = "//div[@role='button' and (contains(., 'Bình luận') or contains(., 'Comment'))]"
        XPATH_INPUT = "//textarea[contains(@class, 'internal-input')]"
        XPATH_SEND = "//div[@role='button' and (@aria-label='Post a comment' or @aria-label='Đăng bình luận' or @aria-label='Gửi')]"

        count = 0
        while True:
            try:
                count += 1
                print(f"\n--- 🔄 Lượt chạy thứ {count} ---")
                
                # 1. Làm mới & Cuộn
                driver.get("https://m.facebook.com/")
                time.sleep(random.randint(5, 8))
                
                scroll_times = random.randint(3, 7)
                for i in range(scroll_times):
                    driver.execute_script(f"window.scrollBy(0, {random.randint(300, 700)})")
                    time.sleep(random.randint(1, 3))
                
                # 2. Tìm nút Comment
                try:
                    buttons = driver.find_elements(By.XPATH, XPATH_FEED_COMMENT_BTN)
                    
                    if len(buttons) > 0:
                        # Chọn ngẫu nhiên 1 nút
                        chosen_btn = random.choice(buttons)
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen_btn)
                        time.sleep(1)
                        chosen_btn.click()
                        time.sleep(3)
                        
                        # 3. Nhập & Gửi
                        input_box = wait.until(EC.presence_of_element_located((By.XPATH, XPATH_INPUT)))
                        input_box.click()
                        
                        intro = random.choice(INTRO_SENTENCES)
                        full_content = f"{intro}\n{PRICE_LIST_TEMPLATE}"
                        final_content = bien_hinh_van_ban(full_content)
                        
                        input_box.send_keys(final_content)
                        time.sleep(2)
                        
                        send_btn = driver.find_element(By.XPATH, XPATH_SEND)
                        send_btn.click()
                        print(f"   + ✅ Đã comment thành công!")
                        
                    else:
                        print("   ! Không thấy nút comment nào.")
                
                except Exception as e:
                    print(f"   ❌ Lỗi thao tác: {e}")
                    driver.save_screenshot(f"error_{count}.png")

                # 4. NGỦ RANDOM TỪ 8 ĐẾN 12 PHÚT
                delay = random.randint(480, 720)
                print(f"   + 💤 Ngủ {delay}s (~{delay/60:.1f} phút)...")
                time.sleep(delay)

            except Exception as e:
                print(f"❌ Lỗi vòng lặp: {e}")
                time.sleep(60)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
