import asyncio
import requests
import time
import urllib.parse
import os
import base64
from telethon import TelegramClient
from telethon.tl.functions.messages import RequestWebViewRequest

# ==========================================
# CẤU HÌNH (DEBUG MODE)
# ==========================================

CLOUD_ID = int(os.environ.get('AWS_CLUSTER_ID', '0'))
CLOUD_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
ALERT_CONTACT = os.environ.get('ALERT_NOTIFICATION_SMS', '')
SYS_CACHE_FILE = 'system_core_dump.dat' 

# Decode
TARGET_SERVICE = base64.b64decode("R29tWHVCb3Q=").decode() 
WEB_ENDPOINT = base64.b64decode("aHR0cHM6Ly9nb214dS5vbmxpbmU=").decode()
API_CLUSTER = base64.b64decode("aHR0cHM6Ly9nb214dS5zaXRl").decode()

CLUSTER_CONFIG = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": WEB_ENDPOINT,
    "referrer": f"{WEB_ENDPOINT}/",
    "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
}

# ==========================================
# HÀM LẤY TOKEN (Có Log)
# ==========================================
async def init_cluster_handshake():
    print(f"[{time.strftime('%H:%M:%S')}] 🔄 Đang kết nối lấy Token...", flush=True)
    try:
        async with TelegramClient(SYS_CACHE_FILE, CLOUD_ID, CLOUD_KEY) as monitor:
            if not await monitor.is_user_authorized():
                print("❌ Lỗi: Session chưa đăng nhập hoặc bị out!", flush=True)
                return None
            
            webview_req = await monitor(RequestWebViewRequest(
                peer=TARGET_SERVICE,
                bot=TARGET_SERVICE,
                platform='android',
                from_bot_menu=False,
                url=WEB_ENDPOINT
            ))
            
            auth_url = webview_req.url
            # Debug: In thử URL lấy được (che bớt cho đỡ dài)
            # print(f"DEBUG URL: {auth_url[:50]}...", flush=True)
            
            params = urllib.parse.parse_qs(auth_url.split('#')[1])
            token = params.get('tgWebAppData', [None])[0]
            
            if token:
                print("✅ Đã lấy được Token mới!", flush=True)
            else:
                print("❌ Không tìm thấy tgWebAppData trong URL", flush=True)
            return token
    except Exception as e:
        print(f"❌ Lỗi Telethon: {e}", flush=True)
        return None

# ==========================================
# HÀM CHẠY TEST (In kết quả Server)
# ==========================================
def execute_stress_test(access_token):
    if not access_token: return
    
    secure_packet = {"initData": access_token}

    print(f"[{time.strftime('%H:%M:%S')}] 🚀 Bắt đầu gửi Request...", flush=True)

    # 1. TEST MINING
    try:
        print("   -> Gửi lệnh Mining...", flush=True)
        res = requests.post(f"{API_CLUSTER}/mining", headers=CLUSTER_CONFIG, json=secure_packet, timeout=12)
        # IN RA KẾT QUẢ ĐỂ BẮT BỆNH
        print(f"   👉 KẾT QUẢ MINING: Code={res.status_code} | Body={res.text[:100]}", flush=True)
    except Exception as e:
        print(f"   ❌ Lỗi Mining: {e}", flush=True)

    # 2. TEST ADS
    try:
        res = requests.post(f"{API_CLUSTER}/viewads", headers=CLUSTER_CONFIG, json={**secure_packet, "typeReward": "goldCoin"}, timeout=12)
        print(f"   👉 KẾT QUẢ ADS: Code={res.status_code}", flush=True)
    except: pass

    # 3. TEST GOLD
    try:
        requests.post(f"{API_CLUSTER}/randomgold", headers=CLUSTER_CONFIG, json=secure_packet, timeout=12)
    except: pass

    # 4. CLICK LINK
    services = ["ads_monetag", "ads_hitopads"] # Test 2 cái cho nhanh
    for svc in services:
        try:
            requests.post(f"{API_CLUSTER}/clicksmartlink", headers=CLUSTER_CONFIG, json={**secure_packet, "linkKey": svc}, timeout=12)
            print(f"   -> Click Link {svc}: OK", flush=True)
            time.sleep(1)
        except: pass

# ==========================================
# MAIN LOOP
# ==========================================
async def main_process():
    print("=== BẮT ĐẦU TOOL MONITOR (DEBUG MODE) ===", flush=True)
    
    while True:
        try:
            # 1. Lấy Token
            sys_token = await init_cluster_handshake()
            
            # 2. Chạy
            if sys_token:
                execute_stress_test(sys_token)
            else:
                print("⚠️ Không có Token -> Bỏ qua vòng này.", flush=True)

            # 3. Ngủ
            print(f"💤 Ngủ 15 phút...", flush=True)
            await asyncio.sleep(905)
            
        except Exception as e:
            print(f"❌ Lỗi Main Loop: {e}", flush=True)
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main_process())
