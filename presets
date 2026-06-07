# UUON Fractal Engine · Preset Showcase

**UUON Foundation Inc. · Phillip A. Ruiz III**  
uuonfoundation.com · [phi1@uuonfoundation.com](mailto:phi1@uuonfoundation.com) · @uuon.foundation

-----

## What the Engine Produces

The UUON Fractal Engine is a WebGL2/GLSL real-time fractal renderer.
Every image below represents a named parameter preset — a specific combination
of generator, coloring mode, transforms, and palette that produces a
reproducible aesthetic.

Parameter sets are public (see `presets.json`).
The rendering source is proprietary.

-----

## The Eight Core Presets

### Mandelbrot

**Generator:** z² + c · **Coloring:** Smooth escape time  
The canonical escape-time fractal. Infinite self-similar boundary detail.
Fractal dimension Df ≈ 2.0 at the boundary. The reference against which
all other generators are measured.

```json
{ "generator": 0, "iterations": 144, "coloring_mode": 0, "center_re": -0.5 }
```

-----

### Julia · c = −0.7269 + 0.1889i

**Generator:** z² + c · **Coloring:** Smooth escape time  
Connected Julia set. The same iteration formula as Mandelbrot but with
a fixed c value per pixel rather than variable. Produces the classic
spiral dendrite form — one of the most recognizable fractals in mathematics.

```json
{ "generator": 0, "julia_re": -0.7269, "julia_im": 0.1889, "coloring_mode": 0 }
```

-----

### Burning Ship

**Generator:** z² + c · **Pre-transform:** |Re(z)|+i·|Im(z)|  
Absolute value folding before iteration breaks complex analyticity and
introduces hard asymmetric edges. The result resembles a ship silhouette
on fire — one of the most visually distinctive escape-time fractals.
Highest iteration count of the core set (240) to resolve fine edge detail.

```json
{ "generator": 0, "pre_transform": 7, "iterations": 240, "center_re": -0.4, "center_im": -0.6, "zoom": 1.0 }
```

-----

### Newton · Root Basins

**Generator:** Newton z³−1 · **Coloring:** Final angle (arg)  
Newton-Raphson iteration applied to z³=1. The three roots of unity
partition the complex plane into three basins of attraction.
The boundaries between basins are fractal — infinitely intricate
stained-glass cellular regions. Best coloring book candidate in the set.

```json
{ "generator": 11, "coloring_mode": 5, "iterations": 80 }
```

-----

### Nova · Perturbed Newton

**Generator:** Nova z³−1+c · **Coloring:** Smooth escape time  
Newton iteration with an additive c perturbation introduces
Mandelbrot-like parameter dependence into the root-basin structure.
The result combines cellular basin regions with escape-time gradients.

```json
{ "generator": 12, "julia_re": -0.5, "julia_im": 0.5, "iterations": 112 }
```

-----

### Phoenix · Organic Tendrils

**Generator:** sin(z)+c · **Params:** a=−0.5, b=0.1  
Complex sine iteration with non-zero param_a and param_b. The sine
function has infinitely many singular points along the imaginary axis,
producing wave-like organic boundary structures. The param values
introduce asymmetry that generates feather-like tendrils.
Second-best coloring book candidate.

```json
{ "generator": 5, "param_a": -0.5, "param_b": 0.1, "julia_re": -0.5, "julia_im": 0.1 }
```

-----

### Biomorph · Cellular Forms

**Generator:** Biomorph sin+cos+c · **Coloring:** Smooth escape time  
Composite sine+cosine generator produces forms that resemble biological
microscopy — cell membranes, organelle boundaries, and microorganism
outlines. Lower iteration count (64) keeps boundaries clean.

```json
{ "generator": 13, "iterations": 64 }
```

-----

### Quantum · Interference Pattern

**Generator:** Quantum Wave ψ·e^(i|ψ|²)+c  
**Coloring:** Probability density ∫|ψ|² · **Symmetry:** k=5  
Nonlinear Schrödinger-inspired iteration with probability density coloring.
Five-fold rotational symmetry applied. Produces radially symmetric
interference-pattern structures that resemble quantum wavefunction
visualizations.

```json
{ "generator": 14, "coloring_mode": 18, "symmetry_k": 5, "julia_re": -0.4, "julia_im": 0.6 }
```

-----

## Coloring Book Suitability

|Preset      |Df (approx)|Line Density|Print Score|
|------------|-----------|------------|-----------|
|Newton      |1.85       |High        |⭐⭐⭐⭐⭐      |
|Phoenix     |1.72       |High        |⭐⭐⭐⭐       |
|Julia       |1.90       |Medium-High |⭐⭐⭐⭐       |
|Nova        |1.80       |Medium      |⭐⭐⭐        |
|Mandelbrot  |2.00       |Medium      |⭐⭐⭐        |
|Biomorph    |1.65       |Medium      |⭐⭐⭐        |
|Burning Ship|1.78       |Medium      |⭐⭐         |
|Quantum     |1.70       |Low-Medium  |⭐⭐         |

**For print:** Override coloring mode to 8 (Distance estimate) and
contrast to ≥1.0 on any preset. Newton + Distance estimate produces
the cleanest hard-boundary line art.

-----

## Using These Presets

**Via the API:**

```bash
curl -X POST https://your-api-url/v1/params/recommend \
  -H "Content-Type: application/json" \
  -d '{"description": "newton root basins coloring book"}'
```

**Via `presets.json`:**
The full parameter set for each preset is in `presets.json` in this repository.
Load the `parameters` object directly into any compatible fractal renderer.

**Via the live demo:**
[uuon-fractal-api Explorer](https://claude.ai/artifacts) — Module B · Advisor

-----

## License

Parameter sets in `presets.json` and `SHOWCASE.md` are released under MIT.  
The UUON Fractal Engine rendering source (GLSL shaders) is proprietary.  
Commercial use of the engine or API requires a UUON license.

Contact: [phi1@uuonfoundation.com](mailto:phi1@uuonfoundation.com)  
Instagram: @uuon.foundation  
Website: uuonfoundation.com

-----

*UUON Foundation Inc. · Phillip A. Ruiz III*
