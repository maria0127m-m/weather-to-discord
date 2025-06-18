import requests
from pdf2image import convert_from_bytes
from PIL import Image, ImageDraw, ImageFont
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

# OLR + 200hPa流線図（5日/10日/30日平均） → 縦に結合
def get_olr_combo_image():
    # JST基準で2日前の画像を取得
    jst_now = datetime.utcnow() + timedelta(hours=9)
    target_date = jst_now - timedelta(days=2)
    date_str = target_date.strftime('%Y%m%d')
    base_url = f"https://ds.data.jma.go.jp/tcc/tcc/products/clisys/anim/GIF/tp/anom/{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"

    periods = [("5日平均", "5day"), ("10日平均", "10day"), ("30日平均", "30day")]
    images = []

    for label, period in periods:
        gif_url = f"{base_url}/{period}/OlrPsiWaf_tp200hPa_{date_str}.gif"
        response = requests.get(gif_url)
        if response.status_code != 200:
            print(f"❌ {period} GIF取得失敗: {gif_url}")
            return None

        img = Image.open(io.BytesIO(response.content)).convert("RGB")

        # ラベル描画
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 36)
        except:
            font = ImageFont.load_default()

        # テキスト位置：左上 (20, 20)
        draw.text((50, 10), label, fill="white", font=font, stroke_width=2, stroke_fill="black")
        images.append(img)

    # 画像を縦に結合
    total_height = sum(img.height for img in images)
    max_width = max(img.width for img in images)
    combined = Image.new("RGB", (max_width, total_height))
    y = 0
    for img in images:
        combined.paste(img, (0, y))
        y += img.height

    output = io.BytesIO()
    combined.save(output, format="PNG")
    output.seek(0)
    return output

# Discordへの投稿
def post_to_discord():
    asas_img = get_asas_image()
    olr_img = get_olr_combo_image()

    if not (asas_img and olr_img):
        print("❌ 画像取得に失敗")
        return

    files = {
        "file1": ("ASAS_COLOR.png", asas_img, "image/png"),
        "file2": ("OLR_combo.png", olr_img, "image/png")
    }

    jst_now = datetime.utcnow() + timedelta(hours=9)
    post_time = jst_now.strftime('%Y-%m-%d %H:%M JST')

    data = {
        "content": f"🗾 地上天気図 + 🌏 OLR+200hPa流線図（5/10/30日平均結合）\n🕒 {post_time}"
    }

    response = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files)
    if response.status_code == 204:
        print("✅ 投稿成功")
    else:
        print(f"⚠ 投稿失敗: {response.status_code}, {response.text}")

if __name__ == "__main__":
    post_to_discord()
