import requests

# ✅ あなたの Discord Webhook URL をここに貼ってください
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1384711572873674782/w4HdJy_ol7xQN4JhbrEatjxlcmyV229MSJlHbDosW6uiXAb8lxPIZnNVx_bqN1IQK3fk"  # ← 自分のWebhook URLに変更！

def post_pdf_to_discord():
    url = "https://www.data.jma.go.jp/yoho/data/wxchart/quick/ASAS_COLOR.pdf"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ PDF取得失敗: {url}")
        return

    files = {
        "file": ("ASAS_COLOR.pdf", response.content, "application/pdf")
    }
    data = {
        "content": "🗾 最新の地上天気図（ASAS, 気象庁）"
    }

    post_response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)

    if post_response.status_code == 204:
        print("✅ PDF投稿成功")
    else:
        print(f"⚠ 投稿失敗: {post_response.status_code}, {post_response.text}")

if __name__ == "__main__":
    post_pdf_to_discord()

