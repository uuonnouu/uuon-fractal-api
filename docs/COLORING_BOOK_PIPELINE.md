# UUON Coloring Book Pipeline

**UUON Foundation Inc. · Phillip A. Ruiz III**

Complete workflow from fractal render → print-ready coloring book page.

-----

## Pipeline Overview

```
┌─────────────────────┐
│  UUON Fractal Engine│  ← uuon_fractal_engine.html
│  Export 4K PNG      │     Distance estimate mode (8)
│  Monolith palette   │     Contrast ≥ 1.0
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Line Art           │  ← Python script (step 2 below)
│  Extraction         │     Edge detection → clean black lines
│  (local, free)      │     on white background
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  AI Enhancement     │  ← Adobe Firefly / similar
│  (optional)         │     Prompt templates below
│  Adds detail/style  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Print Preparation  │  ← Python script (step 4 below)
│  300dpi · CMYK-safe │     Resize, sharpen, border, metadata
│  8.5×11 or A4       │
└─────────────────────┘
```

-----

## Step 1 — Engine Settings for Coloring Book Output

Use these settings in `uuon_fractal_engine.html` before exporting:

|Parameter    |Value                |Why                              |
|-------------|---------------------|---------------------------------|
|Coloring mode|8 (Distance estimate)|Cleanest gradient lines          |
|Palette      |4 (Monolith)         |Black and white base             |
|Contrast     |1.2–1.6              |Stronger line definition         |
|Cycles       |0.6–0.9              |Fewer color bands = cleaner lines|
|Iterations   |192–384              |More detail at boundaries        |

**Best presets for coloring book (ranked):**

1. Newton (root basins — hard cellular lines)
1. Phoenix (organic tendrils — medium complexity)
1. Julia (spiral dendrites — classic form)

-----

## Step 2 — Line Art Extraction (Python, runs locally)

Install once:

```bash
pip install Pillow opencv-python numpy
```

**Script: `extract_line_art.py`**

```python
"""
UUON Coloring Book Pipeline — Step 2: Line Art Extraction
Run: python extract_line_art.py input.png output_lineart.png
"""
import sys
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps

def extract_line_art(input_path: str, output_path: str,
                     blur_radius: int = 1,
                     canny_low: int = 30,
                     canny_high: int = 100,
                     dilate: int = 1,
                     invert: bool = True):
    """
    Extract clean line art from a fractal render.
    Produces black lines on white background, suitable for coloring book print.
    """
    # Load and convert to grayscale
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Gaussian blur to reduce noise before edge detection
    blurred = cv2.GaussianBlur(gray, (blur_radius*2+1, blur_radius*2+1), 0)

    # Canny edge detection
    edges = cv2.Canny(blurred, canny_low, canny_high)

    # Dilate slightly to thicken lines
    if dilate > 0:
        kernel = np.ones((dilate, dilate), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

    # Invert: black lines on white background
    if invert:
        edges = cv2.bitwise_not(edges)

    # Save
    cv2.imwrite(output_path, edges)
    print(f"Line art saved: {output_path}")
    return output_path

# Preset configurations per fractal type
CONFIGS = {
    "newton":     {"blur_radius": 1, "canny_low": 20,  "canny_high": 80,  "dilate": 1},
    "julia":      {"blur_radius": 1, "canny_low": 30,  "canny_high": 100, "dilate": 1},
    "phoenix":    {"blur_radius": 2, "canny_low": 25,  "canny_high": 90,  "dilate": 1},
    "mandelbrot": {"blur_radius": 1, "canny_low": 40,  "canny_high": 120, "dilate": 0},
    "default":    {"blur_radius": 1, "canny_low": 30,  "canny_high": 100, "dilate": 1},
}

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "render.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "lineart.png"
    cfg = sys.argv[3] if len(sys.argv) > 3 else "default"
    params = CONFIGS.get(cfg, CONFIGS["default"])
    extract_line_art(inp, out, **params)
```

**Usage:**

```bash
# Newton preset (cleanest lines)
python extract_line_art.py renders/2d/newton/UUON_Newton_2026-06-07.png \
                           renders/coloring_book/line_art/newton_01.png newton

# Julia preset
python extract_line_art.py renders/2d/julia/UUON_Julia_2026-06-07.png \
                           renders/coloring_book/line_art/julia_01.png julia
```

-----

## Step 3 — AI Enhancement (Adobe Firefly / optional)

Use these prompts with Firefly’s **Generative Fill** or **Text to Image**
to add decorative detail or refine the line art.

### Prompt A — Clean Line Art Enhancement

```
Ultra-clean black and white line art coloring book page, mathematical fractal 
pattern, precise ink lines on pure white background, no gray tones, no shading, 
suitable for adult coloring book, high contrast, crisp edges, intricate geometric 
detail, professional illustration quality, 300dpi print ready
```

### Prompt B — Newton Basin Style

```
Stained glass coloring book template, cellular geometric fractal pattern, 
black outlines only on white, three-fold radial symmetry, 
mathematical precision, no fill colors, clean line art, 
adult coloring book page, botanical intricacy level detail
```

### Prompt C — Organic/Phoenix Style

```
Botanical fractal coloring book page, organic flowing lines, 
feather and tendril patterns, black ink on white paper, 
no gray values, intricate natural geometry, fern-like recursive detail, 
suitable for therapeutic adult coloring, clean precise outlines
```

### Prompt D — Preserve Structure (for Firefly Generative Fill)

```
Add fine detail and decorative line work to this fractal pattern. 
Maintain the existing geometric structure. Black lines only, white background. 
Coloring book style. Do not add color or shading.
```

**Firefly settings:**

- Style: Graphic, Line art
- Content type: Graphic
- Effects: None (let the math speak)
- Aspect ratio: Match your export (4:3 or 1:1)

-----

## Step 4 — Print Preparation (Python)

**Script: `prepare_print.py`**

```python
"""
UUON Coloring Book Pipeline — Step 4: Print Preparation
Run: python prepare_print.py input_lineart.png output_print.png
Produces: 8.5x11 inch, 300dpi, CMYK-safe black on white
"""
import sys
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

def prepare_print(input_path: str, output_path: str,
                  dpi: int = 300,
                  page_w_in: float = 8.5,
                  page_h_in: float = 11.0,
                  margin_in: float = 0.5,
                  sharpen: float = 1.3):
    """
    Resize line art to print dimensions, add margin, sharpen, save at 300dpi.
    """
    img = Image.open(input_path).convert("L")

    # Ensure pure black and white (no gray)
    img = img.point(lambda p: 0 if p < 128 else 255)

    # Target content area (page minus margins)
    content_w = int((page_w_in - margin_in * 2) * dpi)
    content_h = int((page_h_in - margin_in * 2) * dpi)

    # Resize maintaining aspect ratio
    img.thumbnail((content_w, content_h), Image.LANCZOS)

    # Create white page
    page_w_px = int(page_w_in * dpi)
    page_h_px = int(page_h_in * dpi)
    page = Image.new("L", (page_w_px, page_h_px), 255)

    # Center image on page
    offset_x = (page_w_px - img.width)  // 2
    offset_y = (page_h_px - img.height) // 2
    page.paste(img, (offset_x, offset_y))

    # Sharpen
    if sharpen > 1.0:
        enhancer = ImageEnhance.Sharpness(page)
        page = enhancer.enhance(sharpen)

    # Save with DPI metadata
    page.save(output_path, dpi=(dpi, dpi))
    print(f"Print-ready saved: {output_path} ({page_w_in}x{page_h_in}in @ {dpi}dpi)")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "lineart.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "print_ready.png"
    prepare_print(inp, out)
```

**Usage:**

```bash
python prepare_print.py renders/coloring_book/line_art/newton_01.png \
                        renders/coloring_book/print_ready/newton_01_print.png
```

-----

## Full Pipeline One-Liner

```bash
# Extract then prepare in sequence
python extract_line_art.py input.png /tmp/lineart.png newton && \
python prepare_print.py /tmp/lineart.png output_print.png
```

-----

## File Requirements for Publishing

|Property   |Value                                        |
|-----------|---------------------------------------------|
|Resolution |300 dpi minimum                              |
|Color mode |Grayscale (or RGB with pure black/white only)|
|Page size  |8.5 × 11 in (US) or A4 (210 × 297mm)         |
|Bleed      |0.125 in if using print-on-demand            |
|File format|PNG or TIFF (lossless)                       |
|Spine text |Add separately in design software            |

**Print-on-demand platforms:** KDP (Amazon), Lulu, IngramSpark  
KDP requires PDF — convert final PNGs with:

```bash
# Install: pip install img2pdf
img2pdf renders/coloring_book/print_ready/*.png -o uuon_coloring_book.pdf
```

-----

## Install All Dependencies

```bash
pip install Pillow opencv-python numpy img2pdf
```

-----

*UUON Foundation Inc. · Phillip A. Ruiz III · [phi1@uuonfoundation.com](mailto:phi1@uuonfoundation.com)*
*All fractal renders © UUON Foundation Inc. Coloring book pipeline MIT licensed.*