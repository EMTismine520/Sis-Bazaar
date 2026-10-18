from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter


OUT = Path(__file__).resolve().parent / "web" / "assets" / "meats-sticker"
SIZE = 256
SCALE = 3
INK = (91, 52, 43, 226)
MEAT = (211, 86, 75, 255)
MEAT_LIGHT = (245, 160, 134, 255)
FAT = (255, 221, 188, 255)
DARK = (157, 63, 58, 255)
GOLD = (237, 157, 68, 255)
EMBER = (228, 126, 43, 255)
GREEN = (92, 167, 89, 255)

ROUTE = (
    "chicken-leg", "bacon", "meatballs", "thick-steak", "ribs",
    "pork-chop", "roast-roll", "bone-steak", "pork-belly", "roasted-ribs",
    "meat-feast",
)


def as_rgba(color):
    return tuple(color) if len(color) == 4 else tuple(color) + (255,)


def mix_color(first, second, amount):
    return tuple(round(first[index] * (1 - amount) + second[index] * amount) for index in range(4))


def polish_sticker(image):
    """Tighten the transparent frame and feather the outer alpha edge."""
    image = image.convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if not bbox:
        return image

    padding = 8
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(image.width, bbox[2] + padding)
    bottom = min(image.height, bbox[3] + padding)
    cropped = image.crop((left, top, right, bottom))
    scale = min((image.width - 2 * padding) / cropped.width, (image.height - 2 * padding) / cropped.height)
    fitted = cropped.resize((round(cropped.width * scale), round(cropped.height * scale)), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", image.size, (0, 0, 0, 0))
    canvas.alpha_composite(fitted, ((image.width - fitted.width) // 2, (image.height - fitted.height) // 2))
    alpha = canvas.getchannel("A")
    softened = alpha.filter(ImageFilter.GaussianBlur(0.65))
    canvas.putalpha(Image.blend(alpha, softened, 0.55))
    return canvas


def p(v):
    return int(v * SCALE)


def box(values):
    return tuple(p(v) for v in values)


class Painter:
    def __init__(self):
        self.image = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def _paint_gradient(self, shape, fill, outline, width):
        rgba = as_rgba(fill)
        if rgba[3] < 220:
            shape(self.draw, fill, outline, width)
            return
        mask = Image.new("L", self.image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        shape(mask_draw, 255, None, 0)
        bounds = mask.getbbox()
        if not bounds:
            return
        top = mix_color(rgba, (255, 246, 219, 255), 0.24)
        bottom = mix_color(rgba, (55, 28, 24, 255), 0.22)
        gradient = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient)
        for y in range(bounds[1], bounds[3] + 1):
            progress = (y - bounds[1]) / max(1, bounds[3] - bounds[1])
            color = tuple(round(top[index] * (1 - progress) + bottom[index] * progress) for index in range(4))
            gradient_draw.line((bounds[0], y, bounds[2], y), fill=color)
        self.image.paste(gradient, (0, 0), mask)
        self.draw = ImageDraw.Draw(self.image)
        if outline:
            shape(self.draw, None, outline, width)

    def ellipse(self, bounds, fill, outline=INK, width=4):
        def shape(draw, shape_fill, shape_outline, shape_width):
            draw.ellipse(box(bounds), fill=shape_fill, outline=shape_outline, width=max(1, p(shape_width)))

        self._paint_gradient(shape, fill, outline, width)

    def rounded(self, bounds, radius, fill, outline=INK, width=4):
        def shape(draw, shape_fill, shape_outline, shape_width):
            draw.rounded_rectangle(box(bounds), radius=p(radius), fill=shape_fill, outline=shape_outline, width=max(1, p(shape_width)))

        self._paint_gradient(shape, fill, outline, width)

    def polygon(self, points, fill, outline=INK, width=4):
        scaled = [(p(x), p(y)) for x, y in points]

        def shape(draw, shape_fill, shape_outline, shape_width):
            draw.polygon(scaled, fill=shape_fill)
            if shape_outline:
                draw.line(scaled + [scaled[0]], fill=shape_outline, width=max(1, p(shape_width)), joint="curve")

        self._paint_gradient(shape, fill, outline, width)

    def line(self, points, fill=INK, width=4):
        self.draw.line([(p(x), p(y)) for x, y in points], fill=fill, width=max(1, p(width)), joint="curve")

    def arc(self, bounds, start, end, fill, width=4):
        self.draw.arc(box(bounds), start, end, fill=fill, width=max(1, p(width)))

    def mask_ellipse(self, bounds):
        mask = Image.new("L", self.image.size, 0)
        ImageDraw.Draw(mask).ellipse(box(bounds), fill=255)
        return mask

    def mask_polygon(self, points):
        mask = Image.new("L", self.image.size, 0)
        ImageDraw.Draw(mask).polygon([(p(x), p(y)) for x, y in points], fill=255)
        return mask

    def speckles(self, mask, color, seed, count=50, radius=(0.45, 1.4), alpha=36):
        rng = Random(seed)
        layer = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        bounds = mask.getbbox()
        if not bounds:
            return
        for _ in range(count):
            x = rng.randint(bounds[0], max(bounds[0], bounds[2] - 1))
            y = rng.randint(bounds[1], max(bounds[1], bounds[3] - 1))
            r = p(rng.uniform(*radius))
            layer_draw.ellipse((x - r, y - r, x + r, y + r), fill=as_rgba(tuple(color[:3]) + (alpha,)))
        layer.putalpha(ImageChops.multiply(mask, layer.getchannel("A")))
        self.image.alpha_composite(layer)
        self.draw = ImageDraw.Draw(self.image)

    def soft_highlight(self, bounds, color=(255, 247, 219), alpha=78):
        layer = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse(box(bounds), fill=tuple(color) + (alpha,))
        self.image.alpha_composite(layer)
        self.draw = ImageDraw.Draw(self.image)

    def plate(self):
        self.ellipse((27, 166, 229, 224), (112, 70, 58, 45), None, 1)
        self.ellipse((31, 70, 225, 204), (255, 244, 213, 255), INK, 5)
        self.ellipse((48, 86, 208, 181), (255, 219, 178, 255), (156, 91, 69, 255), 3)

    def draw_item(self, kind):
        if kind == "chicken-leg":
            # Rounded pink drumstick inspired by the supplied reference:
            # bulbous meat, a short pale bone, and a soft juicy highlight.
            chicken = (222, 103, 98, 255)
            chicken_light = (248, 151, 139, 255)
            chicken_dark = (164, 62, 66, 220)
            bone = (255, 226, 208, 255)
            bone_shadow = (215, 141, 130, 255)

            shaft = [(119, 89), (148, 57), (160, 62), (132, 104)]
            self.polygon(shaft, bone, INK, 4)
            knob = [(151, 57), (151, 47), (157, 40), (165, 39), (171, 44), (173, 51), (181, 53), (184, 60), (180, 67), (171, 69), (164, 63)]
            self.polygon(knob, bone, INK, 4)
            self.line([(126, 86), (151, 61)], bone_shadow, 4)
            self.soft_highlight((158, 43, 166, 51), (255, 250, 235), 105)

            meat = [(55, 112), (61, 94), (75, 80), (94, 73), (115, 75), (132, 86), (140, 101), (139, 119), (130, 136), (118, 151), (103, 164), (85, 171), (68, 168), (54, 159), (46, 145), (45, 129)]
            self.polygon(meat, chicken, INK, 5)
            self.ellipse((53, 113, 112, 169), chicken_light, None, 1)
            self.polygon([(69, 103), (81, 89), (100, 85), (118, 91), (127, 104), (123, 116), (112, 125), (92, 130), (75, 123)], (239, 129, 121, 170), None, 1)

            # Pale fatty fold at the lower cut and two hand-painted surface glints.
            self.ellipse((72, 136, 116, 160), (255, 201, 188, 255), chicken_dark, 3)
            self.ellipse((81, 141, 107, 153), (255, 235, 215, 175), None, 1)
            self.soft_highlight((65, 94, 91, 117), (255, 224, 213), 108)
            self.soft_highlight((77, 84, 102, 98), (255, 244, 226), 70)
            self.line([(58, 126), (77, 115), (97, 112)], (255, 193, 180, 180), 4)
            self.line([(58, 139), (76, 133)], (179, 67, 70, 150), 3)
            self.line([(104, 94), (123, 103)], (255, 191, 176, 135), 3)
            self.speckles(self.mask_polygon(meat), (139, 52, 58), 21, 48, (0.4, 1.1), 27)
        elif kind == "bacon":
            self.polygon([(50, 44), (199, 38), (211, 203), (62, 213)], MEAT_LIGHT, INK, 5)
            for x in (76, 123, 170):
                self.line([(x, 50), (x + 10, 199)], FAT, 14)
                self.line([(x, 50), (x + 10, 199)], DARK, 3)
            self.line([(55, 93), (205, 84)], MEAT, 5)
            self.line([(59, 151), (208, 143)], (183, 64, 54, 210), 4)
            self.line([(75, 54), (84, 190)], (255, 213, 183, 140), 2)
            self.speckles(self.mask_polygon([(50, 44), (199, 38), (211, 203), (62, 213)]), DARK, 22, 54, (0.4, 1.1), 26)
        elif kind == "meatballs":
            left = [(29, 121), (31, 105), (40, 91), (55, 82), (73, 79), (91, 83), (106, 94), (117, 109), (123, 126), (118, 143), (108, 158), (94, 169), (77, 177), (59, 175), (44, 167), (34, 153), (28, 137)]
            top = [(91, 88), (95, 70), (103, 57), (119, 47), (136, 46), (151, 52), (165, 64), (175, 80), (181, 96), (176, 111), (166, 124), (151, 134), (136, 138), (119, 132), (104, 121), (96, 106)]
            right = [(139, 122), (146, 107), (157, 95), (172, 87), (188, 87), (204, 94), (216, 105), (224, 119), (223, 136), (217, 151), (205, 164), (190, 173), (174, 178), (158, 173), (147, 163), (140, 148), (137, 134)]
            self.polygon(left, MEAT, INK, 5)
            self.polygon(top, MEAT_LIGHT, INK, 5)
            self.polygon(right, DARK, INK, 5)
            self.soft_highlight((53, 100, 74, 120), (255, 213, 175), 58)
            self.soft_highlight((116, 61, 140, 83), (255, 221, 184), 56)
            self.soft_highlight((171, 103, 189, 121), (255, 203, 164), 45)
            self.ellipse((64, 119, 78, 129), (255, 201, 158, 210), None, 1)
            self.ellipse((124, 87, 137, 97), (255, 204, 160, 205), None, 1)
            self.ellipse((178, 128, 191, 138), (255, 194, 150, 190), None, 1)
            self.line([(45, 135), (67, 126)], (112, 43, 38, 190), 3)
            self.line([(104, 110), (126, 100)], (135, 50, 43, 170), 3)
            self.line([(184, 145), (204, 137)], (82, 31, 29, 175), 3)
            self.speckles(self.mask_polygon(left), (96, 39, 33), 23, 38, (0.45, 1.35), 36)
            self.speckles(self.mask_polygon(top), (116, 48, 38), 24, 38, (0.45, 1.35), 34)
            self.speckles(self.mask_polygon(right), (74, 29, 28), 25, 36, (0.45, 1.35), 38)
        elif kind == "thick-steak":
            self.polygon([(38, 90), (70, 51), (187, 47), (218, 95), (204, 169), (160, 202), (68, 191), (35, 149)], MEAT, INK, 5)
            self.ellipse((95, 92, 136, 135), FAT, DARK, 4)
            self.line([(57, 121), (98, 88), (161, 79), (193, 111)], MEAT_LIGHT, 7)
            self.line([(83, 165), (139, 142), (183, 148)], MEAT_LIGHT, 6)
            self.line([(59, 133), (105, 104), (168, 95)], (255, 185, 139, 120), 3)
            self.speckles(self.mask_polygon([(38, 90), (70, 51), (187, 47), (218, 95), (204, 169), (160, 202), (68, 191), (35, 149)]), DARK, 24, 78, (0.45, 1.3), 30)
            self.soft_highlight((73, 62, 104, 86), (255, 197, 153), 42)
        elif kind == "ribs":
            for y in (66, 103, 140):
                self.rounded((39, y, 205, y + 43), 17, MEAT_LIGHT, INK, 4)
                self.line([(61, y + 10), (180, y + 28)], FAT, 8)
                self.line([(73, y + 29), (184, y + 12)], DARK, 4)
            self.ellipse((182, 79, 220, 104), FAT, INK, 3)
            self.speckles(self.mask_ellipse((39, 66, 205, 183)), DARK, 25, 82, (0.4, 1.25), 26)
        elif kind == "pork-chop":
            self.polygon([(34, 95), (64, 56), (166, 45), (208, 85), (197, 169), (149, 205), (59, 183)], MEAT_LIGHT, INK, 5)
            self.ellipse((75, 93, 121, 137), FAT, DARK, 4)
            self.line([(133, 89), (177, 163)], MEAT, 8)
            self.line([(54, 141), (112, 164), (160, 149)], MEAT, 7)
            self.line([(54, 84), (73, 68)], EMBER, 4)
            self.speckles(self.mask_polygon([(34, 95), (64, 56), (166, 45), (208, 85), (197, 169), (149, 205), (59, 183)]), DARK, 26, 72, (0.4, 1.2), 30)
            self.soft_highlight((68, 65, 101, 93), (255, 213, 179), 46)
        elif kind == "roast-roll":
            self.ellipse((31, 64, 91, 193), MEAT_LIGHT, INK, 5)
            self.rounded((57, 64, 193, 193), 26, MEAT, INK, 5)
            self.ellipse((165, 64, 225, 193), MEAT_LIGHT, INK, 5)
            self.ellipse((80, 97, 173, 158), FAT, DARK, 5)
            self.line([(88, 77), (96, 180)], MEAT_LIGHT, 5)
            self.line([(136, 77), (142, 180)], MEAT_LIGHT, 5)
            self.line([(67, 87), (69, 170)], DARK, 4)
            self.line([(184, 87), (187, 170)], DARK, 4)
            self.speckles(self.mask_ellipse((57, 64, 193, 193)), DARK, 27, 66, (0.4, 1.2), 28)
        elif kind == "bone-steak":
            self.polygon([(45, 93), (74, 52), (168, 50), (202, 92), (183, 174), (87, 196), (44, 155)], MEAT, INK, 5)
            self.ellipse((170, 102, 217, 145), FAT, INK, 4)
            self.line([(188, 122), (225, 122)], FAT, 13)
            self.ellipse((212, 101, 233, 122), FAT, INK, 3)
            self.ellipse((212, 123, 233, 144), FAT, INK, 3)
            self.ellipse((89, 91, 124, 125), FAT, DARK, 3)
            self.line([(62, 125), (104, 90)], MEAT_LIGHT, 6)
            self.line([(111, 87), (156, 70)], MEAT_LIGHT, 6)
            self.speckles(self.mask_polygon([(45, 93), (74, 52), (168, 50), (202, 92), (183, 174), (87, 196), (44, 155)]), DARK, 28, 78, (0.45, 1.25), 28)
        elif kind == "pork-belly":
            self.rounded((35, 54, 220, 196), 25, MEAT, INK, 5)
            for y, color in ((77, FAT), (105, MEAT_LIGHT), (133, FAT), (161, MEAT_LIGHT)):
                self.line([(51, y), (204, y + 8)], color, 17)
                self.line([(51, y), (204, y + 8)], DARK if color == MEAT_LIGHT else (225, 160, 129, 255), 3)
            self.line([(66, 64), (183, 69)], EMBER, 4)
            self.speckles(self.mask_ellipse((35, 54, 220, 196)), DARK, 29, 86, (0.4, 1.2), 26)
        elif kind == "roasted-ribs":
            self.plate()
            for x, y, w in ((55, 99, 104), (78, 126, 111), (107, 94, 100)):
                self.rounded((x, y, x + w, y + 32), 15, MEAT, INK, 4)
                self.line([(x + 16, y + 9), (x + w - 14, y + 22)], FAT, 5)
                self.line([(x + 20, y + 22), (x + w - 22, y + 10)], DARK, 4)
            self.line([(54, 66), (43, 39)], GREEN, 7)
            self.line([(65, 67), (74, 36)], GREEN, 7)
            self.speckles(self.mask_ellipse((45, 86, 214, 178)), DARK, 30, 72, (0.45, 1.25), 28)
        elif kind == "meat-feast":
            self.plate()
            self.ellipse((48, 99, 106, 147), MEAT, INK, 4)
            self.rounded((97, 91, 172, 139), 18, MEAT_LIGHT, INK, 4)
            self.polygon([(145, 110), (178, 85), (208, 105), (193, 151), (159, 155)], GOLD, INK, 4)
            self.ellipse((104, 133, 169, 174), DARK, INK, 4)
            self.line([(57, 74), (46, 42)], GREEN, 7)
            self.line([(69, 75), (78, 40)], GREEN, 7)
            self.line([(177, 159), (197, 170)], GREEN, 5)
            self.ellipse((182, 166, 199, 177), (140, 190, 101, 255), INK, 2)
            self.speckles(self.mask_ellipse((48, 85, 208, 177)), DARK, 31, 90, (0.45, 1.3), 28)
        else:
            raise ValueError(kind)

    def finish(self):
        alpha = self.image.getchannel("A")
        shadow = Image.new("RGBA", self.image.size, (74, 61, 45, 0))
        shadow.putalpha(alpha.point(lambda value: round(value * 0.12)))
        offset = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        offset.alpha_composite(shadow, (0, p(4)))
        offset.alpha_composite(self.image)
        output = offset.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
        return polish_sticker(output)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for kind in ROUTE:
        painter = Painter()
        painter.draw_item(kind)
        target = OUT / f"{kind}.png"
        painter.finish().save(target, optimize=True)
        print(target)

    # Saves created during the sausage version can still be opened after the
    # rollback; the old key remains the canonical art and the sausage file is
    # kept as a compatibility alias.
    chicken_leg = OUT / "chicken-leg.png"
    if chicken_leg.exists():
        legacy = OUT / "sausage.png"
        with Image.open(chicken_leg) as image:
            image.convert("RGBA").save(legacy, optimize=True)
        print(legacy)


if __name__ == "__main__":
    main()
