from pathlib import Path

from PIL import Image, ImageDraw


OUT = Path(__file__).resolve().parent / "web" / "assets" / "cooking"
SIZE = 256
SCALE = 3
INK = (76, 57, 46, 255)


def p(value):
    return int(value * SCALE)


def canvas():
    return Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))


def save(image, name):
    OUT.mkdir(parents=True, exist_ok=True)
    image.resize((SIZE, SIZE), Image.Resampling.LANCZOS).save(OUT / name, optimize=True)


def draw_pot():
    image = canvas()
    draw = ImageDraw.Draw(image)
    draw.ellipse((p(29), p(179), p(227), p(230)), fill=(81, 58, 47, 48))
    draw.ellipse((p(46), p(66), p(210), p(133)), fill=(255, 179, 67, 230), outline=INK, width=p(5))
    draw.rounded_rectangle((p(50), p(95), p(206), p(202)), radius=p(32), fill=(97, 82, 76, 255), outline=INK, width=p(6))
    draw.ellipse((p(57), p(87), p(199), p(139)), fill=(73, 62, 58, 255), outline=INK, width=p(4))
    draw.arc((p(69), p(23), p(111), p(95)), 190, 350, fill=(247, 126, 53, 255), width=p(8))
    draw.arc((p(102), p(12), p(149), p(89)), 190, 350, fill=(255, 198, 70, 255), width=p(8))
    draw.arc((p(139), p(23), p(181), p(95)), 190, 350, fill=(247, 126, 53, 255), width=p(8))
    draw.ellipse((p(73), p(112), p(103), p(140)), fill=(91, 177, 103, 255), outline=INK, width=p(3))
    draw.ellipse((p(113), p(105), p(145), p(136)), fill=(220, 75, 64, 255), outline=INK, width=p(3))
    draw.ellipse((p(151), p(113), p(181), p(141)), fill=(244, 187, 121, 255), outline=INK, width=p(3))
    save(image, "cooking-pot.png")


def draw_dish(name, level, colors):
    image = canvas()
    draw = ImageDraw.Draw(image)
    base, accent, garnish = colors
    draw.ellipse((p(28), p(174), p(228), p(229)), fill=(81, 58, 47, 48))
    draw.ellipse((p(31), p(74), p(225), p(204)), fill=(250, 237, 205, 255), outline=INK, width=p(5))
    draw.ellipse((p(50), p(91), p(206), p(181)), fill=base, outline=(126, 91, 59, 255), width=p(3))
    for x, y, color in ((86, 120, accent), (123, 103, base), (160, 122, accent), (122, 145, garnish)):
        draw.ellipse((p(x - 24), p(y - 18), p(x + 24), p(y + 18)), fill=color, outline=INK, width=p(3))
    draw.arc((p(53), p(48), p(205), p(230)), 190, 350, fill=garnish, width=p(6))
    draw.ellipse((p(168), p(50), p(195), p(77)), fill=(255, 216, 84, 255), outline=INK, width=p(3))
    if level >= 6:
        draw.ellipse((p(102), p(42), p(130), p(70)), fill=(255, 164, 65, 255), outline=INK, width=p(3))
        draw.arc((p(43), p(37), p(215), p(236)), 205, 335, fill=(239, 109, 67, 255), width=p(6))
    save(image, name)


draw_pot()
draw_dish("fusion-pot-lv4-garden-wrap.png", 4, ((247, 205, 121, 255), (91, 177, 103, 255), (244, 187, 121, 255)))
draw_dish("fusion-pot-lv4-golden-beef.png", 4, ((245, 169, 107, 255), (176, 73, 58, 255), (239, 135, 49, 255)))
draw_dish("fusion-pot-lv4-sea-pasta.png", 4, ((247, 161, 132, 255), (239, 126, 91, 255), (220, 75, 64, 255)))
draw_dish("fusion-pot-lv4-rainbow-skewer.png", 4, ((247, 205, 121, 255), (231, 133, 133, 255), (239, 169, 48, 255)))
draw_dish("fusion-pot-lv4-corn-cup.png", 4, ((248, 218, 117, 255), (244, 195, 48, 255), (244, 187, 121, 255)))
draw_dish("fusion-pot-lv5-jade-banquet.png", 5, ((157, 222, 174, 255), (91, 177, 103, 255), (176, 73, 58, 255)))
draw_dish("fusion-pot-lv5-sweet-sea.png", 5, ((249, 174, 139, 255), (239, 126, 91, 255), (239, 135, 49, 255)))
draw_dish("fusion-pot-lv5-rainbow-platter.png", 5, ((219, 175, 226, 255), (231, 133, 133, 255), (220, 75, 64, 255)))
draw_dish("fusion-pot-lv6-three-flavor.png", 6, ((255, 221, 111, 255), (91, 177, 103, 255), (239, 126, 91, 255)))
draw_dish("fusion-pot-lv6-harvest-cauldron.png", 6, ((250, 207, 117, 255), (244, 195, 48, 255), (231, 133, 133, 255)))
