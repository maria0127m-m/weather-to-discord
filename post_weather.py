import requests
from pdf2image import convert_from_bytes
from datetime import datetime, timedelta
import io

# ✅ あなたの Discord Webhook URL をここに貼ってください
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1384711572873674782/w4HdJy_ol7xQN4JhbrEatjxlcmyV229MSJlHbDosW6uiXAb8lxPIZnNVx_bqN1IQK3fk"  # ← 自分のWebhook URLに変更！

# 地上天気図（ASAS）の画像取得・変換
def get_asas_image():
    pdf_url = "https://www.data.jma.go.jp/yoho/data/wxchart/quick/ASAS_COLOR.pdf"
    response = requests.get(pdf_url)

    if response.status_code != 200:
        print(f"❌ PDF取得失敗: {pdf_url}")
        return None

    # PDF → PNG（1ページ目のみ）
    images = convert_from_bytes(response.content, first_page=1, last_page=1, poppler_path="/usr/bin")
    image_io = io.BytesIO()
    images[0].save(image_io, format='PNG')
    image_io.seek(0)
    return image_io

# ひまわり衛星画像（RGB PNG）のURL生成
def get_himawari_url():
    now = datetime.utcnow() - timedelta(hours=1)  # 1時間前が安定
    timestamp = now.strftime("%Y%m%d%H0000")
    return f"https://www.jma.go.jp/bosai/himawari/data/satimg/{timestamp}_00_RGB_PNH.png"

# Discordへ投稿（画像2枚）
def post_to_discord():
    asas_image = get_asas_image()
    himawari_url = get_himawari_url()
    himawari_response = requests.get(himawari_url)

    if asas_image is None or himawari_response.status_code != 200:
        print("❌ いずれかの画像取得に失敗しました")
        return

    files = {
        "file1": ("ASAS_COLOR.png", asas_image, "image/png"),
        "file2": ("himawari.png", himawari_response.content, "image/png")
    }

    data = {
        "content": "🗾 **最新の地上天気図** ＋ 🛰️ **ひまわり衛星画像**（気象庁）"
    }

    post_response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)

    if post_response.status_code == 204:
        print("✅ 2枚投稿成功")
    else:
        print(f"⚠ 投稿失敗: {post_response.status_code}, {post_response.text}")

if __name__ == "__main__":
    post_to_discord()

