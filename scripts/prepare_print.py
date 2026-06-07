"""
UUON Coloring Book Pipeline — Step 4: Print Preparation
UUON Foundation Inc. · phi1@uuonfoundation.com

Run: python prepare_print.py input_lineart.png output_print.png
Produces: 8.5x11 inch, 300dpi, pure black on white

Install: pip install Pillow
"""
import sys
from PIL import Image, ImageEnhance

def prepare_print(input_path, output_path,
                  dpi=300, page_w_in=8.5, page_h_in=11.0,
                  margin_in=0.5, sharpen=1.3):
    img = Image.open(input_path).convert("L")
    img = img.point(lambda p: 0 if p < 128 else 255)
    content_w = int((page_w_in - margin_in * 2) * dpi)
    content_h = int((page_h_in - margin_in * 2) * dpi)
    img.thumbnail((content_w, content_h), Image.LANCZOS)
    page = Image.new("L", (int(page_w_in*dpi), int(page_h_in*dpi)), 255)
    page.paste(img, ((int(page_w_in*dpi)-img.width)//2,
                     (int(page_h_in*dpi)-img.height)//2))
    if sharpen > 1.0:
        page = ImageEnhance.Sharpness(page).enhance(sharpen)
    page.save(output_path, dpi=(dpi, dpi))
    print(f"Print-ready: {output_path} ({page_w_in}x{page_h_in}in @ {dpi}dpi)")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "lineart.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "print_ready.png"
    prepare_print(inp, out)
