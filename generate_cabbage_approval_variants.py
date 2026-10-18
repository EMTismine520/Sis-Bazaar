"""Render three approval variants for the cabbage route stickers.

These files intentionally live under web/previews and do not replace the
production assets until a variant is approved.
"""

from importlib.util import module_from_spec, spec_from_file_location
from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "web" / "previews" / "vegetable-styles" / "generate_assets.py"
OUT = ROOT / "web" / "previews" / "cabbage-approval"
KINDS = ("cabbage", "purple-cabbage")
VARIANTS = {
    "v1": {"scale": 0.82, "lobes": 7, "depth": 0.07, "phase": -0.2, "seed": 41},
    "v2": {"scale": 0.86, "lobes": 8, "depth": 0.055, "phase": 0.18, "seed": 67},
    "v3": {"scale": 0.90, "lobes": 6, "depth": 0.085, "phase": 0.42, "seed": 93},
}


def load_source():
    spec = spec_from_file_location("vegetable_sticker_source", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load source painter: {SOURCE}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def lobed_points(cx, cy, rx, ry, lobes, depth, phase):
    points = []
    for index in range(96):
        angle = 2 * pi * index / 96
        radius = 1 + depth * sin(lobes * angle + phase)
        points.append((cx + rx * radius * cos(angle), cy + ry * radius * sin(angle)))
    return points


def shrink_to_canvas(image, factor):
    inner_size = round(256 * factor)
    inner = image.resize((inner_size, inner_size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    canvas.alpha_composite(inner, ((256 - inner_size) // 2, (256 - inner_size) // 2))
    return canvas


def draw_variant(painter, kind, settings, source):
    palette = painter.palette
    outline = painter.outline
    silhouette = lobed_points(54, 57, 36, 34, settings["lobes"], settings["depth"], settings["phase"])
    painter.polygon(silhouette, palette["leaf"] if kind == "cabbage" else palette["purple"], outline, 2)

    if kind == "cabbage":
        painter.ellipse((23, 36, 55, 78), palette["leaf-light"], None, 1)
        painter.ellipse((34, 24, 68, 67), (112, 188, 92, 235), None, 1)
        painter.ellipse((54, 29, 87, 69), (126, 195, 96, 230), None, 1)
        painter.ellipse((36, 50, 73, 89), (120, 190, 90, 235), None, 1)
        painter.arc((20, 31, 67, 82), 36, 154, (61, 141, 70, 205), 2)
        painter.arc((34, 21, 84, 80), 210, 339, (196, 226, 143, 205), 2)
        painter.arc((43, 40, 88, 91), 195, 320, (63, 145, 71, 190), 2)
        painter.line([(47, 79), (51, 62), (62, 45)], (214, 237, 155, 215), 2)
        painter.speckles(painter.mask_polygon(silhouette), (48, 119, 57), settings["seed"], 78, (0.35, 1.15), 28)
    else:
        painter.ellipse((23, 35, 54, 76), palette["purple-light"], None, 1)
        painter.ellipse((35, 24, 68, 67), (166, 96, 173, 235), None, 1)
        painter.ellipse((52, 31, 86, 71), (130, 66, 151, 235), None, 1)
        painter.ellipse((34, 50, 74, 88), (112, 52, 137, 235), None, 1)
        painter.arc((20, 31, 69, 82), 34, 155, (102, 48, 128, 200), 2)
        painter.arc((34, 22, 84, 77), 206, 337, (213, 148, 205, 210), 2)
        painter.arc((40, 42, 90, 92), 195, 325, (86, 40, 115, 205), 2)
        painter.line([(48, 76), (48, 59), (60, 42)], (222, 164, 214, 225), 2)
        painter.line([(48, 59), (33, 47)], (207, 143, 201, 205), 2)
        painter.speckles(painter.mask_polygon(silhouette), (79, 38, 107), settings["seed"], 74, (0.35, 1.1), 28)


def make_overview(source):
    tile_w, tile_h = 184, 190
    canvas = Image.new("RGBA", (3 * tile_w, 2 * tile_h + 62), (255, 248, 226, 255))
    draw = ImageDraw.Draw(canvas)
    # Use a Windows CJK font when available so the approval sheet remains
    # readable on machines where Pillow's default bitmap font lacks Chinese
    # glyphs.  Keep a deterministic fallback for other environments.
    font_candidates = (
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/msyh.ttf"),
        Path("C:/Windows/Fonts/simhei.ttf"),
    )
    font_path = next((candidate for candidate in font_candidates if candidate.exists()), None)
    title_font = ImageFont.truetype(str(font_path), 16) if font_path else ImageFont.load_default()
    label_font = ImageFont.truetype(str(font_path), 12) if font_path else ImageFont.load_default()
    draw.text((18, 16), "包菜 / 紫甘蓝审批候选 · 无白色高光 · 缩小版", fill=(91, 59, 42, 255), font=title_font)
    for index, variant in enumerate(VARIANTS):
        for row, kind in enumerate(KINDS):
            x = index * tile_w
            y = 62 + row * tile_h
            draw.rounded_rectangle((x + 10, y + 10, x + tile_w - 10, y + tile_h - 10), radius=18, fill=(255, 239, 199, 255), outline=(232, 198, 143, 255), width=2)
            image = Image.open(OUT / f"{kind}-{variant}.png").convert("RGBA")
            image.thumbnail((142, 142), Image.Resampling.LANCZOS)
            canvas.alpha_composite(image, (x + (tile_w - image.width) // 2, y + 16))
            label = f"{variant.upper()} · {'包菜' if kind == 'cabbage' else '紫甘蓝'}"
            draw.text((x + 16, y + tile_h - 31), label, fill=(109, 72, 52, 255), font=label_font)
    canvas.convert("RGB").save(OUT / "approval-overview.png", optimize=True)


def main():
    source = load_source()
    OUT.mkdir(parents=True, exist_ok=True)
    for variant, settings in VARIANTS.items():
        for kind in KINDS:
            painter = source.Painter("sticker")
            draw_variant(painter, kind, settings, source)
            image = shrink_to_canvas(painter.finish(), settings["scale"])
            image.save(OUT / f"{kind}-{variant}.png", optimize=True)
    make_overview(source)
    print(OUT / "approval-overview.png")


if __name__ == "__main__":
    main()
