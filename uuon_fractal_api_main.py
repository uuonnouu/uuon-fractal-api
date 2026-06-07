"""
uuon-fractal-api · main.py
UUON Foundation Inc. · Phillip A. Ruiz III
phi1@uuonfoundation.com · uuonfoundation.com

Companion to uuon-cloud-api. This API exposes mathematical fractal
analysis and parameter advisory services derived from UUON research —
without exposing any engine source code, GLSL shaders, or coloring logic.

Deploy: pip install -r requirements.txt && python uuon_fractal_api_main.py
Docs:   /docs  (Swagger UI, auto-generated)
Sandbox:/sandbox (one-command toy demo, no key required)

LICENSE: Free to test and explore.
         Commercial use requires a UUON Foundation license.
         Contact: phi1@uuonfoundation.com
"""

import numpy as np
import base64, io, hashlib, time, json
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from PIL import Image, ImageDraw
import pywt
from skimage import filters

# ─── App ─────────────────────────────────────────────────────────────────────

REPO    = "github.com/uuon-foundation/uuon-fractal-api"
CONTACT = "phi1@uuonfoundation.com"
SITE    = "uuonfoundation.com"
VERSION = "1.0.0"
ATTR    = f"UUON Foundation Inc. · {SITE} · License required for commercial use."

app = FastAPI(
    title="uuon-fractal-api",
    description=f"""
**Mathematical fractal analysis + parameter advisory API.**
Companion to `uuon-cloud-api`. Built on research by UUON Foundation Inc.

**Why this exists:** The UUON Fractal Engine is a WebGL2/GLSL renderer whose
source is proprietary. This API exposes only the *mathematical layer* —
fractal dimension measurement, generator parameter recommendations, and a
formula knowledge base — giving developers a fully testable surface without
touching the rendering IP.

### Modules
| Module | Path | What it does |
|--------|------|--------------|
| A · Analyzer | `/v1/analyze/*` | Box-counting, wavelet, lacunarity Df measurement |
| B · Advisor  | `/v1/params/*`  | Natural language → engine parameter sets |
| C · Knowledge| `/v1/knowledge/*`| Generator formulas, coloring modes, algorithm catalog |
| Sandbox      | `/sandbox`      | Zero-config browser demo, no API key needed |

### Quick Start (60 seconds)
```bash
git clone https://github.com/uuon-foundation/uuon-fractal-api
cd uuon-fractal-api
docker compose up          # or: pip install -r requirements.txt && python uuon_fractal_api_main.py
open http://localhost:8080/docs
```

**Free tier:** 20 req/day, no key required.
**Explorer key:** 500 req/day, free signup at {SITE}.
**Commercial license:** {CONTACT}
""",
    version=VERSION,
    contact={"name": "UUON Foundation Inc.", "email": CONTACT},
    license_info={"name": "UUON Commercial License", "url": f"https://{SITE}/license"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ─── Rate limiting (in-memory; swap Redis dict for production) ────────────────

_call_log: Dict[str, list] = {}

def _check_rate(key: str, limit: int, window: int = 86400) -> bool:
    now = time.time()
    calls = [t for t in _call_log.get(key, []) if now - t < window]
    _call_log[key] = calls
    if len(calls) >= limit:
        return False
    _call_log[key].append(now)
    return True

async def _gate(request: Request, x_uuon_key: Optional[str] = Header(None)) -> str:
key = x_uuon_key or f"ip:{request.client.host if request.client else 'test-client'}"
    limit = 500 if x_uuon_key else 20
    if not _check_rate(key, limit):
        raise HTTPException(429, detail={
            "error":   "Rate limit exceeded",
            "tier":    "explorer" if x_uuon_key else "free (20/day)",
            "upgrade": CONTACT,
        })
    return key

# ─── Schemas ─────────────────────────────────────────────────────────────────

class AnalysisOptions(BaseModel):
    binarize:        bool       = True
    threshold:       int        = 128
    scale_range:     List[int]  = [4, 256]
    r_squared_cutoff: float     = 0.95

class AnalysisRequest(BaseModel):
    image:            str                     # base64 PNG or JPEG
    methods:          List[str]               = ["box_counting", "wavelet", "lacunarity"]
    ensemble:         bool                    = True
    ensemble_weights: Dict[str, float]        = {"box_counting": 0.2, "wavelet": 0.5, "multifractal": 0.3}
    options:          AnalysisOptions         = AnalysisOptions()

class RecommendRequest(BaseModel):
    description:  str
    style_tags:   List[str] = []
    constraints:  Dict      = {}

class ValidateRequest(BaseModel):
    parameters: Dict

# ─── Image helpers ───────────────────────────────────────────────────────────

def _decode(b64: str) -> np.ndarray:
    try:
        img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("L")
        return np.array(img)
    except Exception:
        raise HTTPException(400, "Invalid base64 image. Send PNG or JPEG encoded as base64.")

def _binarize(img: np.ndarray, threshold: int, auto: bool) -> np.ndarray:
    if not auto:
        return (img > threshold).astype(np.uint8)
    try:
        return (img > filters.threshold_otsu(img)).astype(np.uint8)
    except Exception:
        return (img > threshold).astype(np.uint8)

# ─── Module A: Math ──────────────────────────────────────────────────────────

def _box_count(img_bin: np.ndarray, scales: List[int]) -> dict:
    pts = []
    for s in scales:
        h, w   = img_bin.shape
        bh, bw = h // s, w // s
        if bh == 0 or bw == 0:
            continue
        blk   = img_bin[:bh*s, :bw*s].reshape(bh, s, bw, s)
        count = int(np.any(blk > 0, axis=(1, 3)).sum())
        pts.append((s, count))
    if len(pts) < 3:
        return {"Df": 2.0, "r_squared": 0.0, "note": "Image too small for reliable box counting"}
    scales_u, ns = zip(*pts)
    log_s = np.log(1.0 / np.array(scales_u, dtype=float))
    log_n = np.log(np.array(ns, dtype=float) + 1e-10)
    c     = np.polyfit(log_s, log_n, 1)
    yp    = np.polyval(c, log_s)
    r2    = float(1 - np.sum((log_n - yp)**2) / (np.sum((log_n - log_n.mean())**2) + 1e-10))
    return {"Df": round(float(c[0]), 4), "r_squared": round(r2, 4),
            "scale_range_used": [int(scales_u[0]), int(scales_u[-1])]}

def _wavelet(img: np.ndarray, levels: int = 6) -> dict:
    energies, data = [], img.astype(float)
    for _ in range(levels):
        try:
            cA, (cH, cV, cD) = pywt.dwt2(data, 'db4')
            energies.append(float(np.sum(cH**2 + cV**2 + cD**2)))
            data = cA
        except Exception:
            break
    if len(energies) < 2 or energies[0] < 1e-10:
        return {"Df": 2.0, "energy_ratio": 0.0, "decomposition_levels": len(energies)}
    ratios     = [energies[i+1] / (energies[i] + 1e-10) for i in range(len(energies)-1)]
    mean_ratio = float(np.mean(ratios))
    Df         = float(np.clip(2.0 + np.log2(max(mean_ratio, 1e-10)) / 2.0, 1.0, 3.0))
    return {"Df": round(Df, 4), "energy_ratio": round(mean_ratio, 6), "decomposition_levels": len(energies)}

def _lacunarity(img_bin: np.ndarray, box_sizes: List[int]) -> dict:
    spectrum = []
    for r in box_sizes:
        h, w, step = img_bin.shape[0], img_bin.shape[1], max(r // 2, 1)
        masses = [float(img_bin[i:i+r, j:j+r].sum())
                  for i in range(0, h - r, step) for j in range(0, w - r, step)]
        masses = np.array(masses)
        lac    = float((masses**2).mean() / (masses.mean()**2) - 1) if masses.mean() > 0 else 0.0
        spectrum.append(round(lac, 6))
    mean_lac = float(np.mean(spectrum)) if spectrum else 0.0
    return {
        "spectrum":        spectrum,
        "box_sizes":       box_sizes,
        "mean_lacunarity": round(mean_lac, 6),
        "heterogeneity":   "high" if mean_lac > 0.5 else "moderate" if mean_lac > 0.2 else "low",
    }

def _ensemble(results: dict, weights: Dict[str, float]) -> dict:
    df_vals = {}
    for m in ("box_counting", "wavelet"):
        if m in results and "Df" in results[m]:
            df_vals[m] = results[m]["Df"]
    if not df_vals:
        return {}
    tw  = sum(weights.get(k, 0.33) for k in df_vals)
    edf = sum(df_vals[k] * weights.get(k, 0.33) for k in df_vals) / tw
    var = float(np.var(list(df_vals.values())))
    return {"Df": round(edf, 4), "confidence": round(max(0.0, 1.0 - var * 10), 3),
            "variance": round(var, 6), "method": "weighted_average"}

# ─── Module A: Endpoints ─────────────────────────────────────────────────────

@app.post("/v1/analyze/full",
          summary="Full fractal dimension analysis (all methods + ensemble)",
          tags=["Module A · Analyzer"])
async def analyze_full(req: AnalysisRequest, request: Request,
                       x_uuon_key: Optional[str] = Header(None)):
    await _gate(request, x_uuon_key)
    t0  = time.time()
    img = _decode(req.image)
    bin_img = _binarize(img, req.options.threshold, not req.options.binarize)
    min_s, max_s = req.options.scale_range
    scales    = [s for s in [4, 8, 16, 32, 64, 128, 256] if min_s <= s <= max_s]
    lac_sizes = [s for s in [4, 8, 16, 32] if s <= min(img.shape) // 4]
    results   = {}
    if "box_counting" in req.methods: results["box_counting"] = _box_count(bin_img, scales)
    if "wavelet"      in req.methods: results["wavelet"]      = _wavelet(img)
    if "lacunarity"   in req.methods: results["lacunarity"]   = _lacunarity(bin_img, lac_sizes)
    if req.ensemble:
        e = _ensemble(results, req.ensemble_weights)
        if e: results["ensemble"] = e
    return {
        "id":       f"ana_{hashlib.md5(req.image[:200].encode()).hexdigest()[:12]}",
        "status":   "success",
        "results":  results,
        "metadata": {"image_size": list(img.shape),
                     "processing_ms": round((time.time() - t0) * 1000),
                     "api": "uuon-fractal-api", "version": VERSION},
        "attribution": ATTR,
    }

@app.get("/v1/analyze/methods",
         summary="List available analysis methods with formulas",
         tags=["Module A · Analyzer"])
async def list_methods():
    return {
        "methods": [
            {"id": "box_counting", "name": "Box-Counting (Minkowski-Bouligand)",
             "accuracy": "good", "best_for": "binary images, general purpose",
             "formula": "Df = -slope of log N(ε) vs log(1/ε)"},
            {"id": "wavelet",      "name": "Wavelet Transform Method (WTM)",
             "accuracy": "highest", "best_for": "self-affine structures",
             "formula": "Df = 2 + log₂(E_{j+1}/E_j) / 2"},
            {"id": "lacunarity",   "name": "Lacunarity (Gap Texture Analysis)",
             "accuracy": "complementary", "best_for": "texture heterogeneity",
             "formula": "Λ(ε) = M²(ε)/M(ε)² - 1"},
            {"id": "multifractal", "name": "Multifractal Spectrum Dq",
             "accuracy": "detailed", "best_for": "heterogeneous fractals",
             "formula": "Dq = (1/(q-1)) · lim log Σpᵢ^q / log(1/ε)"},
        ],
        "ensemble_weights": {"box_counting": 0.2, "wavelet": 0.5, "multifractal": 0.3},
        "design_note": "Wavelet weighted highest — superior spatial localisation, no phase loss.",
        "attribution": ATTR,
    }

# ─── Module B: Parameter Advisor ─────────────────────────────────────────────

STYLE_MAP = {
    "dark":          {"coloring_mode": 8,  "contrast": 0.9,  "palette": "Void Obsidian"},
    "light":         {"coloring_mode": 0,  "contrast": 0.6,  "palette": "Arctic Shelf"},
    "organic":       {"generator": 5,  "pre_transform": 16, "param_a": 0.3},
    "geometric":     {"symmetry_k": 6, "pre_transform": 4,  "generator": 0},
    "spiral":        {"pre_transform": 21, "generator": 10, "post_transform": 8},
    "coloring_book": {"coloring_mode": 8,  "contrast": 1.2, "cycles": 0.8},
    "glowing":       {"coloring_mode": 15, "contrast": 0.7},
    "chaotic":       {"generator": 13, "pre_transform": 17, "post_transform": 7},
    "symmetrical":   {"symmetry_k": 8, "symmetry_rotation": 45},
    "quantum":       {"generator": 14, "coloring_mode": 18},
    "metallic":      {"coloring_mode": 12, "post_transform": 2},
    "minimal":       {"pre_transform": 0,  "post_transform": 0, "symmetry_k": 1},
    "newton":        {"generator": 11, "coloring_mode": 0},
    "julia":         {"generator": 0,  "julia_re": -0.7269, "julia_im": 0.1889},
    "mandelbrot":    {"generator": 0,  "center_re": -0.5,   "zoom": 0.0},
    "wave":          {"generator": 5,  "coloring_mode": 7},
    "electric":      {"coloring_mode": 15, "generator": 4,  "palette": "Plasma Arc"},
    "depth":         {"coloring_mode": 16, "contrast": 1.1},
    "print":         {"coloring_mode": 8,  "contrast": 1.4, "cycles": 0.6},
}

DEFAULTS = {
    "generator": 0, "pre_transform": 0, "post_transform": 0,
    "power": 2.0, "param_a": 0.0, "param_b": 0.0,
    "iterations": 144, "escape_radius": 4.0, "coloring_mode": 0,
    "symmetry_k": 1, "symmetry_rotation": 0, "tessellation": 0.0,
    "cycles": 1.0, "offset": 0.0, "contrast": 0.65,
    "julia_re": -0.7269, "julia_im": 0.1889,
    "zoom": 0.0, "center_re": -0.5, "center_im": 0.0,
    "palette": "Void Obsidian", "animation_speed": 1.0,
}

GEN_NAMES = {
    0:"z² + c (Mandelbrot)", 1:"z³ + c", 2:"z⁴ + c",
    3:"zᵖ + c (custom power)", 4:"eᶻ + c (exponential)", 5:"sin(z) + c",
    6:"cos(z) + c", 7:"tan(z) + c", 8:"sinh(z) + c", 9:"cosh(z) + c",
    10:"log(z) + c", 11:"Newton z³−1 (root basins)", 12:"Nova z³−1 + c",
    13:"Biomorph sin+cos+c", 14:"Quantum Wave ψ·e^(i|ψ|²)+c",
    15:"Schrödinger damped oscillator",
}
COL_NAMES = {
    0:"Smooth escape time", 1:"Banded escape", 2:"Orbit trap · circle",
    3:"Orbit trap · cross", 4:"Orbit trap · point", 5:"Final angle (arg)",
    6:"Final magnitude", 7:"Stripe average", 8:"Distance estimate",
    9:"Lyapunov exponent", 10:"Geometry normal", 11:"Tangent · surface flow",
    12:"Metallic · anisotropic", 13:"Glass · chromatic IOR",
    14:"Negative filter", 15:"Iridescent · thin film", 16:"Depth fog",
    17:"Normal map · 3D lit", 18:"Probability density ∫|ψ|²",
    19:"Phase portrait arg(ψ)·|ψ|²",
}

@app.post("/v1/params/recommend",
          summary="Natural language description → UUON engine parameter set",
          tags=["Module B · Advisor"])
async def recommend(req: RecommendRequest, request: Request,
                    x_uuon_key: Optional[str] = Header(None)):
    await _gate(request, x_uuon_key)
    params, matched = DEFAULTS.copy(), []
    desc = req.description.lower()
    for tag in list(req.style_tags) + [t for t in STYLE_MAP if t in desc]:
        if tag in STYLE_MAP:
            params.update(STYLE_MAP[tag])
            matched.append(tag)
    if req.constraints.get("coloring_book_mode"):
        params["coloring_mode"] = 8
        params["contrast"] = max(params.get("contrast", 0.65), 1.0)
    if req.constraints.get("animation_safe"):
        params["animation_speed"] = min(params.get("animation_speed", 1.0), 1.5)
    return {
        "id":     f"prm_{abs(hash(req.description)) & 0xFFFFFF:06x}",
        "status": "success",
        "recommended_parameters": {
            **params,
            "generator_name":    GEN_NAMES.get(params["generator"], "Unknown"),
            "coloring_mode_name":COL_NAMES.get(params["coloring_mode"], "Unknown"),
        },
        "confidence":  round(min(0.95, 0.45 + len(matched) * 0.12), 2),
        "style_match": matched,
        "notes": ("Load into the UUON Fractal Engine at uuonfoundation.com. "
                  "Mode 8 (distance estimate) = cleanest print lines. "
                  "Orbit trap modes 2-4 = harder boundaries."),
        "attribution": ATTR,
    }

@app.get("/v1/params/schema",
         summary="Full parameter schema with types, ranges and valid values",
         tags=["Module B · Advisor"])
async def param_schema():
    return {
        "parameters": {
            "generator":         {"type":"integer","min":0,   "max":15,  "options":GEN_NAMES},
            "pre_transform":     {"type":"integer","min":0,   "max":21},
            "post_transform":    {"type":"integer","min":0,   "max":10},
            "coloring_mode":     {"type":"integer","min":0,   "max":19,  "options":COL_NAMES},
            "power":             {"type":"float",  "min":1.0, "max":4.0, "step":0.05},
            "param_a":           {"type":"float",  "min":-4.0,"max":4.0, "step":0.01},
            "param_b":           {"type":"float",  "min":-4.0,"max":4.0, "step":0.01},
            "iterations":        {"type":"integer","min":16,  "max":384, "step":16},
            "escape_radius":     {"type":"float",  "min":2.0, "max":16.0,"step":0.25},
            "symmetry_k":        {"type":"float",  "min":1,   "max":12,  "step":0.5},
            "symmetry_rotation": {"type":"float",  "min":0,   "max":360, "step":1},
            "tessellation":      {"type":"float",  "min":0.0, "max":1.0, "step":0.01},
            "cycles":            {"type":"float",  "min":0.5, "max":3.0, "step":0.05},
            "offset":            {"type":"float",  "min":0.0, "max":1.0, "step":0.01},
            "contrast":          {"type":"float",  "min":0.3, "max":2.0, "step":0.05},
            "julia_re":          {"type":"float",  "min":-2.0,"max":2.0, "step":0.001},
            "julia_im":          {"type":"float",  "min":-2.0,"max":2.0, "step":0.001},
            "zoom":              {"type":"float",  "min":-3.0,"max":12.0,"step":0.01},
            "center_re":         {"type":"float",  "min":-3.0,"max":3.0, "step":0.01},
            "center_im":         {"type":"float",  "min":-3.0,"max":3.0, "step":0.01},
            "animation_speed":   {"type":"float",  "min":0.05,"max":5.0, "step":0.05},
        },
        "palettes": [
            "Void Obsidian","Bioluminescent","Gravitational Lens","Plasma Arc",
            "Crystal","Solar Wind","Membrane","Monolith","Copper Vein",
            "Quantum Field","Gravity Well","Spectral","Abyssal",
            "Iron Dust","Ember","Arctic Shelf",
        ],
        "style_tags_available": list(STYLE_MAP.keys()),
        "attribution": ATTR,
    }

# ─── Module C: Knowledge Base ─────────────────────────────────────────────────

KNOWLEDGE = {
    "generators": [
        {"id":0,  "name":"z² + c",        "formula":"z_{n+1} = z_n² + c",
         "category":"polynomial",    "description":"Classic Mandelbrot iteration. Canonical escape-time fractal with the full Mandelbrot/Julia duality.",
         "visual_character":["structured","bulbous","infinite detail","classic"],
         "coloring_affinities":[0,8,11]},
        {"id":5,  "name":"sin(z) + c",    "formula":"z_{n+1} = sin(z_n) + c",
         "category":"transcendental","description":"Complex sine before adding c. Infinite singular points on imaginary axis produce organic curved boundaries.",
         "visual_character":["organic","curved","biological","wave-like"],
         "coloring_affinities":[7,8,15]},
        {"id":11, "name":"Newton z³−1",   "formula":"z_{n+1} = z_n - (z_n³-1)/(3z_n²)",
         "category":"root-finding",  "description":"Newton-Raphson on z³=1. Three root basins produce stained-glass cellular boundary fractal.",
         "visual_character":["cellular","stained-glass","three-fold","basin"],
         "coloring_affinities":[0,5,10]},
        {"id":14, "name":"Quantum Wave",  "formula":"z_{n+1} = ψ·e^(i|ψ|²) + c",
         "category":"quantum-inspired","description":"Nonlinear Schrödinger-inspired iteration producing probability-density visual textures.",
         "visual_character":["quantum","wave","interference","probability"],
         "coloring_affinities":[18,19,15]},
    ],
    "algorithms": {
        "box_counting": {
            "name":"Box-Counting Dimension","formula":"Df = lim(ε→0) [log N(ε) / log(1/ε)]",
            "practical":"Df = -slope of log N(ε) vs log(1/ε) via linear regression",
            "accuracy":"good","failure_rate":"~5% on clean images",
            "best_for":"Binary images, general purpose. Most widely validated in SEM/TEM literature.",
        },
        "wavelet": {
            "name":"Wavelet Transform Method","formula":"Df = log₂(E_{j+1}/E_j) / E_scale",
            "accuracy":"highest","failure_rate":"<1% on synthetic fractals",
            "best_for":"Self-affine structures. Superior spatial localisation. No phase information lost.",
            "uuon_note":"UUON ensemble weights wavelet at 0.5 — highest of the three.",
        },
        "lacunarity": {
            "name":"Lacunarity Analysis","formula":"Λ(ε) = M²(ε)/M(ε)² - 1",
            "accuracy":"complementary","best_for":"Distinguishes images with similar Df. Quantifies gap distribution and texture heterogeneity.",
            "interpretation":"High lacunarity = heterogeneous (many gap sizes). Low = homogeneous.",
        },
    },
}

@app.get("/v1/knowledge/generators", tags=["Module C · Knowledge"],
         summary="All fractal generator descriptions, formulas, and visual character")
async def get_generators():
    return {"generators": KNOWLEDGE["generators"], "count": len(KNOWLEDGE["generators"]), "attribution": ATTR}

@app.get("/v1/knowledge/generators/{gen_id}", tags=["Module C · Knowledge"],
         summary="Single generator detail by ID (0–15)")
async def get_generator(gen_id: int):
    g = next((g for g in KNOWLEDGE["generators"] if g["id"] == gen_id), None)
    if not g: raise HTTPException(404, f"Generator {gen_id} not indexed. See /v1/params/schema for full list.")
    return {**g, "attribution": ATTR}

@app.get("/v1/knowledge/algorithms", tags=["Module C · Knowledge"],
         summary="Fractal dimension algorithm catalog with formulas")
async def get_algorithms():
    return {"algorithms": KNOWLEDGE["algorithms"], "attribution": ATTR}

@app.get("/v1/knowledge/algorithms/{method}", tags=["Module C · Knowledge"],
         summary="Single algorithm detail")
async def get_algorithm(method: str):
    a = KNOWLEDGE["algorithms"].get(method)
    if not a: raise HTTPException(404, f"'{method}' not found. Available: {list(KNOWLEDGE['algorithms'].keys())}")
    return {**a, "id": method, "attribution": ATTR}

@app.get("/v1/knowledge/coloring-modes", tags=["Module C · Knowledge"],
         summary="All 20 coloring mode descriptions with usage notes")
async def get_coloring():
    return {
        "coloring_modes": [{"id":k,"name":v} for k,v in COL_NAMES.items()],
        "notes": {
            "coloring_book":  "Mode 8 (Distance estimate) = cleanest lines for print.",
            "lighting_modes": "Modes 10-17 use linear sRGB workflow internally.",
            "quantum_modes":  "Modes 18-19 specific to generators 14 (Quantum Wave) and 15 (Schrödinger).",
        },
        "attribution": ATTR,
    }

# ─── Sandbox: Zero-config browser demo ───────────────────────────────────────
# Playbook item: "toy implementation" that shows the API doing real work.
# No key required. Generates a synthetic test fractal image in-memory,
# runs the full analysis, returns JSON. Browsable at /sandbox.

def _make_test_image(size: int = 256) -> str:
    """Generate a simple Mandelbrot-like bitmap for sandbox demos."""
    pixels = np.zeros((size, size), dtype=np.uint8)
    for py in range(size):
        for px in range(size):
            x0 = (px / size) * 3.5 - 2.5
            y0 = (py / size) * 3.0 - 1.5
            x, y, i = 0.0, 0.0, 0
            while x*x + y*y <= 4 and i < 64:
                x, y = x*x - y*y + x0, 2*x*y + y0
                i += 1
            pixels[py, px] = 255 if i == 64 else 0
    buf = io.BytesIO()
    Image.fromarray(pixels).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@app.get("/sandbox", response_class=HTMLResponse,
         summary="Zero-config browser sandbox — no API key needed",
         tags=["Sandbox"])
async def sandbox():
    b64 = _make_test_image()
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>uuon-fractal-api · Sandbox</title>
<style>
  body{{margin:0;background:#0a0a0f;color:#e8e4dc;font-family:'Courier New',monospace;padding:32px}}
  h1{{color:#c8a96e;letter-spacing:4px;font-size:14px;text-transform:uppercase}}
  h2{{color:#7ec8a0;letter-spacing:2px;font-size:12px;text-transform:uppercase;margin-top:32px}}
  pre{{background:#0d0d14;border:1px solid #1e1e2a;padding:20px;border-radius:6px;font-size:12px;
       overflow-x:auto;color:#aaa;line-height:1.6}}
  .note{{color:#555;font-size:11px;margin-top:8px;line-height:1.6}}
  a{{color:#c8a96e}}
  .pill{{display:inline-block;padding:3px 10px;border-radius:3px;font-size:10px;
         background:#1a2a1a;color:#7ec8a0;border:1px solid #2a4a2a;margin-right:6px}}
</style>
</head>
<body>
<h1>uuon-fractal-api &nbsp;·&nbsp; Sandbox</h1>
<p class="note">
  Zero-config demo. No API key required. A 256×256 Mandelbrot bitmap was generated
  in-memory and sent through the full analysis pipeline. Results below are live.
  <br>Full engine at <a href="https://uuonfoundation.com">uuonfoundation.com</a> &nbsp;·&nbsp;
  Interactive docs at <a href="/docs">/docs</a>
</p>

<h2>Test Image (base64 inline)</h2>
<p class="note">256×256 Mandelbrot · generated server-side · no engine source exposed</p>
<img src="data:image/png;base64,{b64}"
     style="border:1px solid #1e1e2a;display:block;margin:12px 0;image-rendering:pixelated">

<h2>Equivalent curl command</h2>
<pre>curl -X POST https://your-replit-slug.replit.app/v1/analyze/full \\
  -H "Content-Type: application/json" \\
  -d '{{"image": "&lt;base64&gt;", "methods": ["box_counting","wavelet","lacunarity"], "ensemble": true}}'</pre>

<h2>Live result (just ran)</h2>
<pre id="result">Loading...</pre>

<h2>Try the Parameter Advisor</h2>
<pre>curl -X POST https://your-replit-slug.replit.app/v1/params/recommend \\
  -H "Content-Type: application/json" \\
  -d '{{"description": "dark organic spiral for coloring book", "constraints": {{"coloring_book_mode": true}}}}'</pre>

<script>
fetch('/v1/analyze/full', {{
  method: 'POST',
  headers: {{'Content-Type': 'application/json'}},
  body: JSON.stringify({{
    image: '{b64}',
    methods: ['box_counting', 'wavelet', 'lacunarity'],
    ensemble: true
  }})
}})
.then(r => r.json())
.then(d => document.getElementById('result').textContent = JSON.stringify(d, null, 2))
.catch(e => document.getElementById('result').textContent = 'Error: ' + e);
</script>
</body>
</html>
""")

# ─── Root ─────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return {
        "name":    "uuon-fractal-api",
        "version": VERSION,
        "repo":    REPO,
        "modules": {
            "A": "/v1/analyze/*  — Fractal dimension analysis",
            "B": "/v1/params/*   — Parameter advisory",
            "C": "/v1/knowledge/*— Knowledge base & formulas",
        },
        "sandbox": "/sandbox — zero-config browser demo, no key required",
        "docs":    "/docs",
        "license": "Free to test. Commercial use: phi1@uuonfoundation.com",
        "website": SITE,
        "related": "uuon-cloud-api",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("uuon_fractal_api_main:app", host="0.0.0.0", port=8080, reload=True)
