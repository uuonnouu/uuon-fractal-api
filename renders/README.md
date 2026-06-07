# /renders — Fractal Render Archive

This folder stores exported PNG renders from both the UUON 2D and 3D engines.
Used as: portfolio assets, coloring book source material, API showcase images,
and ML training data paired with `presets.json`.

-----

## Folder Structure

```
renders/
│
├── 2d/
│   ├── mandelbrot/
│   │   └── UUON_Mandelbrot_*.png
│   ├── julia/
│   │   └── UUON_Julia_*.png
│   ├── newton/
│   │   └── UUON_Newton_*.png
│   ├── phoenix/
│   │   └── UUON_Phoenix_*.png
│   ├── burning_ship/
│   ├── nova/
│   ├── biomorph/
│   └── quantum/
│
├── 3d/
│   ├── mandelbulb/
│   │   └── UUON_3D_Mandelbulb_*.png
│   └── mandelbox/
│       └── UUON_3D_Mandelbox_*.png
│
└── coloring_book/
    ├── source/       ← full color renders (from engine)
    ├── line_art/     ← processed line art (from pipeline)
    └── print_ready/  ← final print files (300dpi, CMYK-safe)
```

-----

## Naming Convention

All engine exports follow this pattern automatically:

```
UUON_{PresetName}_{YYYY-MM-DD-HH-MM-SS}.png
```

Example: `UUON_Newton_2026-06-07-14-32-11.png`

Do not rename files — the timestamp is the unique identifier used to pair
renders with their parameter sets in the ML training pipeline.

-----

## How to Export from the 2D Engine

1. Open `uuon_fractal_engine.html` in Chrome or Firefox
1. Select a preset or dial in parameters manually
1. Click **EXPORT PNG** — saves at 4K with burned-in metadata
1. Click **EXPORT SUMMARY** — saves matching `.txt` parameter file
1. Place PNG in the correct `/renders/2d/{preset}/` subfolder

## How to Export from the 3D Engine

1. Open `uuon_3d_engine.html`
1. Select preset or adjust parameters
1. Click **EXPORT PNG** — saves current canvas at full resolution
1. Place in `/renders/3d/{mandelbulb or mandelbox}/`

-----

## Coloring Book Pipeline (see COLORING_BOOK_PIPELINE.md)

Source renders → Line art extraction → AI enhancement → Print-ready output

Best candidates for coloring book: Newton, Phoenix, Julia
See `COLORING_BOOK_PIPELINE.md` for the full workflow.

-----

*UUON Foundation Inc. · [phi1@uuonfoundation.com](mailto:phi1@uuonfoundation.com)*