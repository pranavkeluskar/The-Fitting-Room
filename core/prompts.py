"""Brand-locked prompt DNA for Fabric Application Studio v2.3.

v2.3 changes (2026-05-18 Pranav feedback round 2):
    - Course-correction on "editorial." v2.2 stripped scenes to bare product
      shots (no props, no context). Pranav wanted AD-curated interiors —
      populated with intent, layered, lived-in, designed by a master. Not
      Pottery Barn catalog, not empty atelier, but Architectural Digest /
      Vogue Living / T Magazine interior stories.
    - Photography direction made specific: named interior photographers
      (François Halard, Stephen Kent Johnson, Pieter Estersohn, William
      Waldron, Simon Watson, Joshua McHugh), real lens choices, specific
      camera heights at subject-seat level, time-of-day lighting cues,
      mixed natural + practical (lamps lit in scene).
    - Each scene now has 3–5 deliberate AD-level set-dressing elements:
      vintage Italian floor lamps, kilim rugs, Pierre Jeanneret accent
      chairs, travertine coffee tables, period art on walls, Saarinen
      side tables, Noguchi lanterns, etc. Provenance and patina, not
      generic catalog objects.

Designer / photographer references named in the prompts:
    Architects/designers:  Vincent Van Duysen · Axel Vervoordt · Joseph
                            Dirand · John Pawson · Studio KO · Pierre
                            Jeanneret · Eero Saarinen
    Photographers:          François Halard · Stephen Kent Johnson ·
                            Pieter Estersohn · William Waldron · Simon
                            Watson · Joshua McHugh
    Publications:           Architectural Digest · Vogue Living · T
                            Magazine · House & Garden

Anti-AI-tell language explicitly added: asymmetric composition, patina
on surfaces, mixed light sources with practical lamps lit, layered depth,
provenance objects (not catalog-anonymous).

Brand silhouette anchors (still inside prompts; hidden from UI):
    Wingback:               RH French Contemporary Slope Arm Wingback
    Three-seater sofa:      Molteni Paul (Vincent Van Duysen)
    Modular sofa:           RH Cloud Modular Sofa
    Two-seater sofa:        RH Belgian Track Arm 2-Cushion Sofa
    Sectional:              Minotti Freeman Seating System
    Lounge:                 BoConcept Imola

Fabric fidelity language (color / texture / pile / orientation) unchanged
from v1.1 — that's the hardest-won baseline.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Shared blocks
# ---------------------------------------------------------------------------

_FABRIC_INTRO = """Treat the FIRST image as a fabric swatch reference. The photo may be phone-shot — possibly angled, with extraneous items in frame (ruler edges, paper card backgrounds, tables, hands, or loose threads at the cut edge of the swatch). Ignore everything in the frame that is not the fabric itself. Extract the fabric's colour, weave structure, pile, slub, and pattern scale."""

_FABRIC_FIDELITY = """Fabric fidelity:
- COLOUR: match the fabric's colour EXACTLY as it appears in the swatch. Do not shift hue or temperature. Do not "neutralise" or "correct" the colour. If the swatch reads gold, render gold. If navy, render navy. If teal, render teal.
- TEXTURE: preserve the fabric's pattern, weave, and pattern scale exactly. Texture must be honest — visible pile, weave, slub, and sheen.
- PILE: if the swatch shows visible pile depth (shag, fur-like, long-fibre, plush velvet), render that pile depth. Do not flatten high-pile fabrics into bouclé.
- ORIENTATION: render the fabric's pattern in its natural upright orientation as shown in the swatch."""

# v2.3 quality block: positive about what GOOD AD photography looks like,
# rather than just listing things to avoid. Counteracts v2.2's over-strip.
_QUALITY = """Photography and atmosphere:
- This is editorial interior photography in the style of {photographer}, shot for Architectural Digest / Vogue Living / T Magazine.
- The room should feel inhabited, considered, designed by a master — populated with intent, NOT empty, NOT stripped, NOT minimal-to-the-point-of-product-shot. Layered foreground / mid-ground / background.
- Surfaces show patina and lived-in character: aged plaster, worn oak, patinated brass, sun-faded textiles. Not catalog-new, not stock-clean.
- Every object in frame must read as collected, vintage, or designer-specified — never anonymous catalog filler.
- Mixed light sources: natural directional daylight from a window outside the frame, PLUS a warm practical lamp lit somewhere in the scene (table lamp, floor lamp, picture light) casting an ambient pool.
- Cinematic shallow depth of field on the subject; foreground and background subtly defocused but readable.
- Asymmetric composition — subject off-centre, not perfectly square to the camera.

Camera direction:
- Lens: {lens}.
- Camera height: {camera_height}.
- {camera_extras}

Strict constraints:
- No leather furniture anywhere in the frame.
- No visible logos, brand tags, or labels on any furniture or object.
- No on-image text. No watermarks."""


def _assemble(
    subject: str,
    scene: str,
    photographer: str,
    lens: str,
    camera_height: str,
    camera_extras: str = "",
) -> str:
    return "\n\n".join([
        _FABRIC_INTRO,
        f"Generate a photoreal editorial image of {subject}",
        scene,
        _FABRIC_FIDELITY,
        _QUALITY.format(
            photographer=photographer,
            lens=lens,
            camera_height=camera_height,
            camera_extras=camera_extras or "Composition asymmetric, subject off-centre.",
        ),
    ])


# ---------------------------------------------------------------------------
# Per-application prompts — populated, AD-level
# ---------------------------------------------------------------------------

PROMPTS: dict[str, str] = {}

# ── UPHOLSTERY ──────────────────────────────────────────────────────────────

PROMPTS["wingback"] = _assemble(
    subject=(
        "a single wingback armchair in the style of Restoration Hardware's "
        "French Contemporary Slope Arm Wingback Chair — modern restrained "
        "slope-arm silhouette with subtle wings, three-quarter view, "
        "upholstered in the fabric shown above."
    ),
    scene=(
        "Scene — a corner of an architect's private library:\n"
        "- Wall behind the chair: floor-to-ceiling built-in shelves of "
        "stacked monographs, cloth-bound first editions, a few small "
        "ceramic vessels interspersed at the shelf line.\n"
        "- Beside the chair, slightly behind: a vintage 1960s Italian "
        "floor lamp in patinated brass, LIT, casting a warm pool of "
        "light onto the chair's arm.\n"
        "- Underfoot: a worn antique kilim rug in faded madder and indigo.\n"
        "- Architecture: high ceiling, original wide-plank oak floor with "
        "natural patina, raw plaster wall to the right with subtle texture.\n"
        "- Late afternoon, golden raking light from a tall sash window "
        "outside the left of the frame."
    ),
    photographer="François Halard",
    lens="50mm prime",
    camera_height="at chair-seat level, slight upward angle preserving vertical lines",
    camera_extras=(
        "Composition: chair off-centre to the right, the wall of books "
        "filling the left third, the lit lamp's glow anchoring the warm "
        "mid-ground."
    ),
)

PROMPTS["sofa_three_seater"] = _assemble(
    subject=(
        "a modern three-seater sofa in the style of Molteni's Paul (Vincent "
        "Van Duysen design) — single deep seat cushion, clean low straight "
        "arms, slim die-cast aluminum legs in polished pewter — front-three-"
        "quarter view, upholstered in the fabric shown above."
    ),
    scene=(
        "Scene — the living room of a restrained Parisian apartment "
        "(Joseph Dirand atmosphere):\n"
        "- Architecture: original parquet de Versailles oak floor, tall "
        "plaster walls with subtle moldings near the ceiling, a marble "
        "fireplace partially visible to the side.\n"
        "- In front of the sofa: a single vintage 1970s Italian travertine "
        "coffee table — low, substantial, slightly off-centre.\n"
        "- On the table: a single low ceramic bowl in a muted earth tone, "
        "and a stack of two or three art monographs.\n"
        "- Above the sofa on the wall: a large abstract painting in muted "
        "earth and oxblood tones, framed simply.\n"
        "- To the side: a vintage Pierre Jeanneret cane-back chair (NOT "
        "upholstered in the swatch fabric — natural cane and teak) as a "
        "contrast accent piece.\n"
        "- A worn neutral wool rug anchors the seating area.\n"
        "- Late morning, diffused soft daylight from tall French windows "
        "outside the right of frame; a single brass picture light over the "
        "painting is LIT, casting a warm glow."
    ),
    photographer="Stephen Kent Johnson",
    lens="35mm",
    camera_height="at sofa-seat level, looking slightly up",
    camera_extras=(
        "Layered composition: coffee table foreground (slightly defocused), "
        "sofa centred in the plane of focus, painting and architecture "
        "in the soft background."
    ),
)

PROMPTS["sofa_modular"] = _assemble(
    subject=(
        "a modern deep modular sofa in the style of Restoration Hardware's "
        "Cloud Modular Sofa — slipcovered look, generous depth, low-profile, "
        "soft architectural mass — front view, upholstered in the fabric "
        "shown above."
    ),
    scene=(
        "Scene — a contemporary architectural living space (John Pawson "
        "minimalism, but lived in):\n"
        "- Architecture: limewashed plaster walls in soft cream, polished "
        "concrete floor with subtle warmth, a structural concrete column "
        "to one side, a long horizontal slot window high on the back wall.\n"
        "- In the corner behind the sofa: a Noguchi paper lantern (Akari) "
        "on the floor, LIT, glowing warmly.\n"
        "- To one side of the sofa: a single vintage Pierre Jeanneret "
        "cane-back chair (natural cane and teak — NOT upholstered in the "
        "swatch fabric) as a sculptural accent.\n"
        "- On the floor near the sofa: a large sculptural ceramic urn in "
        "matte unglazed clay.\n"
        "- A natural-fibre rug — wool or hand-knotted — anchors the seating.\n"
        "- Overcast diffuse daylight + the warm pool of the Noguchi lantern."
    ),
    photographer="Joshua McHugh",
    lens="35mm",
    camera_height="low, at sofa-seat level",
    camera_extras=(
        "Composition layered with the Pierre Jeanneret chair in the "
        "foreground (defocused), sofa centred, Noguchi lantern glow as "
        "the warm background anchor."
    ),
)

PROMPTS["sofa_two_seater"] = _assemble(
    subject=(
        "a modern two-cushion two-seater sofa in the style of Restoration "
        "Hardware's Belgian Track Arm 2-Cushion Sofa — clean square track "
        "arms, two-cushion seat, restrained slipcover silhouette — front-"
        "three-quarter view, upholstered in the fabric shown above."
    ),
    scene=(
        "Scene — an intimate parlor in a high-end pre-war apartment "
        "(François Halard interior story):\n"
        "- Architecture: original parquet de Versailles oak floor, plaster "
        "walls with subtle patina, a marble fireplace partially visible "
        "off-frame to the right.\n"
        "- Above the sofa: a single large vintage landscape painting in a "
        "worn gilt frame.\n"
        "- Beside the sofa: a small vintage Italian travertine side table "
        "with a single small Etruscan-style ceramic vessel and a vintage "
        "table lamp in patinated brass (LIT, warm pool).\n"
        "- In the far corner: a potted olive tree in an aged terracotta "
        "planter.\n"
        "- A small vintage kilim or Berber rug under the sofa.\n"
        "- Late morning side light from a tall French window outside the "
        "left of frame; brass picture light over the painting also LIT."
    ),
    photographer="François Halard",
    lens="50mm prime",
    camera_height="at sofa-seat level",
    camera_extras=(
        "Composition: sofa slightly off-centre to the right, the painting "
        "above anchoring the vertical, the lit lamp and olive tree creating "
        "warm depth."
    ),
)

PROMPTS["sectional"] = _assemble(
    subject=(
        "a modular L-shape sectional sofa in the style of Minotti's Freeman "
        "Seating System — low and deep, generous in scale, clean lines, "
        "slim profile legs — upholstered in the fabric shown above."
    ),
    scene=(
        "Scene — a grand living room with serious architectural integration "
        "(William Waldron / AD spread):\n"
        "- Architecture: tall ceiling with exposed original timber beams, "
        "wide-plank oak floor, raw plaster walls in warm bone tone, a large "
        "doorway visible to the next room.\n"
        "- In front of the sectional: a substantial vintage travertine "
        "coffee table or a burl wood slab — single dramatic piece.\n"
        "- On the wall above the sectional: a major contemporary art piece "
        "— a large Cy Twombly-esque scrawl in muted earth tones on raw "
        "linen ground.\n"
        "- In the far corner: a vintage 1950s Italian floor lamp in "
        "patinated brass, LIT.\n"
        "- A large hand-knotted wool rug anchors the L-shape, slightly worn.\n"
        "- Golden hour light streaming through tall windows outside the "
        "right of frame + the warm practical floor lamp glow."
    ),
    photographer="William Waldron",
    lens="24mm tilt-shift",
    camera_height="slightly elevated to capture the full L-shape, horizon at eye level",
    camera_extras=(
        "Verticals kept straight by the tilt-shift; composition layered "
        "with the coffee table in the soft foreground, sectional in plane "
        "of focus, the doorway and architecture in the defocused background."
    ),
)

PROMPTS["lounge_imola"] = _assemble(
    subject=(
        "a modernist lounge chair in the style of BoConcept's Imola — "
        "curved organic silhouette, low-slung, contemporary Scandinavian "
        "with visible natural wood frame elements — three-quarter view, "
        "upholstered in the fabric shown above."
    ),
    scene=(
        "Scene — a reading nook in a designer's home / atelier "
        "(Simon Watson / Vogue Living mood):\n"
        "- Beside the chair: a Saarinen tulip side table in white marble, "
        "with a stack of two or three art monographs and a single small "
        "piece of period ceramic on top.\n"
        "- Behind the chair: a single large unframed landscape painting "
        "in muted earth tones — abstract, atmospheric.\n"
        "- To the side: a vintage 1960s Italian floor lamp in patinated "
        "brass, LIT, casting a warm pool over the chair's arm.\n"
        "- Underfoot: a small vintage Moroccan or Persian rug, worn with "
        "character.\n"
        "- Architecture: warm taupe limewash wall, wide-plank oak floor, "
        "a tall window outside the right of frame with a partial view of "
        "a garden in soft focus.\n"
        "- Late morning warm side light + the lit lamp."
    ),
    photographer="Simon Watson",
    lens="50mm prime",
    camera_height="at chair-seat level",
    camera_extras=(
        "Composition layered with the lamp glow in the foreground, the "
        "chair in plane of focus, the painting and window light defocused "
        "in the background."
    ),
)

# ── DRAPERY ─────────────────────────────────────────────────────────────────

PROMPTS["curtain_wave"] = _assemble(
    subject=(
        "floor-length wave-fold (S-fold / ripple-fold) curtain panels made "
        "in the fabric shown above — clean modern S-shaped folds running "
        "uniformly along a recessed ceiling-mounted track. The rhythmic "
        "S-curve is the defining feature."
    ),
    scene=(
        "Scene — a modernist living room with serious glass "
        "(Pieter Estersohn / AD mood):\n"
        "- Floor-to-ceiling windows behind the wave-fold curtain.\n"
        "- Beyond the curtain (defocused): a hint of garden or outdoor "
        "terrace — green leaves, soft light.\n"
        "- In the room: a single vintage modernist armchair (Pierre "
        "Jeanneret or similar — NOT upholstered in the swatch fabric) as "
        "a sculptural accent in the foreground, slightly defocused.\n"
        "- A small sculptural ceramic side table beside the chair.\n"
        "- Wide-plank oak floor or polished concrete with patina.\n"
        "- Bright but diffused daylight, late morning."
    ),
    photographer="Pieter Estersohn",
    lens="24mm",
    camera_height="at eye level, looking across the room",
    camera_extras=(
        "The rhythm of the S-folds reads clearly across the width of "
        "the panel; vintage chair in the foreground anchors depth."
    ),
)

PROMPTS["drape_dramatic"] = _assemble(
    subject=(
        "a length of the fabric shown above, draped dramatically — NOT as "
        "a finished curtain, NO rod, NO installation hardware — falling "
        "from full ceiling height and allowed to pool and puddle naturally "
        "at the floor. Sculptural, editorial, museum-like."
    ),
    scene=(
        "Scene — a T Magazine editorial spread, shot like a museum "
        "installation:\n"
        "- Against a tall raw plaster wall in warm bone tone, on a "
        "polished terrazzo or aged stone floor.\n"
        "- Architectural detail to one side: a single shallow niche cut "
        "into the wall, with a small period bronze sculpture inside; OR "
        "a stone bench at the base of the drape.\n"
        "- A glimpse of a doorway visible to the side of frame leading "
        "to another room (defocused, suggesting depth).\n"
        "- Strong single-source directional side light creating deep, "
        "graphic shadows in the folds of the fabric."
    ),
    photographer="Stephen Kent Johnson for T Magazine",
    lens="35mm",
    camera_height="three-quarter angle, mid-height — fabric full height in frame",
    camera_extras=(
        "Composition asymmetric — drape weighted to one side, the niche "
        "or bench providing visual anchor and scale."
    ),
)

PROMPTS["drape_detail"] = _assemble(
    subject=(
        "a close-up detail of the fabric shown above caught in drape — a "
        "single fold or cascade at the moment it falls under its own "
        "weight. The fabric's hand, drape, weave, and surface texture "
        "are the clear focus."
    ),
    scene=(
        "Scene — editorial textile photography (AD detail shot):\n"
        "- Behind the fabric fold: soft architectural depth — a defocused "
        "tall window light and a hint of plaster wall in shadow.\n"
        "- Raking directional side light skims across the surface, "
        "revealing texture, pile, and weave at near-macro fidelity.\n"
        "- The fold has natural weight and gravity, the fabric pulling "
        "down with realistic drape physics."
    ),
    photographer="Stephen Kent Johnson",
    lens="85mm macro",
    camera_height="close to the fold itself, very shallow depth of field",
    camera_extras=(
        "Fabric fills 80% of the frame; background dissolves into soft "
        "tonal architectural shadow."
    ),
)


def get(application_key: str) -> str:
    """Return the assembled prompt for a given application key."""
    if application_key not in PROMPTS:
        raise KeyError(
            f"Unknown application key {application_key!r}. "
            f"Known: {sorted(PROMPTS)}"
        )
    return PROMPTS[application_key]


def all_keys() -> list[str]:
    return list(PROMPTS.keys())
