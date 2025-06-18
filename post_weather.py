import requests
from datetime import datetime,timedelta

DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1384711572873674782/w4HdJy_ol7xQN4JhbrEatjxlcmyV229MSJlHbDosW6uiXAb8lxPIZnNVx_bqN1IQK3fk"  # ← 自分のWebhook URLに変更！

def get_image_url():
    # 1日前の日付を取得（UTC基準）
    yesterday = datetime.utcnow() - timedelta(days=1)
    date_str = yesterday.strftime('%Y%m%d')
    url = f"https://www.jma.go.jp/bosai/weather_map/data/png/500hPa/{date_str}_00.png"
    return url

def post_to_discord():
    image_url = get_image_url()
    response = requests.get(image_url)

    if response.status_code != 200:
        print(f"❌ 画像取得失敗: {image_url}")
        return

    files = {
        "file": ("500hPa.png", response.content)
    }
    data = {
        "content": "📡 昨日12:00 UTCの500hPa天気図（気象庁）"
    }
    post_response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)

    if post_response.status_code == 204:
        print("✅ 投稿成功")
    else:
        print(f"⚠ 投稿失敗: {post_response.status_code}, {post_response.text}")

if __name__ == "__main__":
    post_to_discord()
