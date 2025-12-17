import os
import requests
KEY = os.environ.get("INIT_DATA")
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "content-type": "application/json",
    "origin": "https://gomxu.online",
    "referrer": "https://gomxu.online/",
    "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
}
def run():
    if not KEY: return
    payload = {"initData": KEY}
    try:
        requests.post("https://gomxu.site/mining", headers=HEADERS, json=payload, timeout=5)
    except: pass
    try:
        data_ads = {**payload, "typeReward": "goldCoin"}
        requests.post("https://gomxu.site/viewads", headers=HEADERS, json=data_ads, timeout=5)
    except: pass
if __name__ == "__main__":
    run()
