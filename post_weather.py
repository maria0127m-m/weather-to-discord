import requests
from pdf2image import convert_from_bytes
import io

# ✅ あなたの Discord Webhook URL を貼ってください
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1384711572873674782/w4HdJy_ol7xQN4JhbrEatjxlcmyV229MSJlHbDosW6uiXAb8lxPIZnNVx_bqN1IQK3fk"  # ← 自分のWebhook URLに変更！

def post_asas_image_to_discord():
    pdf_url = "https://www.data.jma.go.jp/yoho/data/wxchart/quick/ASAS_COLOR.pdf"
    response = requests.get(pdf_url)

    if response.status_code != 200:
        print(f"❌ PDF取得失敗: {pdf_url}")
        return

    # PDF → PNG 変換（1ページ目のみ）
    images = convert_from_bytes(response.content, first_page=1, last_page=1)
    image_io = io.BytesIO()
    images[0].save(image_io, format='PNG')
    image_io.seek(0)

    # Discordへ画像送信
    files = {
        "file": ("ASAS_COLOR.png", image_io, "image/png")
    }
    data = {
        "content": "🗾 最新の地上天気図（気象庁）"
    }

    post_response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)

    if post_response.status_code == 204:
        print("✅ 投稿成功")
    else:
        print(f"⚠ 投稿失敗: {post_response.status_code}, {post_response.text}")

if __name__ == "__main__":
    post_asas_image_to_discord()
