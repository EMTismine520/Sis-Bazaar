from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter


OUT = Path(__file__).resolve().parent / "web" / "assets"
FOOD_DIR = OUT / "foods"
MEAT_DIR = OUT / "meats"
SIZE = 256
SCALE = 3

COLORS = {
    "cabbage": (91, 177, 103),
    "carrot": (239, 135, 49),
    "tomato": (220, 75, 64),
    "pepper": (239, 169, 48),
    "corn": (244, 195, 48),
}

MEAT_COLORS = {
    "chicken": (244, 187, 121),
    "beef": (176, 73, 58),
    "pork": (231, 133, 133),
    "shrimp": (239, 126, 91),
}

FUSION_ART = [
    ("fusion-lv4-cabbage-chicken.png", 4, (76, 156, 102), (174, 224, 153), (238, 151, 78), (255, 221, 111), (91, 177, 103), (244, 187, 121)),
    ("fusion-lv4-carrot-beef.png", 4, (185, 93, 61), (245, 169, 107), (132, 79, 58), (255, 214, 102), (239, 135, 49), (176, 73, 58)),
    ("fusion-lv4-tomato-shrimp.png", 4, (206, 82, 67), (247, 161, 132), (238, 117, 75), (255, 222, 112), (220, 75, 64), (239, 126, 91)),
    ("fusion-lv4-pepper-pork.png", 4, (214, 130, 56), (247, 205, 121), (179, 82, 99), (255, 225, 123), (239, 169, 48), (231, 133, 133)),
    ("fusion-lv4-corn-chicken.png", 4, (205, 153, 48), (248, 218, 117), (225, 119, 71), (255, 231, 128), (244, 195, 48), (244, 187, 121)),
    ("fusion-lv5-jade-golden.png", 5, (54, 139, 116), (157, 222, 174), (39, 112, 133), (255, 230, 113), (91, 177, 103), (176, 73, 58)),
    ("fusion-lv5-sweet-sea.png", 5, (199, 92, 73), (249, 174, 139), (238, 117, 75), (255, 221, 103), (239, 135, 49), (239, 126, 91)),
    ("fusion-lv5-rainbow-sea.png", 5, (153, 92, 166), (219, 175, 226), (190, 77, 143), (255, 223, 111), (220, 75, 64), (231, 133, 133)),
    ("fusion-lv5-harvest-tower.png", 5, (207, 133, 50), (250, 207, 117), (238, 110, 55), (255, 231, 126), (244, 195, 48), (231, 133, 133)),
    ("fusion-lv5-jade-corn.png", 5, (83, 151, 99), (182, 228, 155), (224, 137, 49), (255, 224, 109), (91, 177, 103), (244, 195, 48)),
]


def canvas():
    return Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))


def xy(value):
    return int(value * SCALE)


def draw_shape(image, kind, level):
    draw = ImageDraw.Draw(image)
    c = COLORS[kind]
    dark = tuple(max(0, value - 45) for value in c)
    light = tuple(min(255, value + 45) for value in c)
    ink = (76, 57, 46, 255)

    if level == 1:
        if kind == "cabbage":
            draw.ellipse((xy(44), xy(77), xy(212), xy(206)), fill=dark + (255,), outline=ink, width=xy(4))
            for box, fill in [((65, 74, 153, 191), light), ((88, 60, 186, 178), c), ((43, 104, 116, 216), c), ((117, 97, 215, 216), light)]:
                draw.ellipse(tuple(xy(v) for v in box), fill=fill + (255,), outline=ink, width=xy(3))
            draw.arc((xy(72), xy(108), xy(149), xy(178)), 80, 255, fill=dark + (255,), width=xy(4))
        elif kind == "carrot":
            draw.polygon([(xy(80), xy(58)), (xy(183), xy(69)), (xy(130), xy(216)), (xy(104), xy(216))], fill=c + (255,), outline=ink)
            draw.line((xy(88), xy(65), xy(71), xy(35)), fill=(70, 150, 75, 255), width=xy(10))
            draw.line((xy(113), xy(64), xy(111), xy(28)), fill=(80, 164, 78, 255), width=xy(10))
            draw.line((xy(140), xy(66), xy(157), xy(34)), fill=(62, 139, 68, 255), width=xy(10))
            for y in (105, 137, 169):
                draw.line((xy(111), xy(y), xy(148), xy(y - 7)), fill=light + (255,), width=xy(4))
        elif kind == "tomato":
            draw.ellipse((xy(42), xy(49), xy(214), xy(214)), fill=c + (255,), outline=ink, width=xy(4))
            draw.polygon([(xy(126), xy(69)), (xy(143), xy(39)), (xy(151), xy(75)), (xy(183), xy(59)), (xy(163), xy(91)), (xy(127), xy(79))], fill=(72, 145, 75, 255), outline=ink)
            draw.ellipse((xy(82), xy(83), xy(119), xy(120)), fill=(255, 137, 105, 180))
        elif kind == "pepper":
            draw.polygon([(xy(77), xy(58)), (xy(121), xy(69)), (xy(145), xy(57)), (xy(185), xy(78)), (xy(205), xy(168)), (xy(174), xy(207)), (xy(128), xy(218)), (xy(78), xy(190)), (xy(58), xy(112))], fill=c + (255,), outline=ink)
            draw.line((xy(127), xy(59), xy(128), xy(183)), fill=light + (255,), width=xy(5))
            draw.line((xy(82), xy(84), xy(104), xy(176)), fill=light + (255,), width=xy(5))
            draw.ellipse((xy(119), xy(28), xy(143), xy(69)), fill=(73, 145, 76, 255), outline=ink, width=xy(3))
        elif kind == "corn":
            draw.ellipse((xy(73), xy(45), xy(183), xy(220)), fill=c + (255,), outline=ink, width=xy(4))
            for row in range(5):
                for col in range(3):
                    x = 91 + col * 27 + (row % 2) * 8
                    y = 77 + row * 27
                    draw.ellipse((xy(x), xy(y), xy(x + 22), xy(y + 22)), fill=light + (255,), outline=dark, width=xy(2))
            draw.polygon([(xy(80), xy(126)), (xy(34), xy(91)), (xy(54), xy(180)), (xy(100), xy(212))], fill=(88, 168, 83, 230), outline=ink)
        return

    # Dish levels use a plate or bowl with a clear ingredient signature.
    draw.ellipse((xy(33), xy(153), xy(223), xy(218)), fill=(81, 58, 47, 45))
    if level in (2, 4):
        draw.ellipse((xy(38), xy(75), xy(218), xy(194)), fill=(250, 237, 205, 255), outline=ink, width=xy(5))
        draw.ellipse((xy(57), xy(91), xy(199), xy(178)), fill=light + (255,), outline=(126, 91, 59, 255), width=xy(3))
    else:
        draw.rounded_rectangle((xy(47), xy(74), xy(209), xy(203)), radius=xy(34), fill=(244, 213, 158, 255), outline=ink, width=xy(5))
        draw.ellipse((xy(57), xy(85), xy(199), xy(154)), fill=light + (255,), outline=(126, 91, 59, 255), width=xy(3))

    if kind == "cabbage":
        for x, y in [(84, 119), (112, 101), (141, 126), (164, 108), (124, 145)]:
            draw.ellipse((xy(x - 22), xy(y - 18), xy(x + 22), xy(y + 18)), fill=(89, 181, 106, 255), outline=dark, width=xy(3))
    elif kind == "carrot":
        for x, y, angle in [(86, 122, 0), (123, 106, 0), (157, 123, 0), (119, 141, 0)]:
            draw.polygon([(xy(x - 12), xy(y - 27)), (xy(x + 14), xy(y - 24)), (xy(x + 4), xy(y + 28)), (xy(x - 8), xy(y + 28))], fill=c + (255,), outline=dark)
    elif kind == "tomato":
        for x, y in [(89, 119), (124, 103), (159, 122), (126, 139)]:
            draw.ellipse((xy(x - 21), xy(y - 21), xy(x + 21), xy(y + 21)), fill=c + (255,), outline=dark, width=xy(3))
    elif kind == "pepper":
        for x, y in [(87, 115), (122, 102), (157, 119), (120, 140)]:
            draw.rounded_rectangle((xy(x - 18), xy(y - 25), xy(x + 18), xy(y + 24)), radius=xy(13), fill=c + (255,), outline=dark, width=xy(3))
    elif kind == "corn":
        for x, y in [(89, 118), (119, 104), (150, 119), (119, 139)]:
            for row in range(2):
                for col in range(2):
                    draw.ellipse((xy(x - 17 + col * 18), xy(y - 15 + row * 18), xy(x + 1 + col * 18), xy(y + 3 + row * 18)), fill=light + (255,), outline=dark, width=xy(1))
    if level >= 3:
        draw.ellipse((xy(168), xy(63), xy(193), xy(88)), fill=(255, 218, 81, 255), outline=ink, width=xy(3))
    if level >= 4:
        draw.arc((xy(58), xy(54), xy(203), xy(226)), 190, 350, fill=(245, 130, 60, 255), width=xy(5))
    if level >= 5:
        for x in (67, 99, 161, 193):
            draw.ellipse((xy(x), xy(46), xy(x + 14), xy(62)), fill=(86, 170, 84, 255), outline=ink, width=xy(2))


def save_food(kind, level):
    image = canvas()
    draw_shape(image, kind, level)
    image = image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    image.save(FOOD_DIR / f"{kind}-lv{level}.png", optimize=True)


def draw_meat_shape(image, kind, level):
    draw = ImageDraw.Draw(image)
    c = MEAT_COLORS[kind]
    dark = tuple(max(0, value - 45) for value in c)
    light = tuple(min(255, value + 40) for value in c)
    ink = (76, 57, 46, 255)
    draw.ellipse((xy(35), xy(170), xy(221), xy(224)), fill=(81, 58, 47, 45))

    if level == 1:
        if kind == "chicken":
            draw.rounded_rectangle((xy(68), xy(74), xy(188), xy(193)), radius=xy(33), fill=c + (255,), outline=ink, width=xy(5))
            draw.ellipse((xy(48), xy(124), xy(96), xy(175)), fill=light + (255,), outline=ink, width=xy(4))
            draw.ellipse((xy(160), xy(47), xy(205), xy(91)), fill=(247, 198, 135, 255), outline=ink, width=xy(4))
        elif kind == "beef":
            draw.polygon([(xy(57), xy(80)), (xy(178), xy(54)), (xy(207), xy(126)), (xy(177), xy(194)), (xy(75), xy(203)), (xy(47), xy(142))], fill=c + (255,), outline=ink)
            draw.ellipse((xy(112), xy(104), xy(145), xy(141)), fill=light + (255,), outline=dark, width=xy(3))
        elif kind == "pork":
            draw.ellipse((xy(48), xy(67), xy(210), xy(199)), fill=c + (255,), outline=ink, width=xy(5))
            draw.ellipse((xy(99), xy(104), xy(160), xy(165)), fill=(255, 212, 192, 255), outline=dark, width=xy(4))
            draw.ellipse((xy(73), xy(36), xy(111), xy(75)), fill=(237, 158, 158, 255), outline=ink, width=xy(3))
        elif kind == "shrimp":
            draw.arc((xy(48), xy(59), xy(211), xy(210)), 15, 335, fill=c + (255,), width=xy(28))
            draw.arc((xy(48), xy(59), xy(211), xy(210)), 15, 335, fill=ink, width=xy(4))
            draw.ellipse((xy(156), xy(66), xy(188), xy(97)), fill=(255, 218, 170, 255), outline=ink, width=xy(3))
            for x, y in [(84, 94), (105, 76), (127, 68), (149, 72)]:
                draw.line((xy(x), xy(y), xy(x + 9), xy(y + 23)), fill=dark + (255,), width=xy(3))
        return

    draw.ellipse((xy(34), xy(166), xy(222), xy(220)), fill=(81, 58, 47, 45))
    draw.ellipse((xy(38), xy(67), xy(218), xy(190)), fill=(250, 237, 205, 255), outline=ink, width=xy(5))
    draw.ellipse((xy(57), xy(84), xy(199), xy(171)), fill=(255, 224, 166, 255), outline=(126, 91, 59, 255), width=xy(3))

    if kind == "chicken":
        for x, y in [(87, 116), (123, 101), (160, 119), (122, 143)]:
            draw.rounded_rectangle((xy(x - 20), xy(y - 20), xy(x + 20), xy(y + 20)), radius=xy(10), fill=c + (255,), outline=dark, width=xy(3))
    elif kind == "beef":
        for x, y in [(87, 116), (123, 101), (160, 119), (122, 143)]:
            draw.rounded_rectangle((xy(x - 22), xy(y - 14), xy(x + 22), xy(y + 14)), radius=xy(8), fill=c + (255,), outline=dark, width=xy(3))
            draw.ellipse((xy(x - 7), xy(y - 7), xy(x + 7), xy(y + 7)), fill=light + (255,))
    elif kind == "pork":
        for x, y in [(88, 116), (124, 101), (160, 119), (123, 143)]:
            draw.ellipse((xy(x - 21), xy(y - 20), xy(x + 21), xy(y + 20)), fill=c + (255,), outline=dark, width=xy(3))
            draw.ellipse((xy(x - 7), xy(y - 7), xy(x + 7), xy(y + 7)), fill=(255, 212, 192, 255), outline=dark, width=xy(2))
    elif kind == "shrimp":
        for x, y in [(89, 121), (126, 104), (160, 120), (124, 143)]:
            draw.arc((xy(x - 25), xy(y - 25), xy(x + 25), xy(y + 25)), 15, 330, fill=c + (255,), width=xy(13))
            draw.arc((xy(x - 25), xy(y - 25), xy(x + 25), xy(y + 25)), 15, 330, fill=dark + (255,), width=xy(3))

    if level >= 3:
        draw.ellipse((xy(168), xy(53), xy(193), xy(78)), fill=(255, 218, 81, 255), outline=ink, width=xy(3))
        draw.arc((xy(58), xy(47), xy(203), xy(222)), 190, 350, fill=(245, 130, 60, 255), width=xy(5))


def save_meat(kind, level):
    image = canvas()
    draw_meat_shape(image, kind, level)
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(MEAT_DIR / f"{kind}-lv{level}.png", optimize=True)


def save_meat_bag():
    image = canvas()
    draw = ImageDraw.Draw(image)
    ink = (76, 57, 46, 255)
    draw.ellipse((xy(39), xy(176), xy(216), xy(224)), fill=(81, 58, 47, 45))
    draw.rounded_rectangle((xy(45), xy(54), xy(211), xy(205)), radius=xy(35), fill=(199, 104, 73, 255), outline=ink, width=xy(5))
    draw.arc((xy(76), xy(23), xy(179), xy(102)), 180, 355, fill=ink, width=xy(8))
    draw.rounded_rectangle((xy(60), xy(95), xy(197), xy(179)), radius=xy(20), fill=(244, 178, 133, 255), outline=(151, 76, 55, 255), width=xy(3))
    draw.rounded_rectangle((xy(79), xy(110), xy(121), xy(151)), radius=xy(10), fill=(244, 187, 121, 255), outline=ink, width=xy(3))
    draw.polygon([(xy(140), xy(108)), (xy(177), xy(111)), (xy(171), xy(154)), (xy(143), xy(164)), (xy(126), xy(136))], fill=(176, 73, 58, 255), outline=ink)
    draw.arc((xy(142), xy(105), xy(190), xy(165)), 20, 320, fill=(239, 126, 91, 255), width=xy(13))
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(OUT / "meat-bag-v1.png", optimize=True)


def save_fusion(filename, level, base, light, accent, badge, first, second):
    image = canvas()
    draw = ImageDraw.Draw(image)
    ink = (76, 57, 46, 255)
    draw.ellipse((xy(30), xy(169), xy(226), xy(225)), fill=(81, 58, 47, 45))
    draw.ellipse((xy(34), xy(65), xy(222), xy(199)), fill=(250, 237, 205, 255), outline=ink, width=xy(5))
    draw.ellipse((xy(53), xy(83), xy(203), xy(177)), fill=light + (255,), outline=(126, 91, 59, 255), width=xy(3))
    ingredients = [(82, 119, first), (119, 101, second), (157, 120, first), (120, 143, second)]
    for x, y, color in ingredients:
        draw.ellipse((xy(x - 23), xy(y - 19), xy(x + 23), xy(y + 19)), fill=tuple(color) + (255,), outline=ink, width=xy(3))
    if level >= 5:
        draw.arc((xy(54), xy(49), xy(204), xy(228)), 190, 350, fill=accent + (255,), width=xy(5))
        draw.ellipse((xy(169), xy(49), xy(195), xy(75)), fill=badge + (255,), outline=ink, width=xy(3))
        draw.arc((xy(42), xy(37), xy(214), xy(237)), 200, 340, fill=accent + (255,), width=xy(6))
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(OUT / "fusions" / filename, optimize=True)


def save_bag():
    image = canvas()
    draw = ImageDraw.Draw(image)
    ink = (76, 57, 46, 255)
    draw.ellipse((xy(39), xy(176), xy(216), xy(224)), fill=(81, 58, 47, 45))
    draw.rounded_rectangle((xy(45), xy(54), xy(211), xy(205)), radius=xy(35), fill=(218, 157, 67, 255), outline=ink, width=xy(5))
    draw.arc((xy(76), xy(23), xy(179), xy(102)), 180, 355, fill=ink, width=xy(8))
    draw.rounded_rectangle((xy(60), xy(95), xy(197), xy(179)), radius=xy(20), fill=(245, 203, 104, 255), outline=(151, 94, 45, 255), width=xy(3))
    draw.ellipse((xy(76), xy(113), xy(126), xy(161)), fill=(80, 169, 89, 255), outline=ink, width=xy(3))
    draw.ellipse((xy(112), xy(101), xy(161), xy(151)), fill=(220, 75, 64, 255), outline=ink, width=xy(3))
    draw.polygon([(xy(145), xy(125)), (xy(180), xy(111)), (xy(169), xy(158)), (xy(142), xy(164))], fill=(239, 169, 48, 255), outline=ink)
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(OUT / "vegetable-bag-v2.png", optimize=True)


FOOD_DIR.mkdir(parents=True, exist_ok=True)
MEAT_DIR.mkdir(parents=True, exist_ok=True)
(OUT / "fusions").mkdir(parents=True, exist_ok=True)
save_bag()
for kind in COLORS:
    for level in range(1, 4):
        save_food(kind, level)
save_meat_bag()
for kind in MEAT_COLORS:
    for level in range(1, 4):
        save_meat(kind, level)
for old_asset in (OUT / "fusions").glob("fusion-lv*.png"):
    old_asset.unlink()
for filename, level, base, light, accent, badge, first, second in FUSION_ART:
    save_fusion(filename, level, base, light, accent, badge, first, second)
