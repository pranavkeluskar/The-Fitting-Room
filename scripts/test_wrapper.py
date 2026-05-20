"""Phase 1 plumbing test.

Builds two trivial PIL images, calls core.nano_banana.generate(), and writes
the result to outputs/. This validates the wrapper end-to-end (auth,
multi-image input, model fallback, byte extraction, disk write) WITHOUT
needing real fabric/product photography.

The actual brand-quality test (fabric photo + chair reference + locked
prompt) is the SPEC's Phase 1 acceptance criterion and happens once we
have a fabric photo from Pranav.

Run from project root:
    .venv/bin/python scripts/test_wrapper.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

# Make project root importable when running this script directly.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.nano_banana import generate  # noqa: E402


ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "outputs" / "_phase1_plumbing"
TMP.mkdir(parents=True, exist_ok=True)


def make_test_images() -> tuple[Path, Path]:
    """Write two solid-color squares to disk so generate() can read them."""
    fabric = Image.new("RGB", (512, 512), color=(180, 60, 50))   # dusty red
    product = Image.new("RGB", (512, 512), color=(230, 225, 215))  # plaster
    fp = TMP / "fabric_test.png"
    pp = TMP / "product_test.png"
    fabric.save(fp)
    product.save(pp)
    return fp, pp


def main() -> int:
    fp, pp = make_test_images()
    out_path = TMP / "result.png"

    prompt = (
        "Generate a single photorealistic image of a small fabric swatch in "
        "the colour of the first image, lying flat on a plaster-coloured "
        "background like the second image. Soft north light, 35mm look, "
        "neutral. No leather, no text, no watermark."
    )

    print("Calling core.nano_banana.generate() with two synthetic images...")
    data = generate(
        fabric_path=fp,
        product_ref_path=pp,
        prompt=prompt,
        out_path=out_path,
        verbose=True,
    )
    print(f"\nOK — got {len(data):,} bytes; saved to {out_path}")

    # Quick sanity-check it really is an image
    img = Image.open(out_path)
    print(f"     image: {img.size[0]}x{img.size[1]} {img.format}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
