# CLAUDE.md — Fabric Application Studio

> Persistent context for Claude Code. Read this first, every session.

---

## 1. PROJECT

**Fabric Application Studio** is an internal tool for **D'Decor** and **FabriCare** (D'Decor Home Fabrics — DDHF). It takes a single fabric photograph and renders that fabric applied to a curated set of product references — chairs, curtains, sofas, cushions, headboards.

Output is a downloadable "mockup pack" for Sales (EBOs, MBOs), the Style Expert Service, and the AID (Architect & Interior Designer) community to help customers and pros visualize a fabric in real applications before purchase.

**Owner:** Pranav Keluskar — Head of Brand & Marketing, DDHF. Not a developer. Default to working code over deep configuration; explain trade-offs briefly.

**This is a vibe-coding session.** Ship a working local prototype. Skip auth, databases, deployment infra.

---

## 2. BRAND GUARDRAILS

Every generated image must respect these. They are non-negotiable.

- **Aesthetic benchmark:** Restoration Hardware catalog mood × Minotti / Molteni / BoConcept furniture sensibility.
- **No leather.** Ever. Upholstery is fabric only.
- **Luxury is quiet** — no flashy interiors, no decorative clutter, no influencer styling.
- **Photography logic:** 35mm or 50mm lens look, soft north light, shallow depth of field on the product, neutral plaster / limewash walls, matte oak or walnut floors.
- **Fabric must read honestly** — pile, weave, slub, sheen visible; pattern scale accurate to the source.
- **No visible logos, no on-image text, no watermarks** in the AI output.
- **Colour described in words**, not hex codes, in prompts.

---

## 3. ARCHITECTURE

Two images in, one image out.

```
Fabric photo (user upload)
         +
Product reference image (from local /references library)
         ↓
Gemini 2.5 Flash Image (a.k.a. Nano Banana Pro) API call
         ↓
Photoreal mockup
```

Repeat per product reference. Aggregate into a gallery + downloadable zip pack.

---

## 4. MODEL

**Google Gemini 2.5 Flash Image** — consumer-facing name *Nano Banana Pro*.

- **SDK:** `google-genai` (Python)
- **Model ID:** start with `gemini-2.5-flash-image-preview`. Before writing the wrapper, verify the current production model ID from Google's official docs — Google has been iterating on this family, and a `gemini-2.5-flash-image` (no `-preview`) or Pro variant may now be live.
- **Multi-image input:** pass fabric + product reference together as `contents` in the same request.
- **Auth:** API key from Google AI Studio, stored in `.env` as `GEMINI_API_KEY`. Never hardcode.

---

## 5. STACK

- Python 3.11+
- **Streamlit** for the UI (fastest path to a usable tool)
- `google-genai` for image generation
- `Pillow` for image I/O
- `python-dotenv` for env management

Streamlit chosen because it's local, single-page, and Pranav can run it himself. We graduate to Next.js later if Sales teams adopt it widely.

---

## 6. PRODUCT REFERENCE LIBRARY

Pre-curated product photos that fabrics get applied to. Phase 1 scope = 9 references across 3 categories:

**Chairs (3)**
- Wingback armchair — three-quarter view, plaster wall background
- Lounge chair (low, modernist) — side view
- Dining chair (slim back) — front-three-quarter

**Curtains (3)**
- Full-length pleated panel — light-filled window
- Sheer panel — soft daylight, backlit
- Café curtain — kitchen window context

**Sofas (3)**
- 3-seater straight — low, Minotti-style
- Modular L-shape — neutral living room
- Slipper sofa — editorial three-quarter

References live in `/references/<category>/<style>.jpg`.

For v1, these can be generated via Nano Banana Pro (manually, in Google AI Studio) using our locked aesthetic, then committed to the repo. Replace with real photography in a later phase.

---

## 7. LOCKED PROMPT DNA

Every generation uses this skeleton. Only `{application}` and `{product}` change per category.

```
Apply the provided fabric (first image) as the {application} of the {product}
shown in the second reference image.

Critical requirements:
- Preserve fabric pattern, weave, colour, and pattern scale EXACTLY as in the
  first image. Do not stylise or reinterpret the fabric.
- Preserve product silhouette, proportions, and scene composition EXACTLY as
  in the second image.
- Photoreal, editorial catalog quality.
- 35mm look, soft north light, shallow depth of field on the product.
- Background: neutral plaster wall, matte oak floor, minimal styling.
- No leather. No visible logos. No on-image text.
- Mood: Restoration Hardware × Minotti.
```

`{application}` values: `upholstery`, `curtain panels`, `cushion cover`, `headboard upholstery`.

Comment this generously in `core/prompts.py` — it's the part Pranav will tune most.

---

## 8. FOLDER STRUCTURE

```
fabric-app/
├── CLAUDE.md
├── SPEC.md
├── app.py                  # Streamlit entry
├── core/
│   ├── __init__.py
│   ├── nano_banana.py      # Gemini API wrapper
│   ├── prompts.py          # Locked prompt DNA + per-category builders
│   └── library.py          # Product reference catalog
├── references/
│   ├── chairs/
│   ├── curtains/
│   └── sofas/
├── outputs/                # Generated packs (gitignored)
├── .env                    # GEMINI_API_KEY (gitignored)
├── .gitignore
└── requirements.txt
```

---

## 9. WHAT NOT TO DO

- Don't add auth, user accounts, databases, or deployment infra. Local-only.
- Don't generate product reference images at runtime — they're a static, curated library.
- Don't let the model freestyle the scene. Compositional fidelity to the reference is the whole point of this app.
- Don't hardcode API keys.
- Don't write a 10-option config system. Smart defaults, one or two knobs.
- Don't ask Pranav to design the prompts from scratch — the DNA above is the start. Iterate from there.

---

## 10. WORKING STYLE WITH PRANAV

- Pranav thinks like a Chief Brand Officer, not an engineer. Lead with outcomes; reveal mechanics only when asked.
- When unsure about an API name or parameter, **verify with current Google docs before writing code**. Don't guess.
- Show working output early. One end-to-end happy path beats five half-built modules.
- Comment liberally where prompts are tuned. That's the surface Pranav will live in.
