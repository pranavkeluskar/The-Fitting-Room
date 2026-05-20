"""Fabric Application Studio — Streamlit entry, v2.1.

Run from project root with the venv active:
    .venv/bin/streamlit run app.py

v2.1 changes (2026-05-18 Pranav feedback):
  - Removed per-application checkboxes. The only choice the user makes is
    USE TYPE (Upholstery / Drapery / Both). All apps in that category
    render automatically.
  - Gallery is now the primary post-Generate surface, prominent and
    inline. Download is demoted to a small secondary action at the very
    bottom.
  - Pushed editorial styling further: Google Fonts (Cormorant Garamond +
    Inter), pill-style category selector, larger hero, more whitespace,
    auto-show of cached results so re-running is instant.
"""

from __future__ import annotations

import hashlib
import io
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

# Production deployment bridge: Streamlit Cloud stores secrets in st.secrets,
# but core/nano_banana.py reads from os.environ (via python-dotenv). Mirror
# the key from st.secrets to os.environ before importing core modules so
# the same code runs locally (via .env) and on Streamlit Cloud (via secrets).
try:
    if "GEMINI_API_KEY" in st.secrets and "GEMINI_API_KEY" not in os.environ:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    # Local dev: no st.secrets file; .env handles it.
    pass

from core.library import Application, by_key, for_use_type
from core.nano_banana import generate
from core.prompts import get as get_prompt


ROOT = Path(__file__).resolve().parent
OUTPUTS_ROOT = ROOT / "outputs"
# v2.3: bumped cache root again so v2.2's prop-stripped renders aren't
# served. v2.3 scenes are populated with AD-level set dressing.
CACHE_ROOT = OUTPUTS_ROOT / "cache_v2_3"


# ---------------------------------------------------------------------------
# Editorial styling — single injected CSS block
# ---------------------------------------------------------------------------

_CSS = """
<style>
/* Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

/* Hide Streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
.stDeployButton { display: none !important; }

/* Page width + spacing */
.block-container {
    max-width: 1080px;
    padding-top: 4rem;
    padding-bottom: 6rem;
}

/* Base typography */
.stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #3A3633;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-weight: 500 !important;
    letter-spacing: -0.015em !important;
    color: #1F1A17 !important;
}
.stApp h1 {
    font-size: 3.75rem !important;
    line-height: 1.05 !important;
    margin-top: 0 !important;
    margin-bottom: 0.5rem !important;
    font-weight: 500 !important;
}
.stApp h2 {
    font-size: 2.25rem !important;
    margin-top: 3.5rem !important;
    margin-bottom: 1.25rem !important;
    font-weight: 500 !important;
}
.stApp h3 {
    font-size: 1.35rem !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.75rem !important;
}

.eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.22em;
    font-size: 0.68rem;
    color: #8A7E72;
    margin-bottom: 0.65rem;
    font-weight: 500;
}
.lede {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 1.3rem !important;
    color: #5A5048 !important;
    font-style: italic;
    margin-top: 0.25rem;
    margin-bottom: 3rem;
    max-width: 640px;
    line-height: 1.4;
}

/* File uploader */
[data-testid="stFileUploader"] section {
    background: #EFEAE0 !important;
    border: 1px dashed #B8A88E !important;
    border-radius: 0 !important;
    padding: 2.5rem 1.5rem !important;
}
[data-testid="stFileUploader"] section > div:first-child {
    font-family: 'Inter', sans-serif !important;
    color: #5A5048 !important;
}
[data-testid="stFileUploader"] section button {
    background: transparent !important;
    color: #6B4F3A !important;
    border: 1px solid #6B4F3A !important;
    border-radius: 0 !important;
    padding: 0.55rem 1.5rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stFileUploader"] small {
    color: #8A7E72 !important;
    font-size: 0.68rem !important;
}

/* Pill-style radio (Use type selector) */
.stRadio > div {
    gap: 0 !important;
    display: inline-flex !important;
    background: #EFEAE0;
    border: 1px solid #D9CFC0;
    padding: 4px;
}
.stRadio > div > label {
    margin: 0 !important;
    padding: 0.55rem 1.5rem !important;
    border-radius: 0 !important;
    cursor: pointer;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #5A5048 !important;
    transition: all 0.15s;
}
.stRadio > div > label:hover {
    color: #1F1A17 !important;
}
.stRadio > div > label > div:first-child {
    display: none !important;  /* hide the radio circle */
}
.stRadio > div > label[data-baseweb="radio"] > div:nth-child(2) {
    font-weight: 500 !important;
}
.stRadio > div > label > div:nth-child(2) > div {
    color: inherit !important;
}
/* highlight selected pill */
.stRadio > div > label:has(input:checked) {
    background: #1F1A17 !important;
    color: #F8F4EE !important;
}
.stRadio > div > label:has(input:checked) > div:nth-child(2) > div {
    color: #F8F4EE !important;
}

/* Primary buttons (Generate) */
.stButton > button[kind="primary"] {
    background: #1F1A17 !important;
    color: #F8F4EE !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 1rem 2.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.14em !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button[kind="primary"]:hover {
    background: #6B4F3A !important;
}

/* Secondary download button (smaller, lower-key) */
.stDownloadButton > button {
    background: transparent !important;
    color: #8A7E72 !important;
    border: 1px solid #B8A88E !important;
    border-radius: 0 !important;
    padding: 0.55rem 1.5rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-size: 0.72rem !important;
    font-weight: 400 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Captions */
.caption {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-style: italic;
    color: #5A5048;
    font-size: 1.05rem;
    text-align: center;
    margin-top: 0.75rem;
    margin-bottom: 2.5rem;
    letter-spacing: 0.01em;
}
.cost-note {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-style: italic;
    color: #8A7E72;
    font-size: 1rem;
    margin-top: 0.75rem;
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid #D9CFC0 !important;
    margin: 3rem 0 !important;
}

/* Progress bar */
.stProgress > div > div > div > div { background-color: #1F1A17 !important; }
.stProgress > div > div > div { background-color: #EFEAE0 !important; }
</style>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fabric_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:12]


def cache_dir_for(fab_hash: str) -> Path:
    d = CACHE_ROOT / fab_hash
    d.mkdir(parents=True, exist_ok=True)
    return d


def mockup_path(cache_dir: Path, app: Application) -> Path:
    return cache_dir / f"mockup_{app.short}.jpg"


def render_or_cached(
    fabric_path: Path, app: Application, cache_dir: Path
) -> tuple[Path, bool]:
    """Returns (mockup_path, was_cached)."""
    out_path = mockup_path(cache_dir, app)
    if out_path.exists():
        return out_path, True
    generate(fabric_path=fabric_path, prompt=get_prompt(app.key), out_path=out_path)
    return out_path, False


def build_zip(cache_dir: Path, apps: list[Application]) -> bytes:
    """Pack the input fabric + selected mockups into an in-memory zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # input fabric
        for f in cache_dir.iterdir():
            if f.is_file() and f.name.startswith("_input_"):
                zf.write(f, arcname=f.name)
        # selected mockups
        for app in apps:
            p = mockup_path(cache_dir, app)
            if p.exists():
                zf.write(p, arcname=f"mockup_{app.short}.jpg")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def render_gallery(
    apps: list[Application],
    cache_dir: Path,
) -> None:
    """Render all mockup images in a 2-column grid with serif italic captions."""
    cols_per_row = 2
    rows = (len(apps) + cols_per_row - 1) // cols_per_row
    for r in range(rows):
        cols = st.columns(cols_per_row, gap="large")
        for c in range(cols_per_row):
            idx = r * cols_per_row + c
            if idx >= len(apps):
                continue
            app = apps[idx]
            p = mockup_path(cache_dir, app)
            with cols[c]:
                if p.exists():
                    st.image(Image.open(p), use_container_width=True)
                    st.markdown(
                        f'<div class="caption">{app.label}</div>',
                        unsafe_allow_html=True,
                    )


def main() -> None:
    st.set_page_config(
        page_title="Fabric Application Studio",
        page_icon="·",
        layout="centered",
    )
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Hero ───────────────────────────────────────────────────────────────
    st.markdown('<div class="eyebrow">D\'Decor · Brand Desk</div>', unsafe_allow_html=True)
    st.markdown("# Fabric Application Studio")
    st.markdown(
        '<div class="lede">Upload a fabric — a phone shot is enough — '
        'and see it rendered onto chairs, sofas, and drapery, in '
        'editorial photography.</div>',
        unsafe_allow_html=True,
    )

    # ── Upload ─────────────────────────────────────────────────────────────
    uploaded = st.file_uploader(
        " ",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
        help=(
            "Frame the fabric. Angle, lighting, and slight background "
            "clutter are all OK — the model is told to extract the fabric "
            "and ignore the rest."
        ),
    )

    if uploaded is None:
        return

    fabric_bytes = uploaded.getvalue()
    fab_hash = fabric_hash(fabric_bytes)
    cdir = cache_dir_for(fab_hash)
    fabric_in_cache = cdir / f"_input_{uploaded.name}"
    if not fabric_in_cache.exists():
        fabric_in_cache.write_bytes(fabric_bytes)

    # ── Preview + Use-type selector ────────────────────────────────────────
    st.markdown("---")
    col_preview, col_picker = st.columns([1, 1.2], gap="large")

    with col_preview:
        st.markdown("### Your fabric")
        # exif_transpose: iPhone JPEGs carry orientation in EXIF metadata
        # rather than rotating pixels. Without this the preview (and the
        # bytes Gemini sees) come out sideways for portrait shots.
        preview_img = ImageOps.exif_transpose(
            Image.open(io.BytesIO(fabric_bytes))
        )
        st.image(preview_img, use_container_width=True)

    with col_picker:
        st.markdown("### Render onto")
        use_type_label = st.radio(
            "Use type",
            options=["Upholstery", "Drapery", "Both"],
            horizontal=True,
            label_visibility="collapsed",
            index=0,
        )
        use_type = use_type_label.lower()
        apps = list(for_use_type(use_type))

        # Cached / cost summary
        cached_count = sum(1 for a in apps if mockup_path(cdir, a).exists())
        new_count = len(apps) - cached_count
        cost = new_count * 0.12

        if new_count == 0:
            st.markdown(
                f'<div class="cost-note">All {len(apps)} mockups are already '
                f'rendered — showing below.</div>',
                unsafe_allow_html=True,
            )
            run = False
            show_cached = True
        else:
            label = (
                f"Generate {new_count} mockup{'s' if new_count != 1 else ''}"
                if cached_count == 0
                else f"Generate {new_count} new (· {cached_count} cached)"
            )
            run = st.button(label, type="primary", use_container_width=False)
            st.markdown(
                f'<div class="cost-note">{len(apps)} renders · '
                f'≈ ${cost:.2f}{" net new" if cached_count else ""}</div>',
                unsafe_allow_html=True,
            )
            show_cached = False

    # ── Gallery ────────────────────────────────────────────────────────────
    if not (run or show_cached):
        return

    st.markdown("## Mockups")

    if show_cached:
        # All already rendered — show inline immediately, no progress UI.
        render_gallery(apps, cdir)
    else:
        # Build placeholder grid first so all spots are visible upfront.
        cols_per_row = 2
        rows = (len(apps) + cols_per_row - 1) // cols_per_row
        placeholders: dict[str, "st.delta_generator.DeltaGenerator"] = {}
        cap_placeholders: dict[str, "st.delta_generator.DeltaGenerator"] = {}
        for r in range(rows):
            cols = st.columns(cols_per_row, gap="large")
            for c in range(cols_per_row):
                idx = r * cols_per_row + c
                if idx >= len(apps):
                    continue
                app = apps[idx]
                with cols[c]:
                    placeholders[app.key] = st.empty()
                    cap_placeholders[app.key] = st.empty()
                    placeholders[app.key].markdown(
                        f'<div style="padding: 4rem 1rem; background: #EFEAE0; '
                        f'text-align: center; color: #8A7E72; '
                        f'font-family: Cormorant Garamond, Georgia, serif; '
                        f'font-style: italic;">'
                        f'Rendering {app.label.lower()}…</div>',
                        unsafe_allow_html=True,
                    )

        progress = st.progress(0.0)
        progress_msg = st.empty()
        done = 0

        with ThreadPoolExecutor(max_workers=min(6, len(apps))) as pool:
            futures = {
                pool.submit(render_or_cached, fabric_in_cache, a, cdir): a
                for a in apps
            }
            for fut in as_completed(futures):
                app = futures[fut]
                try:
                    p, was_cached = fut.result()
                    placeholders[app.key].image(Image.open(p), use_container_width=True)
                    cap_placeholders[app.key].markdown(
                        f'<div class="caption">{app.label}</div>',
                        unsafe_allow_html=True,
                    )
                except Exception as e:
                    placeholders[app.key].error(
                        f"{app.label} failed — {type(e).__name__}: {e}"
                    )
                done += 1
                progress.progress(done / len(apps))
                progress_msg.markdown(
                    f'<div class="cost-note">{done} of {len(apps)} done</div>',
                    unsafe_allow_html=True,
                )

        progress.empty()
        progress_msg.empty()

    # ── Download (secondary, footer) ───────────────────────────────────────
    rendered = [a for a in apps if mockup_path(cdir, a).exists()]
    if rendered:
        st.markdown("---")
        zip_bytes = build_zip(cdir, rendered)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "Download as zip",
            data=zip_bytes,
            file_name=f"fabric_pack_{fab_hash}_{timestamp}.zip",
            mime="application/zip",
        )


if __name__ == "__main__":
    main()
