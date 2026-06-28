from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

kanji_list = open("joyo_kanji_2136.txt").read().splitlines()

fonts = {
    "MSMincho": "C:/Windows/Fonts/msmincho.ttc",
    "MSGothic": "C:/Windows/Fonts/msgothic.ttc",
    "Meiryo": "C:/Windows/Fonts/meiryo.ttc",
    "YuGothic": "C:/Windows/Fonts/YuGothic.ttc",
    "YuMincho": "C:/Windows/Fonts/YuMincho.ttc",
}

for name, font_path in fonts.items():
    pdf_path = f"pdf_{name}.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)

    c.setFont("Helvetica", 12)  # fallback
    c.setFont(font_path, 32)

    x, y = 50, 780
    for k in kanji_list:
        c.drawString(x, y, k)
        x += 40
        if x > 500:
            x = 50
            y -= 50
        if y < 50:
            c.showPage()
            c.setFont(font_path, 32)
            x, y = 50, 780

    c.save()
