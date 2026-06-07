"""
UUON Coloring Book Pipeline — Step 2: Line Art Extraction
UUON Foundation Inc. · phi1@uuonfoundation.com

Run: python extract_line_art.py input.png output_lineart.png [preset]
Presets: newton, julia, phoenix, mandelbrot, default

Install: pip install opencv-python numpy Pillow
"""
import sys
import cv2
import numpy as np

def extract_line_art(input_path, output_path,
                     blur_radius=1, canny_low=30,
                     canny_high=100, dilate=1, invert=True):
    img    = cv2.imread(input_path)
    gray   = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (blur_radius*2+1, blur_radius*2+1), 0)
    edges  = cv2.Canny(blurred, canny_low, canny_high)
    if dilate > 0:
        kernel = np.ones((dilate, dilate), np.uint8)
        edges  = cv2.dilate(edges, kernel, iterations=1)
    if invert:
        edges = cv2.bitwise_not(edges)
    cv2.imwrite(output_path, edges)
    print(f"Line art saved: {output_path}")

CONFIGS = {
    "newton":     {"blur_radius":1,"canny_low":20, "canny_high":80,  "dilate":1},
    "julia":      {"blur_radius":1,"canny_low":30, "canny_high":100, "dilate":1},
    "phoenix":    {"blur_radius":2,"canny_low":25, "canny_high":90,  "dilate":1},
    "mandelbrot": {"blur_radius":1,"canny_low":40, "canny_high":120, "dilate":0},
    "default":    {"blur_radius":1,"canny_low":30, "canny_high":100, "dilate":1},
}

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "render.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "lineart.png"
    cfg = sys.argv[3] if len(sys.argv) > 3 else "default"
    extract_line_art(inp, out, **CONFIGS.get(cfg, CONFIGS["default"]))
