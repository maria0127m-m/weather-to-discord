import requests
from pdf2image import convert_from_bytes
from datetime import datetime, timedelta
import io

# ✅ あなたの Discord Webhook URL をここに貼ってください
DISCORD_WEBHOOK_URL = "https://discordapp.com/api/webhooks/1384711572873674782/w4HdJy_ol7xQN4JhbrEatjxlcmyV229MSJlHbDosW6uiXAb8lxPIZnNVx_bqN1IQK3fk"  # ← 自分のWebhook URLに変更！

# 地上天気図（PDF → PNG）
def get_asas_image():
    pdf_url = "https://www.data.jma.go.jp/yoho/data/wxchart/quick/ASAS_COLOR.pdf"
    response = requests.get(pdf_url)
    if response.status_code != 200:
        print("❌ ASAS PDF取得失敗")
        return None
    images = convert_from_bytes(response.content, first_page=1, last_page=1, poppler_path="/usr/bin")
    image_io = io.BytesIO()
    images[0].save(image_io, format='PNG')
    image_io.seek(0)
    return image_io

# OLR + 200hPa流線GIF
def get_olr_gif():
    # JST基準で1日前の日付を取得（UTCに直す）
    jst_now = datetime.utcnow() + timedelta(hours=9)
    target_date = jst_now - timedelta(days=1)
    date_str = target_date.strftime('%Y%m%d')
    gif_url = f"https://ds.data.jma.go.jp/tcc/tcc/products/clisys/anim/GIF/tp/anom/{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}/5day/OlrPsiWaf_tp200hPa_{date_str}.gif"
    response = requests.get(gif_url)
    if response.status_code == 200:
        return response
    else:
        print(f"❌ OLR画像取得失敗: {gif_url}")
        return None


# Discord投稿
def post_to_discord():
    asas_img = get_asas_image()
    olr_gif = get_olr_gif()

    if not (asas_img and olr_gif):
        print("❌ いずれかの画像取得に失敗")
        return

    files = {
        "file1": ("ASAS_COLOR.png", asas_img, "image/png"),
        "file2": ("olr_psi.gif", olr_gif.content, "image/gif")
    }

    data = {
        "content": "🗾 地上天気図 + 🌏 OLR+200hPa流線図（5日平均）"
    }

    response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
    if response.status_code == 204:
        print("✅ 投稿成功")
    else:
        print(f"⚠ 投稿失敗: {response.status_code}, {response.text}")

if __name__ == "__main__":
    post_to_discord()
