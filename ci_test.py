import asyncio
import requests
import time
import urllib.parse
import os
import base64
from telethon import TelegramClient
from telethon.tl.functions.messages import RequestWebViewRequest

# ==========================================
# CONFIGURATION
# ==========================================
CLOUD_ID = int(os.environ.get('AWS_CLUSTER_ID', '0'))
CLOUD_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
ALERT_CONTACT = os.environ.get('ALERT_NOTIFICATION_SMS', '')

SYS_CACHE_FILE = 'monitor_cache' 

# [SỬA] Cập nhật đúng tên Bot: GomXu_Bot -> R29tWHVfQm90
TARGET_SERVICE = base64.b64decode("R29tWHVfQm90").decode() 
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
# CORE PROTOCOLS
# ==========================================
async def init_cluster_handshake():
    print(f"[{time.strftime('%H:%M:%S')}] 🔄 Connecting to Secure Storage...", flush=True)
    
    client = TelegramClient(SYS_CACHE_FILE, CLOUD_ID, CLOUD_KEY)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ LỖI: Session không hợp lệ!", flush=True)
            await client.disconne9019
            
        except Exception as e:
            print(f"❌ Main Loop Error: {e}", flush=True)
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main_process())
