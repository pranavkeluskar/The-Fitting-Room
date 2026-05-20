"""Application catalog for Fabric Application Studio v2.2.

Each Application is one thing the user can render their fabric onto.
There is no associated reference image — the model generates the scene
from scratch using the brand-anchored prompt in core/prompts.py.

v2.3 changes (2026-05-18 Pranav feedback round 2):
  - Lounge chair (Imola) restored — Pranav specifically asked for it back.
  - Pleated curtain dropped — kept only wave-fold, dramatic drop, drape detail.
  - Final list: 6 upholstery + 3 drapery = 9 total.

v2.2 changes (earlier same day):
  - Consolidated upholstery to Pranav's spec list (three-seater, modular,
    two-seater, wingback, sectional). Cushion dropped.
  - Removed the second wingback variant. Kept the modern slope-arm wingback
    (RH French Contemporary Slope Arm silhouette) under the simpler label
    "Wingback chair."
  - Brand silhouette anchor names are NO LONGER shown in the UI captions.
    The `silhouette` field below is purely internal — it travels into the
    prompt so the model picks up the silhouette, but it is not surfaced
    to the user.

To add an application:
    1. Append an Application(...) to APPLICATIONS below.
    2. Add a matching prompt in core/prompts.py keyed on the same `key`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Application:
    """One renderable application of a fabric (a chair, a curtain, etc.)."""

    key: str          # stable identifier — prompt lookup + cache filename
    label: str        # short label shown in the UI (NO brand names)
    silhouette: str   # internal — brand silhouette anchor for the prompt
    category: str     # "upholstery" or "drapery"
    short: str        # very short tag used in cache filename suffix


APPLICATIONS: Sequence[Application] = (
    # ── Upholstery (5) ─────────────────────────────────────────────────────
    Application(
        key="sofa_three_seater",
        label="Three-seater sofa",
        silhouette="Molteni Paul (Vincent Van Duysen)",
        category="upholstery",
        short="three-seater",
    ),
    Application(
        key="sofa_modular",
        label="Modular sofa",
        silhouette="RH Cloud Modular Sofa",
        category="upholstery",
        short="modular",
    ),
    Application(
        key="sofa_two_seater",
        label="Two-seater sofa",
        silhouette="RH Belgian Track Arm 2-Cushion Sofa",
        category="upholstery",
        short="two-seater",
    ),
    Application(
        key="wingback",
        label="Wingback chair",
        silhouette="RH French Contemporary Slope Arm Wingback",
        category="upholstery",
        short="wingback",
    ),
    Application(
        key="sectional",
        label="Sectional sofa",
        silhouette="Minotti Freeman Seating System",
        category="upholstery",
        short="sectional",
    ),
    Application(
        key="lounge_imola",
        label="Lounge chair",
        silhouette="BoConcept Imola",
        category="upholstery",
        short="lounge",
    ),

    # ── Drapery (3) ────────────────────────────────────────────────────────
    Application(
        key="curtain_wave",
        label="Wave-fold curtain",
        silhouette="Modern S-fold / ripple-fold, floor length",
        category="drapery",
        short="curtain-wave",
    ),
    Application(
        key="drape_dramatic",
        label="Dramatic fabric drop",
        silhouette="Sculptural drape from ceiling, pooled at floor",
        category="drapery",
        short="drape-drop",
    ),
    Application(
        key="drape_detail",
        label="Drape detail",
        silhouette="Close-up of a single fold; texture-forward",
        category="drapery",
        short="drape-detail",
    ),
)


UPHOLSTERY: tuple[Application, ...] = tuple(
    a for a in APPLICATIONS if a.category == "upholstery"
)
DRAPERY: tuple[Application, ...] = tuple(
    a for a in APPLICATIONS if a.category == "drapery"
)


def by_key(key: str) -> Application:
    for a in APPLICATIONS:
        if a.key == key:
            return a
    raise KeyError(
        f"No application with key {key!r}. Known: {[a.key for a in APPLICATIONS]}"
    )


def for_use_type(use_type: str) -> tuple[Application, ...]:
    """`use_type` is 'upholstery', 'drapery', or 'both'."""
    ut = use_type.lower()
    if ut == "upholstery":
        return UPHOLSTERY
    if ut == "drapery":
        return DRAPERY
    if ut == "both":
        return tuple(APPLICATIONS)
    raise ValueError(f"Unknown use_type {use_type!r}")
