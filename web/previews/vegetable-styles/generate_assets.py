from pathlib import Path
from random import Random
from math import cos, pi, sin

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
KINDS = (
    "cabbage",
    "tomato",
    "pepper",
    "carrot",
    "mushroom",
    "corn",
    "potato",
    "purple-cabbage",
)
INK = (55, 53, 42, 255)

PALETTES = {
    "sticker": {
        "leaf": (77, 163, 91), "leaf-light": (144, 208, 119),
        "red": (226, 73, 64), "red-light": (255, 143, 106),
        "pepper": (246, 168, 48), "orange": (237, 119, 45),
        "cream": (248, 223, 160), "cap": (144, 91, 60),
        "soil": (184, 139, 91), "purple": (150, 85, 166),
        "purple-light": (202, 141, 199), "vein": (76, 137, 81),
    },
    "watercolor": {
        "leaf": (96, 147, 96), "leaf-light": (165, 190, 132),
        "red": (193, 91, 77), "red-light": (229, 151, 119),
        "pepper": (219, 163, 83), "orange": (205, 127, 78),
        "cream": (237, 216, 169), "cap": (137, 104, 78),
        "soil": (169, 139, 103), "purple": (137, 101, 149),
        "purple-light": (185, 143, 180), "vein": (91, 130, 91),
    },
    "pixel": {
        "leaf": (34, 132, 69), "leaf-light": (98, 193, 82),
        "red": (218, 48, 42), "red-light": (255, 111, 54),
        "pepper": (255, 184, 33), "orange": (235, 91, 25),
        "cream": (255, 228, 123), "cap": (142, 70, 39),
        "soil": (190, 125, 49), "purple": (126, 53, 163),
        "purple-light": (199, 92, 190), "vein": (28, 97, 57),
    },
}


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


def as_rgba(color):
    return tuple(color) if len(color) == 4 else tuple(color) + (255,)


def mix_color(first, second, amount):
    return tuple(round(first[index] * (1 - amount) + second[index] * amount) for index in range(4))


def lobed_points(cx, cy, rx, ry, lobes=7, depth=0.08, phase=0.0):
    """Return a smooth scalloped outline for a leafy head."""
    points = []
    for index in range(96):
        angle = 2 * pi * index / 96
        radius = 1 + depth * sin(lobes * angle + phase)
        points.append((cx + rx * radius * cos(angle), cy + ry * radius * sin(angle)))
    return points


class Painter:
    def __init__(self, style):
        self.style = style
        self.scale = 0.64 if style == "pixel" else 4
        size = 64 if style == "pixel" else 1024
        self.image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.palette = PALETTES[style]
        self.outline = (79, 57, 45, 226) if style == "sticker" else (94, 77, 59, 110 if style == "watercolor" else 225)

    def p(self, value):
        return round(value * self.scale)

    def box(self, values):
        return tuple(self.p(v) for v in values)

    def _paint_gradient(self, shape, fill, outline, width):
        rgba = as_rgba(fill)
        if self.style != "sticker" or rgba[3] < 220:
            shape(self.draw, fill, outline, width)
            return
        mask = Image.new("L", self.image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        shape(mask_draw, 255, None, 0)
        bounds = mask.getbbox()
        if not bounds:
            return
        top = mix_color(rgba, (255, 250, 224, 255), 0.24)
        bottom = mix_color(rgba, (54, 35, 28, 255), 0.18)
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

    def ellipse(self, bounds, fill, outline=None, width=2):
        def shape(draw, shape_fill, shape_outline, shape_width):
            draw.ellipse(self.box(bounds), fill=shape_fill, outline=shape_outline, width=max(1, self.p(shape_width)))

        self._paint_gradient(shape, fill, outline, width)

    def polygon(self, points, fill, outline=None, width=2):
        scaled = [(self.p(x), self.p(y)) for x, y in points]

        def shape(draw, shape_fill, shape_outline, shape_width):
            draw.polygon(scaled, fill=shape_fill)
            if shape_outline:
                draw.line(scaled + [scaled[0]], fill=shape_outline, width=max(1, self.p(shape_width)), joint="curve")

        self._paint_gradient(shape, fill, outline, width)

    def rounded(self, bounds, radius, fill, outline=None, width=2):
        def shape(draw, shape_fill, shape_outline, shape_width):
            draw.rounded_rectangle(self.box(bounds), radius=self.p(radius), fill=shape_fill, outline=shape_outline, width=max(1, self.p(shape_width)))

        self._paint_gradient(shape, fill, outline, width)

    def line(self, points, fill, width=2):
        self.draw.line([(self.p(x), self.p(y)) for x, y in points], fill=fill, width=max(1, self.p(width)), joint="curve")

    def arc(self, bounds, start, end, fill, width=2):
        self.draw.arc(self.box(bounds), start, end, fill=fill, width=max(1, self.p(width)))

    def mask_ellipse(self, bounds):
        mask = Image.new("L", self.image.size, 0)
        ImageDraw.Draw(mask).ellipse(self.box(bounds), fill=255)
        return mask

    def mask_polygon(self, points):
        mask = Image.new("L", self.image.size, 0)
        ImageDraw.Draw(mask).polygon([(self.p(x), self.p(y)) for x, y in points], fill=255)
        return mask

    def speckles(self, mask, color, seed, count=42, radius=(0.5, 1.4), alpha=42):
        rng = Random(seed)
        layer = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        bounds = mask.getbbox()
        if not bounds:
            return
        for _ in range(count):
            x = rng.randint(bounds[0], max(bounds[0], bounds[2] - 1))
            y = rng.randint(bounds[1], max(bounds[1], bounds[3] - 1))
            r = self.p(rng.uniform(*radius))
            layer_draw.ellipse((x - r, y - r, x + r, y + r), fill=as_rgba(tuple(color[:3]) + (alpha,)))
        layer.putalpha(ImageChops.multiply(mask, layer.getchannel("A")))
        self.image.alpha_composite(layer)
        self.draw = ImageDraw.Draw(self.image)

    def soft_highlight(self, bounds, color=(255, 247, 219), alpha=80):
        layer = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse(self.box(bounds), fill=tuple(color) + (alpha,))
        self.image.alpha_composite(layer)
        self.draw = ImageDraw.Draw(self.image)

    def leaf(self, bounds, color, vein=True):
        self.ellipse(bounds, color, self.outline if self.style == "sticker" else None, 2)
        if vein:
            x1 = (bounds[0] + bounds[2]) / 2
            self.line([(x1, bounds[1] + 5), (x1, bounds[3] - 5)], self.palette["vein"], 2)

    def draw_kind(self, kind):
        p = self.palette
        if kind == "cabbage":
            silhouette = lobed_points(54, 57, 36, 34, lobes=7, depth=0.085, phase=-0.25)
            self.polygon(silhouette, p["leaf"], self.outline, 2)
            self.ellipse((23, 36, 55, 78), p["leaf-light"], None, 1)
            self.ellipse((34, 23, 68, 67), (111, 191, 91, 235), None, 1)
            self.ellipse((54, 28, 87, 69), p["leaf-light"], None, 1)
            self.ellipse((36, 49, 73, 90), (129, 201, 101, 235), None, 1)
            self.arc((20, 31, 67, 82), 34, 155, (57, 139, 70, 210), 2)
            self.arc((34, 21, 84, 80), 210, 340, (207, 239, 153, 220), 2)
            self.arc((43, 40, 88, 91), 195, 320, (65, 151, 73, 200), 2)
            self.line([(47, 79), (51, 62), (62, 45)], (239, 255, 190, 220), 2)
            if self.style == "sticker":
                self.speckles(self.mask_polygon(silhouette), (44, 126, 57), 11, 86, (0.35, 1.2), 32)
                self.soft_highlight((29, 35, 52, 58), (240, 255, 190), 88)
                self.soft_highlight((50, 30, 68, 47), (225, 250, 170), 55)
        elif kind == "tomato":
            self.ellipse((19, 27, 81, 84), p["red"], self.outline, 2)
            self.ellipse((27, 35, 49, 55), p["red-light"], None)
            self.polygon([(48, 39), (40, 25), (47, 28), (51, 17), (57, 29), (68, 23), (62, 38), (54, 34)], p["leaf"], self.outline if self.style == "sticker" else None)
            self.line([(52, 32), (57, 14)], p["vein"], 4)
            if self.style == "sticker":
                self.soft_highlight((30, 38, 47, 52), (255, 219, 178), 74)
                self.speckles(self.mask_ellipse((19, 27, 81, 84)), (173, 44, 39), 12, 54, (0.35, 1.0), 26)
                self.arc((27, 31, 75, 80), 202, 320, (255, 143, 106, 115), 1.5)
        elif kind == "pepper":
            rear = [(30, 31), (40, 35), (47, 29), (58, 34), (66, 46), (61, 70), (49, 81), (37, 76), (26, 67), (23, 47)]
            front = [(48, 28), (58, 33), (66, 27), (78, 35), (84, 49), (79, 75), (67, 87), (53, 81), (43, 68), (42, 46)]
            self.polygon(rear, p["red"], self.outline)
            self.polygon(front, p["pepper"], self.outline)
            self.line([(54, 36), (53, 73)], (255, 222, 137, 255), 3)
            self.line([(67, 38), (64, 70)], (255, 237, 157, 220), 2)
            self.line([(48, 32), (50, 18), (57, 14)], p["leaf"], 5)
            self.line([(68, 31), (69, 17), (76, 15)], p["leaf"], 5)
            if self.style == "sticker":
                self.speckles(self.mask_polygon(front), (181, 114, 23), 13, 48, (0.35, 1.0), 28)
                self.soft_highlight((59, 38, 71, 53), (255, 247, 186), 70)
        elif kind == "carrot":
            body = [(27, 34), (68, 34), (64, 48), (56, 88), (43, 91), (30, 54)]
            self.polygon(body, p["orange"], self.outline)
            for y, offset in ((48, 0), (59, 2), (70, 3), (80, 4)):
                self.line([(36 + offset, y), (57 - offset, y - 3)], (255, 184, 103, 255), 2)
            self.line([(39, 35), (28, 19)], p["leaf"], 5)
            self.line([(48, 35), (47, 14)], p["leaf-light"], 5)
            self.line([(56, 35), (67, 18)], p["leaf"], 5)
            self.line([(61, 35), (76, 25)], (68, 145, 76, 255), 4)
            if self.style == "sticker":
                self.speckles(self.mask_polygon(body), (182, 74, 24), 14, 46, (0.35, 1.0), 30)
                self.soft_highlight((36, 40, 47, 71), (255, 221, 151), 55)
        elif kind == "mushroom":
            self.rounded((26, 50, 50, 84), 8, (240, 219, 178, 255), self.outline, 2)
            self.ellipse((17, 31, 60, 62), (129, 78, 48, 255), self.outline, 2)
            self.rounded((50, 49, 75, 84), 9, (246, 224, 184, 255), self.outline, 2)
            self.ellipse((43, 27, 84, 63), p["cap"], self.outline, 2)
            self.ellipse((29, 37, 39, 47), (250, 224, 177, 255), None)
            self.ellipse((60, 34, 70, 43), (250, 224, 177, 255), None)
            self.ellipse((50, 44, 58, 51), (238, 193, 137, 190), None)
            self.line([(27, 48), (39, 55)], (239, 189, 128, 200), 2)
            if self.style == "sticker":
                self.speckles(self.mask_ellipse((17, 27, 84, 63)), (89, 48, 31), 15, 70, (0.35, 1.1), 34)
                self.arc((21, 31, 56, 61), 188, 347, (226, 171, 119, 180), 2)
                self.arc((47, 29, 81, 61), 188, 347, (226, 171, 119, 160), 2)
        elif kind == "corn":
            self.polygon([(40, 30), (65, 31), (68, 76), (55, 86), (36, 74)], p["cream"], self.outline)
            for row in range(4):
                for col in range(3):
                    x, y = 42 + col * 8, 38 + row * 10
                    self.ellipse((x, y, x + 7, y + 8), (255, 198 + (row % 2) * 20, 54, 255), p["soil"] if self.style == "pixel" else None, 1)
            self.polygon([(39, 57), (18, 43), (23, 72), (44, 88), (49, 81)], p["leaf"], self.outline if self.style == "sticker" else None)
            self.polygon([(62, 55), (82, 43), (78, 72), (61, 88), (55, 80)], p["leaf-light"], self.outline if self.style == "sticker" else None)
            if self.style == "sticker":
                self.speckles(self.mask_polygon([(40, 30), (65, 31), (68, 76), (55, 86), (36, 74)]), (190, 132, 24), 16, 36, (0.35, 0.9), 35)
                self.soft_highlight((43, 33, 52, 68), (255, 250, 182), 66)
        elif kind == "potato":
            self.ellipse((28, 28, 72, 68), (194, 137, 72, 255), self.outline, 2)
            self.ellipse((46, 34, 86, 70), (207, 151, 79, 255), self.outline, 2)
            self.ellipse((17, 47, 64, 88), p["soil"], self.outline, 2)
            self.soft_highlight((28, 39, 49, 53), (255, 221, 160), 42)
            self.soft_highlight((55, 41, 68, 53), (255, 221, 160), 32)
            for x, y in ((31, 58), (52, 50), (67, 55), (45, 74), (25, 70), (74, 65)):
                self.ellipse((x, y, x + 5, y + 4), (112, 72, 46, 255), None)
                self.line([(x + 1, y + 5), (x + 5, y + 7)], (220, 174, 112, 255), 1)
            if self.style == "sticker":
                self.speckles(self.mask_ellipse((17, 28, 86, 88)), (119, 74, 39), 17, 84, (0.35, 1.2), 34)
        elif kind == "purple-cabbage":
            silhouette = lobed_points(53, 57, 36, 34, lobes=7, depth=0.08, phase=0.18)
            self.polygon(silhouette, p["purple"], self.outline, 2)
            self.ellipse((23, 35, 54, 76), p["purple-light"], None, 1)
            self.ellipse((35, 24, 68, 67), (170, 102, 177, 235), None, 1)
            self.ellipse((52, 31, 86, 71), (129, 65, 153, 238), None, 1)
            self.ellipse((34, 50, 74, 88), (112, 51, 139, 235), None, 1)
            self.arc((20, 31, 69, 82), 32, 156, (104, 49, 131, 205), 2)
            self.arc((34, 22, 84, 77), 206, 337, (226, 164, 214, 225), 2)
            self.arc((40, 42, 90, 92), 195, 325, (86, 40, 119, 210), 2)
            self.line([(48, 76), (48, 59), (60, 42)], (246, 199, 231, 245), 2)
            self.line([(48, 59), (33, 47)], (230, 165, 220, 220), 2)
            if self.style == "sticker":
                self.speckles(self.mask_polygon(silhouette), (83, 40, 112), 18, 80, (0.35, 1.1), 30)
                self.soft_highlight((28, 34, 49, 55), (255, 213, 244), 78)
                self.soft_highlight((48, 29, 66, 45), (245, 193, 229), 52)

    def finish(self):
        if self.style == "sticker":
            alpha = self.image.getchannel("A")
            shadow = Image.new("RGBA", self.image.size, (74, 61, 45, 0))
            shadow.putalpha(alpha.point(lambda a: round(a * 0.12)))
            offset = Image.new("RGBA", self.image.size, (0, 0, 0, 0))
            offset.alpha_composite(shadow, (0, self.p(3)))
            offset.alpha_composite(self.image)
            self.image = offset
        elif self.style == "watercolor":
            noise = Image.effect_noise(self.image.size, 38).convert("L")
            grain_alpha = noise.point(lambda value: 20 if value > 163 else 0)
            grain_alpha = ImageChops.multiply(grain_alpha, self.image.getchannel("A"))
            grain = Image.new("RGBA", self.image.size, (99, 82, 63, 0))
            grain.putalpha(grain_alpha)
            softened = self.image.filter(ImageFilter.GaussianBlur(1.1))
            self.image = Image.blend(self.image, softened, 0.16)
            self.image.alpha_composite(grain)
        if self.style == "pixel":
            return self.image.resize((256, 256), Image.Resampling.NEAREST)
        output = self.image.resize((256, 256), Image.Resampling.LANCZOS)
        return polish_sticker(output) if self.style == "sticker" else output


def main():
    for style in PALETTES:
        output = ROOT / "assets" / style
        output.mkdir(parents=True, exist_ok=True)
        for kind in KINDS:
            painter = Painter(style)
            painter.draw_kind(kind)
            painter.finish().save(output / f"{kind}.png", optimize=True)


if __name__ == "__main__":
    main()
