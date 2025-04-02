import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas


def split_and_save_pdf(input_pdf, output_pdf, dpi=300):
    """ A0ポスターPDFを16分割してA4サイズのPDFに変換 """
    doc = fitz.open(input_pdf)
    first_page = doc[0]

    zoom = dpi / 72
    pix = first_page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    width, height = img.size
    a4_width, a4_height = width // 4, height // 4

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

    for temp_img in temp_images:
        os.remove(temp_img)

    return output_pdf


def select_pdf():
    """ PDFを選択して処理を実行 """
    file_path = filedialog.askopenfilename(filetypes=[("PDFファイル", "*.pdf")])
    if not file_path:
        return  # ファイルが選択されなかった場合は何もしない

    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_pdf_path = os.path.join(desktop_path, "output_a4_16pages.pdf")

    try:
        split_and_save_pdf(file_path, output_pdf_path)
        messagebox.showinfo("成功", f"分割PDFを保存しました:\n{output_pdf_path}")
    except Exception as e:
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{e}")


# Tkinterのウィンドウを作成
root = tk.Tk()
root.title("A0ポスター分割ツール")
root.geometry("400x200")

label = tk.Label(root, text="PDFを選択してA4サイズに16分割", font=("Arial", 12))
label.pack(pady=20)

btn_select = tk.Button(root,
                       text="PDFを選択",
                       command=select_pdf,
                       font=("Arial", 12))
btn_select.pack(pady=10)

btn_exit = tk.Button(root, text="終了", command=root.quit, font=("Arial", 12))
btn_exit.pack(pady=10)

root.mainloop()
