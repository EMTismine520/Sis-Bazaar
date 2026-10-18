"""Generate the transparent vegetable route stickers used by the web board.

The approved vegetable preview painter lives beside its style comparisons under
``web/previews``.  This small project-level entry point keeps the production
asset path explicit and makes the same deterministic Pillow workflow easy to
rerun alongside ``generate_meat_sticker_assets.py``.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from shutil import copy2


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "web" / "previews" / "vegetable-styles" / "generate_assets.py"
OUT = ROOT / "web" / "assets" / "vegetables-sticker"
APPROVED_CABBAGE = ROOT / "web" / "previews" / "cabbage-approval"
APPROVED_VARIANTS = {
    "cabbage": APPROVED_CABBAGE / "cabbage-v3.png",
    "purple-cabbage": APPROVED_CABBAGE / "purple-cabbage-v3.png",
}


def load_source():
    spec = spec_from_file_location("vegetable_sticker_preview_generator", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load vegetable painter: {SOURCE}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    module = load_source()
    # Generate all comparison styles as before, then publish the selected
    # semi-realistic sticker style to the path consumed by web/index.html.
    module.main()
    source_dir = SOURCE.parent / "assets" / "sticker"
    OUT.mkdir(parents=True, exist_ok=True)
    for kind in module.KINDS:
        # The cabbage route has three approval variants.  V3 is the approved
        # choice, so keep it as the reproducible production source whenever
        # this generator is run again.
        source = APPROVED_VARIANTS.get(kind, source_dir / f"{kind}.png")
        target = OUT / f"{kind}.png"
        copy2(source, target)
        print(target)


if __name__ == "__main__":
    main()
