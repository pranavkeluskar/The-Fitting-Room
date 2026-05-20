"""Phase 0 sanity check.

Confirms three things end-to-end:
    1. .env contains a GEMINI_API_KEY.
    2. The key can reach the Gemini API at all (cheap text call).
    3. The key can call the image-generation model(s) we plan to use.

The Gemini Developer API does not expose `models.list()` for all key tiers
(returns 501 UNIMPLEMENTED), so we probe directly with a tiny request per
candidate model and report which one the key actually has access to.

Run from the project root, with the venv active:
    python scripts/sanity_check.py
"""

from __future__ import annotations

import io
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from PIL import Image


KEY_PROBE_MODEL = "gemini-2.5-flash"           # cheap text model, used only to validate the key
IMAGE_MODELS = [
    ("gemini-3-pro-image-preview", "Nano Banana Pro — preferred, paid preview"),
    ("gemini-2.5-flash-image",     "Nano Banana Flash — GA fallback"),
]


def probe_text(client: genai.Client) -> tuple[bool, str]:
    """Cheapest possible call: does the key work at all?"""
    try:
        resp = client.models.generate_content(
            model=KEY_PROBE_MODEL,
            contents="ping",
            config=types.GenerateContentConfig(max_output_tokens=1),
        )
        # Even with max_output_tokens=1 we may get an empty response; what matters
        # is the call returned without an APIError.
        _ = resp.text or ""
        return True, "ok"
    except APIError as e:
        return False, f"{e.code} {e.message}"
    except Exception as e:  # pragma: no cover
        return False, f"{type(e).__name__}: {e}"


def probe_image(client: genai.Client, model: str) -> tuple[bool, str]:
    """Try a minimal image-generation call against `model`."""
    try:
        resp = client.models.generate_content(
            model=model,
            contents="A single small white square on a plain grey background.",
            config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
        # Inspect parts for actual image bytes
        for part in resp.candidates[0].content.parts:
            inline = getattr(part, "inline_data", None)
            if inline and inline.data:
                img = Image.open(io.BytesIO(inline.data))
                return True, f"got image {img.size[0]}x{img.size[1]} ({img.format})"
        return False, "call succeeded but no image bytes in response"
    except APIError as e:
        return False, f"{e.code} {e.message}"
    except Exception as e:  # pragma: no cover
        return False, f"{type(e).__name__}: {e}"


def main() -> int:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set in .env", file=sys.stderr)
        return 1

    client = genai.Client(api_key=api_key)

    print("1. Validating API key with a cheap text call...")
    ok, detail = probe_text(client)
    print(f"   {KEY_PROBE_MODEL:40s} -> {'OK' if ok else 'FAIL'}  ({detail})")
    if not ok:
        print("\nERROR: the key is invalid or has no API access. Stopping.", file=sys.stderr)
        return 2

    print("\n2. Probing image-generation models with a 1-image test call...")
    any_image_ok = False
    chosen: str | None = None
    for model, note in IMAGE_MODELS:
        ok, detail = probe_image(client, model)
        marker = "OK  " if ok else "FAIL"
        print(f"   {model:40s} -> {marker}  ({detail})  [{note}]")
        if ok and chosen is None:
            chosen = model
            any_image_ok = True

    if not any_image_ok:
        print(
            "\nERROR: no image-generation model is callable with this key.\n"
            "  - Confirm billing is enabled in Google AI Studio.\n"
            "  - Pro image preview requires paid tier.\n"
            "  - Flash image is GA but still requires billing.",
            file=sys.stderr,
        )
        return 3

    print(f"\nPhase 0 sanity check passed. Default image model: {chosen}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
