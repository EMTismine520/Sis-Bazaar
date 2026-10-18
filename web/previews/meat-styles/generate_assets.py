from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "grill"
SCALE = 3
CANVAS = 256

INK = (53, 39, 34, 255)
MEAT = (183, 63, 48, 255)
MEAT_LIGHT = (224, 112, 78, 255)
MEAT_DARK = (126, 48, 39, 255)
CHAR = (84, 45, 34, 255)
FAT = (255, 222, 168, 255)
CREAM = (255, 241, 207, 255)
EMBER = (228, 126, 43, 255)
HERB = (91, 139, 72, 255)
HERB_LIGHT = (140, 177, 92, 255)

ROUTE = (
    ("chicken-leg", "鸡腿"),
    ("bacon", "培根"),
    ("meatballs", "肉丸"),
    ("thick-steak", "厚切牛排"),
    ("ribs", "排骨"),
    ("pork-chop", "猪排"),
    ("roast-roll", "烤肉卷"),
    ("bone-steak", "带骨牛排"),
    ("pork-belly", "五花肉"),
    ("roasted-ribs", "烤肋排"),
    ("meat-feast", "肉类盛宴"),
)


def p(value):
    return round(value * SCALE)


def box(values):
    return tuple(p(value) for value in values)


class Painter:
    def __init__(self):
        self.image = Image.new("RGBA", (CANVAS * SCALE, CANVAS * SCALE), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def ellipse(self, bounds, fill, outline=INK, width=4):
        self.draw.ellipse(box(bounds), fill=fill, outline=outline, width=p(width))

    def rounded(self, bounds, radius, fill, outline=INK, width=4):
        self.draw.rounded_rectangle(box(bounds), radius=p(radius), fill=fill, outline=outline, width=p(width))

    def polygon(self, points, fill, outline=INK, width=4):
        scaled = [(p(x), p(y)) for x, y in points]
        self.draw.polygon(scaled, fill=fill)
        if outline:
            self.draw.line(scaled + [scaled[0]], fill=outline, width=p(width), joint="curve")

    def line(self, points, fill=INK, width=4):
        self.draw.line([(p(x), p(y)) for x, y in points], fill=fill, width=p(width), joint="curve")

    def grill_marks(self, lines, color=CHAR, width=5):
        for start, end in lines:
            self.line([start, end], color, width)

    def plate(self, top=62, bottom=205, accent=True):
        self.ellipse((24, bottom - 35, 232, bottom + 8), (75, 45, 37, 58), None, 1)
        self.ellipse((28, top, 228, bottom), CREAM, INK, 5)
        self.ellipse((44, top + 15, 212, bottom - 18), (255, 218, 169, 255), (160, 76, 55, 255), 3)
        if accent:
            self.line([(64, top + 30), (52, top + 4)], HERB, 6)
            self.line([(75, top + 28), (84, top + 3)], HERB_LIGHT, 5)

    def garnish(self, x, y, color=HERB):
        self.line([(x, y + 24), (x - 6, y)], color, 6)
        self.line([(x + 8, y + 24), (x + 16, y + 3)], HERB_LIGHT, 5)

    def draw_item(self, kind):
        if kind == "chicken-leg":
            self.rounded((74, 57, 164, 181), 34, MEAT, INK, 5)
            self.ellipse((43, 132, 108, 191), MEAT_LIGHT, INK, 4)
            self.ellipse((139, 35, 191, 90), FAT, INK, 4)
            self.line([(160, 65), (128, 113), (104, 153)], MEAT_DARK, 6)
            self.line([(82, 76), (111, 68)], MEAT_LIGHT, 5)
        elif kind == "bacon":
            self.polygon([(51, 46), (199, 39), (211, 202), (61, 214)], MEAT_LIGHT, INK, 5)
            for x in (75, 122, 169):
                self.line([(x, 50), (x + 11, 199)], FAT, 15)
                self.line([(x, 50), (x + 11, 199)], MEAT_DARK, 3)
            self.line([(56, 92), (206, 84)], MEAT, 6)
            self.line([(60, 151), (209, 143)], MEAT_DARK, 5)
        elif kind == "meatballs":
            for bounds, color in [((30, 91, 126, 181), MEAT), ((88, 51, 188, 151), MEAT_LIGHT), ((139, 94, 225, 181), MEAT_DARK)]:
                self.ellipse(bounds, color, INK, 5)
            for x, y in ((65, 120), (123, 89), (173, 126)):
                self.ellipse((x, y, x + 14, y + 10), FAT, None, 1)
            self.garnish(55, 56)
        elif kind == "thick-steak":
            self.polygon([(38, 91), (71, 51), (187, 47), (218, 95), (204, 170), (160, 202), (67, 191), (35, 149)], MEAT, INK, 5)
            self.ellipse((95, 92, 137, 136), FAT, MEAT_DARK, 4)
            self.grill_marks([((56, 121), (97, 88)), ((98, 87), (162, 78)), ((161, 79), (193, 110))], MEAT_LIGHT, 7)
            self.grill_marks([((83, 165), (139, 142)), ((139, 142), (183, 148))], MEAT_LIGHT, 6)
            self.line([(49, 112), (69, 92)], EMBER, 4)
        elif kind == "ribs":
            for y in (65, 102, 139):
                self.rounded((39, y, 205, y + 43), 17, MEAT_LIGHT, INK, 4)
                self.line([(60, y + 10), (180, y + 28)], FAT, 8)
                self.line([(73, y + 21), (188, y + 12)], MEAT_DARK, 4)
            self.ellipse((182, 79, 220, 105), FAT, INK, 3)
            self.garnish(59, 51)
        elif kind == "pork-chop":
            self.polygon([(34, 95), (64, 56), (166, 45), (208, 85), (197, 169), (149, 205), (59, 183)], MEAT_LIGHT, INK, 5)
            self.ellipse((75, 93, 121, 137), FAT, MEAT_DARK, 4)
            self.grill_marks([((133, 89), (177, 163)), ((54, 141), (112, 164)), ((112, 164), (160, 149))], MEAT, 7)
            self.line([(54, 83), (71, 68)], EMBER, 4)
        elif kind == "roast-roll":
            self.ellipse((31, 64, 91, 193), MEAT_LIGHT, INK, 5)
            self.rounded((57, 64, 193, 193), 26, MEAT, INK, 5)
            self.ellipse((165, 64, 225, 193), MEAT_LIGHT, INK, 5)
            self.ellipse((80, 97, 173, 158), FAT, MEAT_DARK, 5)
            self.line([(88, 77), (96, 180)], MEAT_LIGHT, 6)
            self.line([(136, 77), (142, 180)], MEAT_LIGHT, 6)
            self.grill_marks([((67, 86), (69, 170)), ((184, 86), (187, 170))], CHAR, 4)
        elif kind == "bone-steak":
            self.polygon([(45, 93), (74, 52), (168, 50), (202, 92), (183, 174), (87, 196), (44, 155)], MEAT, INK, 5)
            self.ellipse((170, 102, 217, 145), FAT, INK, 4)
            self.line([(188, 122), (225, 122)], FAT, 13)
            self.ellipse((212, 101, 233, 122), FAT, INK, 3)
            self.ellipse((212, 123, 233, 144), FAT, INK, 3)
            self.ellipse((89, 91, 124, 125), FAT, MEAT_DARK, 3)
            self.grill_marks([((62, 125), (104, 90)), ((111, 87), (156, 70))], MEAT_LIGHT, 6)
        elif kind == "pork-belly":
            self.rounded((35, 54, 220, 196), 25, MEAT, INK, 5)
            for y, color in ((77, FAT), (105, MEAT_LIGHT), (133, FAT), (161, MEAT_LIGHT)):
                self.line([(51, y), (204, y + 8)], color, 17)
                self.line([(51, y), (204, y + 8)], MEAT_DARK if color == MEAT_LIGHT else (226, 159, 121, 255), 3)
            self.line([(66, 64), (183, 69)], EMBER, 4)
        elif kind == "roasted-ribs":
            self.plate()
            for x, y, width in ((55, 99, 104), (78, 126, 111), (107, 94, 100)):
                self.rounded((x, y, x + width, y + 32), 15, MEAT, INK, 4)
                self.line([(x + 16, y + 9), (x + width - 14, y + 22)], FAT, 5)
                self.line([(x + 20, y + 22), (x + width - 22, y + 10)], MEAT_DARK, 4)
            self.garnish(53, 63)
        elif kind == "meat-feast":
            self.plate(top=53, bottom=210)
            self.ellipse((48, 99, 106, 147), MEAT, INK, 4)
            self.rounded((97, 91, 172, 139), 18, MEAT_LIGHT, INK, 4)
            self.polygon([(145, 110), (178, 85), (208, 105), (193, 151), (159, 155)], EMBER, INK, 4)
            self.ellipse((104, 133, 169, 174), MEAT_DARK, INK, 4)
            self.garnish(57, 72)
            self.line([(177, 159), (197, 170)], HERB, 5)
            self.ellipse((182, 166, 199, 177), HERB_LIGHT, INK, 2)
        else:
            raise ValueError(kind)

    def finish(self):
        alpha = self.image.getchannel("A")
        shadow = Image.new("RGBA", self.image.size, (44, 31, 25, 0))
        shadow.putalpha(alpha.point(lambda value: round(value * 0.18)))
        offset = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        offset.alpha_composite(shadow, (0, p(5)))
        offset.alpha_composite(self.image)
        return offset.resize((CANVAS, CANVAS), Image.Resampling.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for kind, _name in ROUTE:
        painter = Painter()
        painter.draw_item(kind)
        painter.finish().save(OUT / f"{kind}.png", optimize=True)
    chicken_leg = OUT / "chicken-leg.png"
    if chicken_leg.exists():
        Image.open(chicken_leg).convert("RGBA").save(OUT / "sausage.png", optimize=True)


if __name__ == "__main__":
    main()
