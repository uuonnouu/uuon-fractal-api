"""
uuon-fractal-api · tests/test_api.py
UUON Foundation Inc. · phi1@uuonfoundation.com

Run: pip install pytest httpx && pytest tests/test_api.py -v

Tests all three modules without requiring a live server.
Uses FastAPI's built-in TestClient for in-process testing.
"""

import base64
import json
import numpy as np
from io import BytesIO
from PIL import Image
import pytest
from fastapi.testclient import TestClient

# Import the app
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from uuon_fractal_api_main import app

client = TestClient(app)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_test_image(size=64, pattern="mandelbrot"):
    """Generate a small test image as base64."""
    pixels = np.zeros((size, size), dtype=np.uint8)
    for py in range(size):
        for px in range(size):
            x0 = (px / size) * 3.5 - 2.5
            y0 = (py / size) * 3.0 - 1.5
            x, y, i = 0.0, 0.0, 0
            while x*x + y*y <= 4 and i < 32:
                x, y = x*x - y*y + x0, 2*x*y + y0
                i += 1
            pixels[py, px] = 255 if i == 32 else 0
    buf = BytesIO()
    Image.fromarray(pixels).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

TEST_IMAGE = make_test_image()

# ─── Root ─────────────────────────────────────────────────────────────────────

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "uuon-fractal-api" in data["name"]
    assert "/v1/analyze/*" in data["modules"]["A"]
    assert "/v1/params/*"  in data["modules"]["B"]
    assert "/v1/knowledge/*" in data["modules"]["C"]

# ─── Module A: Analyzer ───────────────────────────────────────────────────────

def test_analyze_methods():
    r = client.get("/v1/analyze/methods")
    assert r.status_code == 200
    data = r.json()
    assert "methods" in data
    ids = [m["id"] for m in data["methods"]]
    assert "box_counting" in ids
    assert "wavelet"      in ids
    assert "lacunarity"   in ids

def test_analyze_full_box_counting():
    r = client.post("/v1/analyze/full", json={
        "image": TEST_IMAGE,
        "methods": ["box_counting"],
        "ensemble": False,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert "box_counting" in data["results"]
    bc = data["results"]["box_counting"]
    assert "Df" in bc
    assert 1.0 <= bc["Df"] <= 3.0

def test_analyze_full_wavelet():
    r = client.post("/v1/analyze/full", json={
        "image": TEST_IMAGE,
        "methods": ["wavelet"],
        "ensemble": False,
    })
    assert r.status_code == 200
    data = r.json()
    assert "wavelet" in data["results"]
    assert 1.0 <= data["results"]["wavelet"]["Df"] <= 3.0

def test_analyze_full_lacunarity():
    r = client.post("/v1/analyze/full", json={
        "image": TEST_IMAGE,
        "methods": ["lacunarity"],
        "ensemble": False,
    })
    assert r.status_code == 200
    data = r.json()
    assert "lacunarity" in data["results"]
    lac = data["results"]["lacunarity"]
    assert "mean_lacunarity" in lac
    assert lac["heterogeneity"] in ("low", "moderate", "high")

def test_analyze_full_ensemble():
    r = client.post("/v1/analyze/full", json={
        "image": TEST_IMAGE,
        "methods": ["box_counting", "wavelet", "lacunarity"],
        "ensemble": True,
    })
    assert r.status_code == 200
    data = r.json()
    assert "ensemble" in data["results"]
    ens = data["results"]["ensemble"]
    assert "Df" in ens
    assert "confidence" in ens
    assert 0.0 <= ens["confidence"] <= 1.0

def test_analyze_bad_image():
    r = client.post("/v1/analyze/full", json={
        "image": "not_valid_base64!!!",
        "methods": ["box_counting"],
    })
    assert r.status_code == 400

def test_analyze_attribution():
    r = client.post("/v1/analyze/full", json={
        "image": TEST_IMAGE,
        "methods": ["box_counting"],
    })
    assert "UUON Foundation" in r.json()["attribution"]

# ─── Module B: Advisor ────────────────────────────────────────────────────────

def test_params_schema():
    r = client.get("/v1/params/schema")
    assert r.status_code == 200
    data = r.json()
    assert "parameters" in data
    params = data["parameters"]
    # Check key parameters exist with correct ranges
    assert params["generator"]["min"] == 0
    assert params["generator"]["max"] == 15
    assert params["coloring_mode"]["max"] == 19
    assert params["power"]["min"] == 1.0
    assert params["power"]["max"] == 4.0
    assert "palettes" in data
    assert len(data["palettes"]) == 16

def test_params_recommend_basic():
    r = client.post("/v1/params/recommend", json={
        "description": "dark spiral",
        "style_tags": ["dark"],
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    p = data["recommended_parameters"]
    assert 0 <= p["generator"] <= 15
    assert 0 <= p["coloring_mode"] <= 19
    assert 1.0 <= p["power"] <= 4.0
    assert 0.3 <= p["contrast"] <= 2.0

def test_params_recommend_coloring_book_constraint():
    r = client.post("/v1/params/recommend", json={
        "description": "coloring book page",
        "constraints": {"coloring_book_mode": True},
    })
    assert r.status_code == 200
    data = r.json()
    p = data["recommended_parameters"]
    # Coloring book mode forces distance estimate (8) and contrast >= 1.0
    assert p["coloring_mode"] == 8
    assert p["contrast"] >= 1.0

def test_params_recommend_confidence():
    r = client.post("/v1/params/recommend", json={
        "description": "quantum wave organic dark spiral",
        "style_tags": ["quantum", "organic", "dark"],
    })
    assert r.status_code == 200
    data = r.json()
    assert 0.0 <= data["confidence"] <= 1.0
    assert len(data["style_match"]) > 0

def test_params_recommend_attribution():
    r = client.post("/v1/params/recommend", json={"description": "test"})
    assert "UUON Foundation" in r.json()["attribution"]

# ─── Module C: Knowledge ──────────────────────────────────────────────────────

def test_knowledge_generators_list():
    r = client.get("/v1/knowledge/generators")
    assert r.status_code == 200
    data = r.json()
    assert "generators" in data
    assert data["count"] == len(data["generators"])
    # Check required fields on each
    for g in data["generators"]:
        assert "id" in g
        assert "name" in g
        assert "formula" in g
        assert "description" in g
        assert "visual_character" in g

def test_knowledge_generator_by_id():
    for gen_id in [0, 5, 11, 14]:
        r = client.get(f"/v1/knowledge/generators/{gen_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == gen_id
        assert "formula" in data

def test_knowledge_generator_not_found():
    r = client.get("/v1/knowledge/generators/99")
    assert r.status_code == 404

def test_knowledge_algorithms():
    r = client.get("/v1/knowledge/algorithms")
    assert r.status_code == 200
    data = r.json()
    assert "algorithms" in data
    algs = data["algorithms"]
    assert "box_counting" in algs
    assert "wavelet"      in algs
    assert "lacunarity"   in algs

def test_knowledge_algorithm_by_method():
    for method in ["box_counting", "wavelet", "lacunarity"]:
        r = client.get(f"/v1/knowledge/algorithms/{method}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == method
        assert "formula" in data
        assert "accuracy" in data

def test_knowledge_algorithm_not_found():
    r = client.get("/v1/knowledge/algorithms/nonexistent")
    assert r.status_code == 404

def test_knowledge_coloring_modes():
    r = client.get("/v1/knowledge/coloring-modes")
    assert r.status_code == 200
    data = r.json()
    assert "coloring_modes" in data
    modes = data["coloring_modes"]
    assert len(modes) == 20  # modes 0-19
    ids = [m["id"] for m in modes]
    assert 8 in ids   # Distance estimate
    assert 18 in ids  # Probability density

def test_knowledge_coloring_notes():
    r = client.get("/v1/knowledge/coloring-modes")
    data = r.json()
    assert "coloring_book" in data["notes"]

# ─── Rate limiting ────────────────────────────────────────────────────────────

def test_rate_limit_headers():
    """Verify API responds normally within rate limits."""
    r = client.get("/v1/analyze/methods")
    assert r.status_code == 200  # Should not be rate limited in test

# ─── Sandbox ─────────────────────────────────────────────────────────────────

def test_sandbox_loads():
    r = client.get("/sandbox")
    assert r.status_code == 200
    assert "uuon-fractal-api" in r.text.lower()
    assert "data:image/png;base64" in r.text  # Test image rendered

