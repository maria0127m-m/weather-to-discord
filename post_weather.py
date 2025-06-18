import requests
from datetime import datetime

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/XXX/YYY"  # ← 自分のWebhook URLに変更！

def get_image_url():
    today = datetime.utcnow().strftime('%Y%m%d')
    return f"https://www.jma.go.jp/bosai/weather_map/data/png/500hPa/{today}_00.png"

def post_to_discord():
    image_url = get_image_url()
    image_response = requests.get(image_url)

    if image_response.status_code != 200:
        print(f"❌ 画像取得失敗: {image_url}")
        return

    files = {
        "file": ("500hPa.png", image_response.content)
    }
    data = {
        "content": "📡 本日12:00 UTCの500hPa天気図（気象庁）"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
    if response.status_code == 204:
        print("✅ 投稿成功")
    else:
        print(f"⚠ 投稿失敗: {response.status_code}, {response.text}")

if __name__ == "__main__":
    post_to_discord()
