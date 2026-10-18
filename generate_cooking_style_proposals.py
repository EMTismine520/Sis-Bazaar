"""Render approval boards for the cooking-pot art direction.

This generator only writes into web/previews/cooking-styles. It deliberately
does not touch production cooking assets or the game's recipe definitions.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "web" / "previews" / "cooking-styles"
VEGETABLES = ROOT / "web" / "assets" / "vegetables-sticker"
GRILL = ROOT / "web" / "previews" / "meat-styles" / "assets" / "grill"
OUT.mkdir(parents=True, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/msyh.ttc"
INK = (67, 48, 38, 255)


def font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


INGREDIENTS = {
    "cabbage": ("包菜", "🥬"),
    "carrot": ("胡萝卜", "🥕"),
    "tomato": ("番茄", "🍅"),
    "pepper": ("彩椒", "🫑"),
    "corn": ("玉米", "🌽"),
    "chicken": ("鸡腿", "🍗"),
    "beef": ("牛肉", "🥩"),
    "pork": ("培根", "🥓"),
    "shrimp": ("虾仁", "🍤"),
}

MEAT_ASSETS = {
    "chicken": "chicken-leg.png",
    "beef": "thick-steak.png",
    "pork": "pork-belly.png",
}

RECIPES = [
    {"id": "cabbage+pork", "level": 4, "name": "炭香包菜猪肉卷", "pairs": [("cabbage", "pork")]},
    {"id": "carrot+chicken", "level": 4, "name": "胡萝卜鸡腿焗盏", "pairs": [("carrot", "chicken")]},
    {"id": "tomato+beef", "level": 4, "name": "番茄黑椒牛肉船", "pairs": [("tomato", "beef")]},
    {"id": "pepper+shrimp", "level": 4, "name": "彩椒蒜香虾仁串", "pairs": [("pepper", "shrimp")]},
    {"id": "corn+pork", "level": 4, "name": "玉米培根黄金杯", "pairs": [("corn", "pork")]},
    {"id": "cabbage+pork|carrot+chicken", "level": 5, "name": "翡翠炭香双拼", "pairs": [("cabbage", "pork"), ("carrot", "chicken")]},
    {"id": "tomato+beef|pepper+shrimp", "level": 5, "name": "红金海陆焗盘", "pairs": [("tomato", "beef"), ("pepper", "shrimp")]},
    {"id": "corn+pork|carrot+chicken", "level": 5, "name": "金玉炭火丰收盘", "pairs": [("corn", "pork"), ("carrot", "chicken")]},
    {"id": "cabbage+pork|tomato+beef|pepper+shrimp", "level": 6, "name": "三色炭火盛宴", "pairs": [("cabbage", "pork"), ("tomato", "beef"), ("pepper", "shrimp")]},
    {"id": "carrot+chicken|corn+pork|tomato+beef", "level": 6, "name": "金谷海陆铁锅", "pairs": [("carrot", "chicken"), ("corn", "pork"), ("tomato", "beef")]},
]

STYLES = {
    "a": {"title": "A  炭火餐馆", "subtitle": "暖奶油餐盘 · 焦边最清晰", "panel": (255, 250, 239, 255), "tile": (255, 228, 190, 255), "line": (194, 74, 53, 255), "accent": (187, 71, 48, 255), "muted": (126, 95, 72, 255), "text": INK, "plate": (255, 244, 209, 255), "rim": (137, 74, 48, 255), "fire": (239, 110, 47, 255), "contrast": 1.12, "saturation": 1.08},
    "b": {"title": "B  手绘料理图鉴", "subtitle": "米白纸张 · 墨线水彩感", "panel": (252, 249, 237, 255), "tile": (244, 238, 215, 255), "line": (87, 116, 96, 255), "accent": (57, 119, 83, 255), "muted": (119, 111, 92, 255), "text": (66, 75, 62, 255), "plate": (255, 249, 225, 255), "rim": (112, 126, 97, 255), "fire": (217, 126, 70, 255), "contrast": 0.96, "saturation": 0.88},
    "c": {"title": "C  夜市铁锅", "subtitle": "深铁锅体 · 橙色火光", "panel": (61, 43, 38, 255), "tile": (88, 59, 47, 255), "line": (239, 145, 55, 255), "accent": (250, 170, 68, 255), "muted": (206, 169, 128, 255), "text": (255, 237, 195, 255), "plate": (65, 62, 59, 255), "rim": (209, 103, 47, 255), "fire": (255, 142, 43, 255), "contrast": 1.18, "saturation": 1.15},
}


def fit(path: Path, size, style):
    image = Image.open(path).convert("RGBA")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    image = ImageEnhance.Contrast(image).enhance(style["contrast"])
    image = ImageEnhance.Color(image).enhance(style["saturation"])
    return image


def paste_center(canvas, image, center, max_size=None):
    if max_size:
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
    canvas.alpha_composite(image, (int(center[0] - image.width / 2), int(center[1] - image.height / 2)))


def draw_shrimp(canvas, center, scale, style):
    draw = ImageDraw.Draw(canvas)
    cx, cy = center
    w, h = int(62 * scale), int(32 * scale)
    shell, dark = (221, 89, 58, 255), (84, 49, 40, 255)
    draw.arc((cx - w, cy - h, cx + w, cy + h), 205, 350, fill=shell, width=max(3, int(9 * scale)))
    draw.arc((cx - w + 8, cy - h + 5, cx + w - 5, cy + h - 3), 205, 350, fill=dark, width=max(2, int(4 * scale)))
    for offset in (-0.38, -0.05, 0.28):
        x = int(cx + w * offset)
        draw.line((x, cy - h * 0.68, x + int(13 * scale), cy + h * 0.42), fill=style["fire"], width=max(2, int(4 * scale)))
    draw.ellipse((cx + int(w * 0.62), cy - int(h * 0.7), cx + int(w * 0.85), cy - int(h * 0.45)), fill=dark)


def dish_art(recipe, style_key, size=(190, 190)):
    style = STYLES[style_key]
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    width, height = size
    draw.ellipse((12, height - 34, width - 12, height - 8), fill=(22, 16, 12, 48))
    if style_key == "c":
        draw.ellipse((10, 52, width - 10, height - 18), fill=style["plate"], outline=style["rim"], width=5)
        draw.arc((22, 28, width - 22, height + 10), 195, 345, fill=style["fire"], width=5)
        for x in (32, width - 32):
            draw.arc((x - 12, 16, x + 12, 70), 185, 350, fill=style["fire"], width=4)
    else:
        draw.ellipse((8, 50, width - 8, height - 14), fill=style["plate"], outline=style["rim"], width=4)
        draw.ellipse((22, 66, width - 22, height - 28), fill=style["tile"], outline=style["rim"], width=2)
    positions = {1: [(width * .5, height * .55)], 2: [(width * .33, height * .58), (width * .67, height * .58)], 3: [(width * .28, height * .56), (width * .5, height * .42), (width * .72, height * .56)]}[len(recipe["pairs"])]
    for (veg, meat), (gx, gy) in zip(recipe["pairs"], positions):
        paste_center(canvas, fit(VEGETABLES / f"{veg}.png", (66, 66), style), (gx - 17, gy + 8), (66, 66))
        if meat == "shrimp":
            draw_shrimp(canvas, (gx + 17, gy - 3), 0.58 if len(recipe["pairs"]) > 1 else 0.7, style)
        else:
            paste_center(canvas, fit(GRILL / MEAT_ASSETS[meat], (77, 77), style), (gx + 19, gy - 2), (77, 77))
    if recipe["level"] >= 5:
        draw.ellipse((width - 49, 19, width - 23, 45), fill=(255, 214, 81, 255), outline=style["rim"], width=2)
    if recipe["level"] >= 6:
        draw.arc((26, 18, width - 26, height - 7), 205, 335, fill=style["fire"], width=5)
    return canvas


def ingredient_line(recipe):
    return " + ".join(f"{INGREDIENTS[v][0]}·{INGREDIENTS[m][0]}" for v, m in recipe["pairs"])


def draw_card(canvas, box, recipe, style_key, detail=False):
    style = STYLES[style_key]
    draw = ImageDraw.Draw(canvas)
    x, y, w, h = box
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18 if detail else 14, fill=style["tile"], outline=style["line"], width=3)
    draw.text((x + 16, y + 12), f"Lv.{recipe['level']}", fill=style["accent"], font=font(22 if detail else 18))
    if detail:
        paste_center(canvas, dish_art(recipe, style_key, (180, 180)), (x + 92, y + h * .53))
        tx = x + 185
        draw.text((tx, y + 55), recipe["name"], fill=style["text"], font=font(23))
        draw.multiline_text((tx, y + 96), ingredient_line(recipe), fill=style["muted"], font=font(16), spacing=4)
        draw.text((tx, y + h - 42), f"锅内 {len(recipe['pairs'])} 槽", fill=style["accent"], font=font(15))
    else:
        paste_center(canvas, dish_art(recipe, style_key, (140, 140)), (x + 82, y + h * .56))
        tx = x + 154
        draw.text((tx, y + 28), recipe["name"], fill=style["text"], font=font(19))
        draw.multiline_text((tx, y + 66), ingredient_line(recipe), fill=style["muted"], font=font(13), spacing=3)
        draw.text((tx, y + h - 32), f"{len(recipe['pairs'])} 槽料理", fill=style["accent"], font=font(13))


def draw_panel_header(canvas, box, style_key):
    style = STYLES[style_key]
    draw = ImageDraw.Draw(canvas)
    x, y, w, h = box
    draw.rounded_rectangle((x, y, x + w, y + h), radius=26, fill=style["panel"], outline=style["line"], width=4)
    draw.text((x + 28, y + 20), style["title"], fill=style["accent"], font=font(31))
    draw.text((x + 30, y + 67), style["subtitle"], fill=style["muted"], font=font(17))
    draw.text((x + w - 360, y + 28), "肉类固定：炭火版", fill=style["accent"], font=font(17))


def render_overview():
    width, height = 2360, 2460
    canvas = Image.new("RGBA", (width, height), (247, 239, 221, 255))
    draw = ImageDraw.Draw(canvas)
    draw.text((54, 30), "料理锅合成路线 · 10 道料理 × 3 套美术方向", fill=INK, font=font(42))
    draw.text((57, 87), "参考图的暖黄图鉴网格；肉类统一使用炭火版，只比较锅体、盘器和光照。", fill=(126, 101, 79, 255), font=font(20))
    panel_y = 145
    panel_h = 700
    for style_key in ("a", "b", "c"):
        panel = (38, panel_y, width - 76, panel_h)
        draw_panel_header(canvas, panel, style_key)
        x, y, w, _ = panel
        grid_x, grid_y = x + 26, y + 116
        gap_x, gap_y = 18, 15
        card_w, card_h = 548, 184
        for index, recipe in enumerate(RECIPES):
            row, col = divmod(index, 4)
            draw_card(canvas, (grid_x + col * (card_w + gap_x), grid_y + row * (card_h + gap_y), card_w, card_h), recipe, style_key)
        panel_y += panel_h + 34
    draw.text((54, height - 56), "审批项：A/B/C 主风格、锅体和盘器；确认后再制作正式透明 PNG。", fill=(126, 101, 79, 255), font=font(18))
    output = canvas.convert("RGB")
    output.save(OUT / "cooking-route-style-overview.png", quality=94)
    output.save(OUT / "cooking-route-style-proposals.png", quality=94)


def render_detail(style_key):
    style = STYLES[style_key]
    width, height = 1780, 1380
    canvas = Image.new("RGBA", (width, height), style["panel"])
    draw = ImageDraw.Draw(canvas)
    draw.text((50, 34), f"料理锅路线放大预览 · {style['title']}", fill=style["accent"], font=font(38))
    draw.text((53, 88), "肉类保持炭火版：深红熟度、炭黑焦边、交叉烤痕。", fill=style["muted"], font=font(19))
    grid_x, grid_y = 46, 145
    gap_x, gap_y = 18, 18
    card_w, card_h = 408, 320
    for index, recipe in enumerate(RECIPES):
        row, col = divmod(index, 4)
        draw_card(canvas, (grid_x + col * (card_w + gap_x), grid_y + row * (card_h + gap_y), card_w, card_h), recipe, style_key, detail=True)
    route_y = 1190
    draw.rounded_rectangle((46, route_y, width - 46, route_y + 122), radius=20, fill=style["tile"], outline=style["line"], width=3)
    draw.text((72, route_y + 18), "路线节奏", fill=style["accent"], font=font(21))
    draw.text((230, route_y + 19), "Lv.4 基础 5 道  →  Lv.5 双料理 3 道  →  Lv.6 三料理 2 道", fill=style["text"], font=font(20))
    draw.text((72, route_y + 67), "锅槽位", fill=style["accent"], font=font(18))
    draw.text((230, route_y + 69), "2 槽完成基础料理；2 槽继续合成 Lv.5；3 槽完成 Lv.6", fill=style["muted"], font=font(17))
    canvas.convert("RGB").save(OUT / f"cooking-route-detail-{style_key}.png", quality=94)


def write_manifest():
    manifest = {
        "reference": "warm yellow cookbook grid with thick outlines and soft shadows",
        "meat_style": "grill",
        "recipes": RECIPES,
        "styles": {key: {"title": value["title"], "subtitle": value["subtitle"]} for key, value in STYLES.items()},
        "outputs": ["cooking-route-style-overview.png", "cooking-route-detail-a.png", "cooking-route-detail-b.png", "cooking-route-detail-c.png"],
    }
    (OUT / "cooking-route-style-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    render_overview()
    for key in STYLES:
        render_detail(key)
    write_manifest()
