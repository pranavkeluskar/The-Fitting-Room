# SPEC.md — Build Plan

> Execute the phases in order. Each phase ships something testable.

---

## GOAL (v1)

A local Streamlit app where Pranav uploads a fabric photo, clicks **Generate**, and gets back a 9-image mockup pack (3 chairs, 3 curtains, 3 sofas) rendered by Nano Banana Pro — under 90 seconds, downloadable as a zip.

---

## PHASE 0 — Setup (≈ 15 min)

1. Create venv: `python -m venv .venv && source .venv/bin/activate`
2. `pip install streamlit google-genai pillow python-dotenv`
3. Create `requirements.txt` with pinned versions.
4. Create `.env` with `GEMINI_API_KEY=...` and add `.env`, `outputs/`, `.venv/`, `__pycache__/` to `.gitignore`.
5. Sanity-check the API key: a one-line script that lists available models and confirms `gemini-2.5-flash-image*` is callable.

**Done when:** `python -c "from google import genai; ..."` returns a live model list.

---

## PHASE 1 — API wrapper (≈ 30 min)

Build `core/nano_banana.py` with a single clean function:

```python
def generate(
    fabric_path: str,
    product_ref_path: str,
    prompt: str,
    out_path: str | None = None,
) -> bytes:
    """Return PNG bytes; optionally save to out_path."""
```

Handles auth, multi-image input, basic retries on transient failure, and clear error messages.

**Test:** pass one fabric + one chair reference + the locked prompt. Eyeball the result. Iterate the prompt if the fabric reads wrong (scale, sheen, colour).

**Done when:** one fabric × one chair produces a photoreal mockup that preserves the fabric honestly.

---

## PHASE 2 — Prompts + library (≈ 30 min)

`core/prompts.py`
- Constant: `PROMPT_SKELETON` (the locked DNA from CLAUDE.md §7).
- Function: `build_prompt(category: str, product: str) -> str`.

`core/library.py`
- A typed catalog: `category → list[ProductRef]`, where each `ProductRef` has `name`, `image_path`, `application`, `product_description`.
- Lookup helpers.

**Done when:** `build_prompt("chairs", "wingback")` returns the full prompt string, ready to send.

---

## PHASE 3 — Reference seeding (≈ 1 hour, mostly waiting)

Generate the 9 reference images. Two paths:

- **Fast:** generate them manually in Google AI Studio using the brand aesthetic codes from CLAUDE.md §2. Commit the 9 jpgs into `/references/<category>/`.
- **Scrappy:** generate them programmatically using `nano_banana.generate` with a "neutral fabric placeholder" prompt. Riskier — manual is better for v1.

**Done when:** `/references/chairs/`, `/references/curtains/`, `/references/sofas/` each contain 3 images that match the brand aesthetic.

---

## PHASE 4 — Streamlit UI (≈ 45 min)

`app.py`:

- Title + one-line description.
- File uploader for the fabric photo. Show a preview.
- Multi-select: which categories to include (default: all three).
- **Generate** button.
- Progress indicator (1/9, 2/9, …).
- Output gallery, grouped by category, 3 across.
- **Download pack** button → zips `/outputs/<timestamp>/` and serves it.

Smart UX defaults: show each mockup as it completes (don't wait for all 9). Cache by `(fabric_hash, product_ref)` so re-runs are free.

**Done when:** Pranav can run `streamlit run app.py`, upload a fabric, get a full pack, and download it as a zip.

---

## PHASE 5 — Polish (open-ended)

Pick from these in priority order based on what Pranav notices when using it:

- Per-category prompt overrides (curtains often need different lighting than chairs).
- Side-by-side: original fabric swatch tile alongside each mockup.
- "Add cushion" / "Add headboard" / "Add slipper sofa" — expanding the library.
- Watermark / D'Decor branding option for sales decks.
- Negative-prompt list for failure modes (warped patterns, wrong scale, leather sneaking back in).
- Switch reference images for real product photography (replace AI-generated refs).
- (Later) Next.js port for team-wide deployment.

---

## DEFINITION OF DONE — v1

Pranav uploads `velvet_emerald.jpg`. Clicks Generate. Sees 9 photoreal mockups appear within ~90s. Downloads the pack. Sends it to a customer or an architect. They get it instantly.
