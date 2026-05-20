"""Phase 1.3 acceptance test — real fabric × both sofas.

Renders the given fabric onto both fixed sofa references in parallel,
using the locked PROMPT from core/prompts.py. Single source of truth —
the Streamlit app uses the same prompt.

Run from project root:
    .venv/bin/python scripts/phase1_acceptance.py [fabric_path]

If no fabric_path is given, defaults to fabric_1_chenille.jpg.
Output filenames are tagged with the fabric stem, so re-runs against
different fabrics don't overwrite each other.
"""

from __future__ import annotations

import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.nano_banana import generate  # noqa: E402
from core.prompts import PROMPT        # noqa: E402  — single source of truth


ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "_phase1_acceptance"
DEFAULT_FABRIC = OUT_DIR / "fabric_1_chenille.jpg"

SOFAS: list[tuple[str, Path]] = [
    ("modular", ROOT / "references" / "sofas" / "sofa_modular.jpg"),
    ("curved",  ROOT / "references" / "sofas" / "sofa_curved.jpg"),
]


def resolve_fabric(argv: list[str]) -> Path:
    """Fabric path from CLI arg[1], else DEFAULT_FABRIC."""
    if len(argv) > 1:
        return Path(argv[1]).expanduser().resolve()
    return DEFAULT_FABRIC


def render_one(
    name: str, sofa_path: Path, fabric_path: Path, tag: str
) -> tuple[str, Path, float, str | None]:
    out_path = OUT_DIR / f"mockup_{name}_{tag}.jpg"
    start = time.time()
    try:
        generate(
            fabric_path=fabric_path,
            product_ref_path=sofa_path,
            prompt=PROMPT,
            out_path=out_path,
        )
        return name, out_path, time.time() - start, None
    except Exception as e:  # surface whatever broke
        return name, out_path, time.time() - start, f"{type(e).__name__}: {e}"


def main() -> int:
    fabric_path = resolve_fabric(sys.argv)
    if not fabric_path.exists():
        print(f"ERROR: fabric photo missing at {fabric_path}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # mockup output tag derived from fabric filename stem,
    # so re-runs against different fabrics don't overwrite each other.
    tag = fabric_path.stem

    print(f"Fabric: {fabric_path.name}  (tag: {tag})")
    for name, p in SOFAS:
        print(f"Sofa:   {name:10s} {p.name}")
    print("\nRendering both sofas in parallel via Pro (Flash fallback if needed)...\n")

    overall = time.time()
    with ThreadPoolExecutor(max_workers=len(SOFAS)) as pool:
        results = list(
            pool.map(lambda args: render_one(*args, fabric_path, tag), SOFAS)
        )

    elapsed = time.time() - overall
    print(f"Total wall time: {elapsed:.1f}s\n")
    for name, out_path, dt, err in results:
        if err:
            print(f"  {name:10s} FAIL ({dt:.1f}s)  {err[:200]}")
        else:
            print(f"  {name:10s} OK   ({dt:.1f}s)  -> {out_path.relative_to(ROOT)}")

    failures = [r for r in results if r[3] is not None]
    return 0 if not failures else 2


if __name__ == "__main__":
    sys.exit(main())
