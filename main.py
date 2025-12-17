import os
import requests
KEY = os.environ.get("INIT_DATA")
HEAD = {
    "content-type": "application/json",
    "origin": "https://gomxu.online",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
}
def run():
    if not KEY: return
    data = {"initData": KEY}
    try: requests.post("https://gomxu.site/mining", headers=HEAD, json=data, timeout=5)
    except: pass
    try: requests.post("https://gomxu.site/viewads", headers=HEAD, json={**data, "typeReward": "gold"}, timeout=5)
    except: pass
if __name__ == "__main__":
    run()
