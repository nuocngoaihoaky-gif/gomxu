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

# ==============================================================================
# 1. KHO TÀNG CONTENT ĐẢO NGỮ
# ==============================================================================

INTRO_STRUCTURES = [
    "{d} đang cần {a} {c} {b} thì ghé bên mình nhé.",
    "{a} {c} {b} cho {d} đang cần đẩy đơn.",
    "Bên mình chuyên {a} các gói {c} {b} nhất thị trường.",
    "Có {d} nào đang tìm nguồn {c} {b} không ạ?",
    "Mách nhỏ {d} chỗ {a} {c} cực kỳ {b} đây.",
    "Hệ thống {a} {c} {b} hoạt động 24/7 cho {d}.",
    "Ké bài chút, bên em nhận {a} {c} {b} bảo hành trọn đời.",
    "Giải pháp {c} {b} giúp {d} tăng tương tác ngay lập tức.",
    "Không cần tìm đâu xa, ở đây có {c} {b} bao ngon.",
    "Dịch vụ {c} {b} - {a} nhiệt tình cho {d}.",
    "Chấm bài xin phép admin, mình nhận {a} {c} giá học sinh.",
    "{d} muốn profile đẹp thì ib, bên mình {a} full dịch vụ.",
    "Xả kho {c} giá hủy diệt, {a} ngay trong ngày.",
    "Acc clone đi dạo, tiện tay share kèo {c} {b}.",
    "Tool {c} {b} mới update, {d} vào test thử nhé.",
    "Chuyên cung cấp {c} cho các shop, cam kết {b}.",
    "Ai cần {c} để bật kiếm tiền/livestream thì ới em.",
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
    [
        "⭐ BẢNG GIÁ NIÊM YẾT:",
        "✅ Follow FB cá nhân: 8k/1k",
        "✅ Follow TikTok: 28k/1k",
        "✅ Tim TikTok: 3k/1k",
    ],
    [
        "🔥 DEAL HỜI HÔM NAY:",
        "➡️ Tăng 1k Sub Phở Bò = 8k",
        "➡️ Tăng 1k Fl Tóp Tóp = 28k",
        "➡️ Tăng 1k Tym Tóp Tóp = 3k",
    ],
    [
        "Báo giá dịch vụ nhanh:",
        "- Facebook Follow: 8.000đ / 1000 sub",
        "- TikTok Follow: 28.000đ / 1000 sub",
        "- TikTok Heart: 3.000đ / 1000 tym",
    ],
    [
        "💎 SERVICE LIST:",
        "🔹 FB Follow >> 8k (Min 1k)",
        "🔹 Tik Follow >> 28k (Min 1k)",
        "🔹 Tik Heart >> 3k (Min 1k)",
    ],
    [
        "⚡ Xả kho tương tác giá sỉ:",
        "+ Sub Face 8k/1k",
        "+ Fl Tik 28k/1k",
        "+ Tim Tik 3k/1k",
    ],
    [
        "🌟 UPDATE GIÁ MỚI NHẤT:",
        "★ Sub xanh Facebook: 8k / 1k",
        "★ Follow TikTok việt: 28k / 1k",
        "★ Like/Tim TikTok: 3k / 1k",
    ]
]

CTA_LINES = [
    "👉 Vào việc ngay tại App Telegram, tìm: {bot}",
    "👉 Bác tải Tele về rồi tìm user: {bot}",
    "👉 Hệ thống tự động 24/7 trên Tele: {bot}",
    "👉 Search Telegram: {bot} là ra em nhé.",
    "👉 Anh em qua Telegram tìm bot: {bot}",
    "👉 Nhắn tin qua Telegram: {bot}",
    "👉 Bot tự động bên Tele: {bot}",
    "👉 Mọi giao dịch qua Telegram: {bot}",
]

def gen_intro():
    s = random.choice(INTRO_STRUCTURES)
    return s.format(
        a=random.choice(INTRO_WORDS["a"]),
        b=random.choice(INTRO_WORDS["b"]),
        c=random.choice(INTRO_WORDS["c"]),
        d=random.choice(INTRO_WORDS["d"]),
    )

def gen_price():
    return "\n".join(random.choice(PRICE_BLOCKS))

def gen_cta(bot="@intro_like_bot"):
    return random.choice(CTA_LINES).format(bot=bot)

# ==============================================================================
# 2. CÁC HÀM HỖ TRỢ BOT
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
    except:
        pass

def bien_hinh_van_ban(text):
    confusables = {
        'a': ['а'], 'o': ['о'], 'e': ['е'], 'c': ['с'], 'p': ['р'], 
        'x': ['х'], 'y': ['у'], 'T': ['Т'], 'H': ['Н'], 'B': ['В'],
        'K': ['К'], 'M': ['М'], 'A': ['А'], 'O': ['О'], 'E': ['Е'],
        'C': ['С'], 'P': ['Р'], 'X': ['Х']
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
    
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    chrome_options.add_argument(f'--user-agent={ua}')
    
    mobile_emulation = { "deviceName": "iPhone X", "userAgent": ua }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    return webdriver.Chrome(options=chrome_options)

# ==============================================================================
# 3. HÀM TƯƠNG TÁC DẠO (CHUẨN CODE SOI TỪ ẢNH)
# ==============================================================================

def tuong_tac_dao(driver):
    print("\n--- 🤸 BẮT ĐẦU CHẾ ĐỘ 'ĐI DẠO & THẢ TIM' ---", flush=True)
    try:
        # Lướt sương sương 3-5 lần
        scroll_times = random.randint(3, 5)
        interacted = False # Cờ đánh dấu đã tương tác chưa
        
        for i in range(scroll_times):
            # Cuộn trang ngẫu nhiên
            driver.execute_script(f"window.scrollBy(0, {random.randint(600, 900)})")
            time.sleep(random.randint(3, 5))
            
            # CHỈ TƯƠNG TÁC 1 LẦN DUY NHẤT TRONG 1 PHIÊN ĐI DẠO (Tỉ lệ 40%)
            if not interacted and random.random() > 0.6:
                
                # 1. TÌM NÚT LIKE CHÍNH (Theo ảnh 1 bác gửi)
                # Tìm thẻ div có role='button' và aria-label chứa 'like' (thường/hoa) hoặc 'thích'
                main_like_xpaths = [
                    "//div[@role='button' and contains(@aria-label, 'like')]", 
                    "//div[@role='button' and contains(@aria-label, 'Like')]",
                    "//div[@role='button' and contains(@aria-label, 'thích')]",
                    "//div[@role='button' and contains(@aria-label, 'Thích')]"
                ]
                
                found_btn = None
                for xp in main_like_xpaths:
                    btns = driver.find_elements(By.XPATH, xp)
                    if len(btns) > 0:
                        for b in btns:
                            if b.is_displayed():
                                found_btn = b
                                break
                    if found_btn: break
                
                if found_btn:
                    # Cuộn tới nút Like
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", found_btn)
                    time.sleep(1)
                    
                    # QUYẾT ĐỊNH: 50% Thả Tim/Haha (Nhấn giữ) - 50% Like thường (Click)
                    if random.random() > 0.5:
                        print("   + 🖱️ Đang nhấn giữ để thả cảm xúc...", flush=True)
                        try:
                            # Hành động: Nhấn giữ 1.5 giây để hiện bảng cảm xúc
                            actions = ActionChains(driver)
                            actions.move_to_element(found_btn).click_and_hold().perform()
                            time.sleep(2) # Chờ bảng hiện ra (Quan trọng)
                            
                            # 2. TÌM NÚT CẢM XÚC (Theo ảnh 2 bác gửi: Love, Care, Haha...)
                            # Code trong ảnh là Tiếng Anh (Love, Care...), nhưng mình cứ thủ thêm Tiếng Việt cho chắc
                            reaction_xpaths = [
                                "//div[@role='button' and @aria-label='Love']",
                                "//div[@role='button' and @aria-label='Yêu thích']",
                                "//div[@role='button' and @aria-label='Care']",
                                "//div[@role='button' and @aria-label='Thương thương']",
                                "//div[@role='button' and @aria-label='Haha']",
                                "//div[@role='button' and @aria-label='Wow']"
                            ]
                            
                            # Quét xem cái nào hiện ra thì bấm
                            visible_reacts = []
                            for rxp in reaction_xpaths:
                                r_btns = driver.find_elements(By.XPATH, rxp)
                                for r in r_btns:
                                    if r.is_displayed():
                                        visible_reacts.append(r)
                            
                            if len(visible_reacts) > 0:
                                chosen = random.choice(visible_reacts)
                                react_type = chosen.get_attribute("aria-label")
                                chosen.click() # BẤM LUÔN
                                
                                # Nhả chuột ra sau khi bấm
                                actions.release().perform()
                                print(f"   + 😍 Đã thả cảm xúc: {react_type}", flush=True)
                                interacted = True
                            else:
                                # Nếu nhấn giữ mà ko ra bảng -> Click thường (Like)
                                print("   + ⚠️ Không thấy bảng cảm xúc -> Click Like thường.", flush=True)
                                actions.release().perform() # Nhả ra trước
                                found_btn.click()
                                interacted = True
                                
                        except Exception as e:
                            print(f"   ! Lỗi thả cảm xúc: {e}", flush=True)
                            # Lỗi thì thử click thường vớt vát
                            try: found_btn.click()
                            except: pass
                    else:
                        # Like thường
                        try:
                            found_btn.click()
                            print("   + 👍 Đã Like thường.", flush=True)
                            interacted = True
                        except: pass
            
            # Nếu đã tương tác rồi thì các lần lướt sau chỉ lướt thôi, ko bấm nữa
            
    except Exception as e:
        print(f"   ! Lỗi đi dạo: {e}", flush=True)
    
    print("--- ✅ KẾT THÚC ĐI DẠO ---\n", flush=True)

# ==============================================================================
# 4. MAIN LOOP
# ==============================================================================

def main():
    print(">>> 🚀 BOT KHỞI ĐỘNG...", flush=True)
    email = os.environ["FB_EMAIL"]
    password = os.environ["FB_PASS"]
    key_2fa = os.environ["FB_2FA_KEY"]

    driver = setup_driver()
    wait = WebDriverWait(driver, 30)

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
        
        # --- XỬ LÝ 2FA ---
        print(">>> 🕵️ Kiểm tra 2FA...", flush=True)
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

        if len(driver.find_elements(By.NAME, "pass")) > 0:
            gui_anh_tele(driver, "❌ LOGIN THẤT BẠI!")
            return

        gui_anh_tele(driver, "✅ LOGIN OK! Vào chế độ SPAM AN TOÀN...")

        # ==========================================
        #           LOGIC SPAM (LOOP)
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
                
                driver.get("https://m.facebook.com/")
                time.sleep(5)
                
                # --- ĐI DẠO ---
                tuong_tac_dao(driver)
                
                # --- TÌM BÀI COMMENT ---
                found_btn = None
                for i in range(2): # Lướt thêm 1 xíu
                    driver.execute_script(f"window.scrollBy(0, 600)")
                    time.sleep(2)
                    for xp in XPATH_COMMENT_BTNS:
                        btns = driver.find_elements(By.XPATH, xp)
                        if len(btns) > 0:
                            for b in btns:
                                if b.is_displayed():
                                    found_btn = b
                                    print(f"   + Tìm thấy nút: {xp}", flush=True)
                                    break
                        if found_btn: break
                    if found_btn: break
                
                if found_btn:
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
                            
                            intro_text = gen_intro()
                            price_text = gen_price()
                            part1_obfuscated = bien_hinh_van_ban(f"{intro_text}\n{price_text}")
                            part2_cta = gen_cta(bot="@intro_like_bot")
                            final_content = f"{part1_obfuscated}\n{part2_cta}"
                            
                            print("   + Đang nhập liệu...", flush=True)
                            
                            driver.execute_script("""
                                var elm = arguments[0];
                                elm.value = arguments[1];
                                elm.dispatchEvent(new Event('input', { bubbles: true }));
                                elm.dispatchEvent(new Event('change', { bubbles: true }));
                            """, input_box, final_content)
                            
                            input_box.send_keys(" ") 
                            time.sleep(2)
                            
                            driver.find_element(By.XPATH, XPATH_SEND).click()
                            time.sleep(5)
                            
                            page_source = driver.page_source
                            if "You're temporarily blocked" in page_source or "Bạn tạm thời bị chặn" in page_source:
                                print(">>> ❌ ACC BỊ CHẶN TÍNH NĂNG! DỪNG BOT.", flush=True)
                                gui_anh_tele(driver, "❌ BÁO ĐỘNG: ACC BỊ CHẶN COMMENT! ĐÃ TẮT BOT.")
                                return

                            print(f"   + ✅ Đã comment thành công!", flush=True)
                            preview_text = final_content.replace("\n", " ")[:50]
                            gui_anh_tele(driver, f"✅ Đã Comment: {preview_text}...")
                            
                            # Ngủ dài 50-70p
                            delay = random.randint(3000, 4200) 
                            print(f"   + 💤 Ngủ {delay}s (~{int(delay/60)} phút)...", flush=True)
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
