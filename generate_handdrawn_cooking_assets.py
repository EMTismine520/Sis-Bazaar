"""Create the approved B-style transparent cooking result sprites."""

from pathlib import Path

from PIL import Image

from generate_cooking_style_proposals import RECIPES, dish_art


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "web" / "assets" / "cooking"


def asset_name(recipe):
    safe_id = recipe["id"].replace("|", "--").replace("+", "-")
    return f"fusion-pot-lv{recipe['level']}-{safe_id}.png"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for recipe in RECIPES:
        image = dish_art(recipe, "b", (256, 256))
        image.save(OUT / asset_name(recipe), optimize=True)
        print(OUT / asset_name(recipe))


if __name__ == "__main__":
    main()
