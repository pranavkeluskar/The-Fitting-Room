"""Gemini image-generation wrapper for the Fabric Application Studio.

Single public entry point:
    generate(fabric_path, product_ref_path, prompt, out_path=None) -> bytes

The wrapper auto-selects which Nano Banana model to use at runtime:

    1. gemini-3-pro-image-preview   (Nano Banana Pro — brand-quality default)
    2. gemini-2.5-flash-image       (Nano Banana Flash — GA fallback)

Why a fallback chain matters: during Phase 0 we saw Pro return 503
("high demand") while Flash worked fine. We want the app to keep producing
mockups when Pro is hot, not break for Sales. Pro is tried first; on
transient errors we retry briefly, then fall through to Flash. Permanent
4xx errors are raised so the caller sees real bugs.
"""

from __future__ import annotations

import io
import os
import time
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from PIL import Image, ImageOps


PREFERRED_MODELS: tuple[str, ...] = (
    "gemini-3-pro-image-preview",
    "gemini-2.5-flash-image",
)

# 5xx + 429 = "this model is having a moment" — retry, then fall through.
_TRANSIENT_THEN_FALLBACK = {429, 500, 502, 503, 504}
# Model-specific availability — don't retry, just try the next model.
_FALLBACK_IMMEDIATELY = {403, 404}
# Request-shape problems — Flash will fail the same way, so raise.
_HARD_FAIL = {400}


_client: genai.Client | None = None


def _client_once() -> genai.Client:
    """Lazy-init a single Gemini client. Reads GEMINI_API_KEY from .env."""
    global _client
    if _client is None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY missing. Add it to .env at the project root."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _load_image(path: str | Path) -> Image.Image:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Image not found: {p}")
    img = Image.open(p)
    img.load()  # force decode now so we surface corrupt-file errors here
    # iPhone JPEGs store EXIF orientation rather than rotating pixels in place.
    # PIL doesn't honour that by default — apply it explicitly here, otherwise
    # portrait phone shots reach Gemini sideways and the model renders the
    # fabric pattern at the wrong orientation on the mockup.
    img = ImageOps.exif_transpose(img)
    return img


def _extract_image_bytes(response) -> bytes:
    """Pull the first inline image payload out of a Gemini response."""
    candidates = getattr(response, "candidates", None) or []
    for cand in candidates:
        parts = getattr(cand.content, "parts", None) or []
        for part in parts:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                return inline.data
    raise RuntimeError(
        "Gemini returned no image bytes. The model may have refused the "
        "request (e.g., safety filter) or returned only text."
    )


def _call(
    client: genai.Client,
    model: str,
    prompt: str,
    fabric: Image.Image,
) -> bytes:
    """One shot at one model. Raises APIError on HTTP failure.

    v2: single image input (the fabric swatch). The application/scene is
    described entirely in `prompt` — no reference image. The model
    generates the scene from scratch.
    """
    response = client.models.generate_content(
        model=model,
        contents=[prompt, fabric],
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )
    return _extract_image_bytes(response)


def generate(
    fabric_path: str | Path,
    prompt: str,
    out_path: str | Path | None = None,
    *,
    models: Iterable[str] = PREFERRED_MODELS,
    max_retries_per_model: int = 2,
    verbose: bool = False,
) -> bytes:
    """Render the fabric at `fabric_path` as the scene described in `prompt`.

    v2: single-image input. The full subject + scene is described in the
    prompt; no product reference image is passed.

    Returns the raw image bytes as Gemini emits them — typically JPEG from
    Pro and PNG from Flash. If `out_path` is given, also writes the bytes
    to disk verbatim (parent dirs are created); pick the extension to
    match what you expect from the model you're calling.

    Walks `models` in order. For each model, retries transient errors
    (5xx / 429) up to `max_retries_per_model` times with linear backoff,
    then falls through to the next model. Permission / availability errors
    (403, 404) skip retries and fall through immediately. A 400 bails out
    hard — Flash would reject the same request.
    """
    client = _client_once()
    fabric = _load_image(fabric_path)

    last_err: Exception | None = None

    for model in models:
        for attempt in range(max_retries_per_model + 1):
            try:
                if verbose:
                    print(f"  -> {model} (attempt {attempt + 1})")
                data = _call(client, model, prompt, fabric)

                if out_path is not None:
                    out = Path(out_path)
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(data)
                    if verbose:
                        print(f"     saved {len(data):,} bytes -> {out}")

                return data

            except APIError as e:
                last_err = e
                code = getattr(e, "code", None)

                if code in _HARD_FAIL:
                    raise

                if code in _FALLBACK_IMMEDIATELY:
                    if verbose:
                        print(f"     {code} on {model} — falling through")
                    break  # next model

                if code in _TRANSIENT_THEN_FALLBACK:
                    if attempt < max_retries_per_model:
                        sleep_s = 2 ** attempt  # 1s, 2s
                        if verbose:
                            print(f"     {code} on {model} — retry in {sleep_s}s")
                        time.sleep(sleep_s)
                        continue
                    if verbose:
                        print(f"     {code} on {model} exhausted retries — falling through")
                    break  # next model

                # Unknown API error — retry once, then fall through.
                if attempt < max_retries_per_model:
                    time.sleep(1)
                    continue
                break

    raise RuntimeError(
        f"All Nano Banana models exhausted. Last error: {last_err}"
    ) from last_err
