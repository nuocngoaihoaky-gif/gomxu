import time
import random
import os
import sys
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

def setup_driver():
    print(">>> 🛠️ Đang khởi tạo Driver...", flush=True)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Fake User-Agent xịn để Cookie đỡ bị nhả
    chrome_options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1")
    
    mobile_emulation = { "deviceName": "iPhone X" }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    return webdriver.Chrome(options=chrome_options)

def main():
    print(">>> 🚀 BOT KHỞI ĐỘNG (CHẾ ĐỘ COOKIE)...", flush=True)

    # Lấy Cookie từ Secret
    cookie_string = os.environ.get("FB_COOKIE")
    if not cookie_string:
        print(">>> ❌ LỖI: Chưa cấu hình Secret 'FB_COOKIE'!", flush=True)
        return

    driver = setup_driver()
    wait = WebDriverWait(driver, 20)

    try:
        # 1. Truy cập trang chủ trước để kích hoạt domain
        print(">>> 🌐 Đang mở m.facebook.com...", flush=True)
        driver.get("https://m.facebook.com/")
        
        # 2. Bơm Cookie vào trình duyệt
        print(">>> 🍪 Đang bơm Cookie...", flush=True)
        try:
            # Xử lý chuỗi cookie: "key=value; key=value"
            for item in cookie_string.split(';'):
                if '=' in item:
                    name, value = item.strip().split('=', 1)
                    driver.add_cookie({
                        'name': name,
                        'value': value,
                        'domain': '.facebook.com',
                        'path': '/'
                    })
            print(">>> ✅ Đã Add Cookie thành công.", flush=True)
        except Exception as e:
            print(f">>> ❌ Lỗi khi add cookie: {e}", flush=True)

        # 3. F5 lại trang để Cookie có hiệu lực
        print(">>> 🔄 Refresh trang để đăng nhập...", flush=True)
        driver.get("https://m.facebook.com/")
        time.sleep(5)

        # 4. Kiểm tra xem đã vào được chưa
        print(">>> 📸 Chụp ảnh kiểm tra Login...", flush=True)
        driver.save_screenshot("debug_cookie_login.png")
        
        # Nếu vẫn thấy nút Đăng nhập hoặc ô Pass -> Cookie chết hoặc IP bị chặn
        if len(driver.find_elements(By.NAME, "login")) > 0 or len(driver.find_elements(By.NAME, "pass")) > 0:
            print(">>> ❌ THẤT BẠI: Cookie đã hết hạn hoặc bị Facebook đá ra.", flush=True)
            print(">>> 🛑 Vui lòng lấy Cookie mới và update lại Secret.", flush=True)
            return
        
        print(">>> ✅ LOGIN THÀNH CÔNG! BẮT ĐẦU ĐI SPAM...", flush=True)

        # --- CODE LƯỚT FEED & SPAM (Giữ nguyên) ---
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
                    except Exception as e:
                        print(f"   ! Lỗi nhập liệu (Có thể bài viết bị khóa cmt): {e}", flush=True)
                else:
                    print("   ! Không thấy nút comment (Có thể Newsfeed chưa load).", flush=True)
                    driver.save_screenshot(f"debug_no_btn_{count}.png")

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
