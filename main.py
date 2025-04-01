import os
from flask import Flask, request, render_template, send_file
from PIL import Image
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def split_and_save_pdf(input_pdf, output_pdf, dpi=300):
    """ A0ポスターPDFを16分割してA4サイズのPDFに変換 """
    doc = fitz.open(input_pdf)
    first_page = doc[0]

    zoom = dpi / 72
    pix = first_page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # A0サイズ（841mm × 1189mm）を想定
    width, height = img.size
    a4_width, a4_height = width // 4, height // 4  # A4サイズ相当のピクセル数

    temp_images = []
    c = canvas.Canvas(output_pdf)

    for row in range(4):
        for col in range(4):
            left = col * a4_width
            upper = row * a4_height
            right = left + a4_width
            lower = upper + a4_height

            cropped = img.crop((left, upper, right, lower))
            temp_img_path = f"temp_{row}_{col}.png"
            cropped.save(temp_img_path, "PNG")
            temp_images.append(temp_img_path)

            c.setPageSize((a4_width, a4_height))
            c.drawImage(temp_img_path,
                        0,
                        0,
                        a4_width,
                        a4_height,
                        preserveAspectRatio=True,
                        anchor='c')
            c.showPage()

    c.save()

    # 作成したPNGファイルを削除
    for temp_img in temp_images:
        os.remove(temp_img)

    return output_pdf


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "ファイルが選択されていません", 400

        file = request.files["file"]
        if file.filename == "":
            return "ファイルが選択されていません", 400

        if file and file.filename.endswith(".pdf"):
            input_pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(input_pdf_path)

            output_pdf_path = os.path.join(OUTPUT_FOLDER,
                                           "output_a4_16pages.pdf")
            split_and_save_pdf(input_pdf_path, output_pdf_path)

            return send_file(output_pdf_path, as_attachment=True)

    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)
