"""Build visual QA contact sheets for the production sticker routes."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
ASSET_ROOT = ROOT / "web" / "assets"
OUT_ROOT = ROOT / "web" / "previews"
VEGETABLES = ("cabbage", "tomato", "pepper", "carrot", "mushroom", "corn", "potato", "purple-cabbage")
MEATS = ("chicken-leg", "bacon", "meatballs", "thick-steak", "ribs", "pork-chop", "roast-roll", "bone-steak", "pork-belly", "roasted-ribs", "meat-feast")


def overview(folder, names, title, filename):
    tile_w, tile_h = 168, 192
    columns = 4
    rows = (len(names) + columns - 1) // columns
    canvas = Image.new("RGBA", (columns * tile_w, rows * tile_h + 54), (255, 248, 226, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((18, 15), title, fill=(91, 59, 42, 255), stroke_width=0)
    for index, name in enumerate(names):
        x = (index % columns) * tile_w
        y = 54 + (index // columns) * tile_h
        draw.rounded_rectangle((x + 8, y + 8, x + tile_w - 8, y + tile_h - 12), radius=18, fill=(255, 239, 199, 255), outline=(232, 198, 143, 255), width=2)
        image = Image.open(folder / f"{name}.png").convert("RGBA")
        image.thumbnail((tile_w - 22, tile_h - 42), Image.Resampling.LANCZOS)
        canvas.alpha_composite(image, (x + (tile_w - image.width) // 2, y + 13))
        draw.text((x + 10, y + tile_h - 31), f"{index + 1:02d}  {name}", fill=(109, 72, 52, 255))
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT_ROOT / filename, optimize=True)
    print(OUT_ROOT / filename)


def board_overview(folder, names, title, filename):
    """Render the same assets near the board's 56 px cell size."""
    tile_w, tile_h = 82, 82
    columns = 6
    rows = (len(names) + columns - 1) // columns
    canvas = Image.new("RGBA", (columns * tile_w, rows * tile_h + 42), (255, 248, 226, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 12), title, fill=(91, 59, 42, 255))
    for index, name in enumerate(names):
        x = (index % columns) * tile_w
        y = 42 + (index // columns) * tile_h
        draw.rounded_rectangle((x + 6, y + 5, x + tile_w - 6, y + tile_h - 5), radius=11, fill=(255, 239, 199, 255), outline=(232, 198, 143, 255), width=1)
        image = Image.open(folder / f"{name}.png").convert("RGBA")
        image.thumbnail((58, 58), Image.Resampling.LANCZOS)
        canvas.alpha_composite(image, (x + (tile_w - image.width) // 2, y + 8))
        draw.text((x + 8, y + tile_h - 19), f"{index + 1:02d}", fill=(109, 72, 52, 255))
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(OUT_ROOT / filename, optimize=True)
    print(OUT_ROOT / filename)


def main():
    overview(ASSET_ROOT / "vegetables-sticker", VEGETABLES, "Vegetable stickers · 8-level route", "vegetables-sticker-overview.png")
    overview(ASSET_ROOT / "meats-sticker", MEATS, "Meat stickers · 11-level route", "meats-sticker-overview.png")
    board_overview(ASSET_ROOT / "vegetables-sticker", VEGETABLES, "Vegetables · board scale", "vegetables-sticker-board-overview.png")
    board_overview(ASSET_ROOT / "meats-sticker", MEATS, "Meats · board scale", "meats-sticker-board-overview.png")


if __name__ == "__main__":
    main()
