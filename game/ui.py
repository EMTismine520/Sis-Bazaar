import os
import pygame
from .config import *
from .items import ITEMS

def font(size, bold=False):
    bundled = os.path.join("assets", "simhei.ttf")
    if os.path.exists(bundled):
        return pygame.font.Font(bundled, size)
    candidates = ["microsoftyahei", "simhei", "arial"]
    for name in candidates:
        f = pygame.font.SysFont(name, size, bold)
        if f:
            return f
    return pygame.font.Font(None, size)

TITLE = font(24, True)
BODY = font(16)
SMALL = font(12)
EMOJI = font(34)

def rounded(surface, rect, color, radius=14, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border_color or ORANGE_DARK, rect, border, border_radius=radius)

def text(surface, value, pos, f=BODY, color=INK, center=False):
    image = f.render(str(value), True, color)
    r = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
    surface.blit(image, r)
    return r

def draw_background(surface):
    surface.fill(BG)
    for x, y, r in ((28, 205, 30), (350, 180, 42), (55, 370, 20), (330, 420, 28)):
        pygame.draw.circle(surface, (196, 229, 207), (x, y), r)
    for x in range(0, SCREEN_W, 24):
        pygame.draw.circle(surface, (235, 246, 229), (x, 96), 3)

def draw_hud(surface, state):
    rounded(surface, (12, 10, SCREEN_W - 24, 56), PANEL, 18, 2, ORANGE)
    text(surface, f"第 {state.day} 天", (23, 20), BODY, ORANGE_DARK)
    text(surface, f"🪙 {state.coins}", (122, 20), BODY, INK)
    text(surface, f"💎 {state.gems}", (226, 20), BODY, INK)
    rounded(surface, (305, 17, 70, 40), (255, 229, 172), 12, 1, ORANGE)
    text(surface, f"🥕 {state.bags}", (316, 25), SMALL, ORANGE_DARK)

def draw_scene(surface, state, order_rect):
    text(surface, "肥鹅小厨房", (18, 82), TITLE, ORANGE_DARK)
    text(surface, "今天也要做出好吃的料理！", (20, 111), SMALL, MUTED)
    pygame.draw.ellipse(surface, (250, 250, 232), (28, 130, 102, 70))
    text(surface, "🪿", (79, 151), EMOJI, INK, True)
    rounded(surface, order_rect, PANEL, 16, 2, ORANGE)
    text(surface, "今日订单", (order_rect.x + 14, order_rect.y + 10), SMALL, ORANGE_DARK)
    text(surface, f"{ITEMS[state.order.item_type]['emoji']}  {state.order.label}", (order_rect.x + 14, order_rect.y + 31), BODY, INK)
    text(surface, f"奖励  🪙 {state.order.reward}  +🥕5", (order_rect.x + 14, order_rect.y + 60), SMALL, MUTED)

def draw_board(surface, state, board_rect, cell_size, drag_index=None):
    rounded(surface, board_rect.inflate(8, 8), PANEL_BLUE, 18, 3, (112, 174, 184))
    for i in range(56):
        row, col = divmod(i, 7)
        x, y = board_rect.x + col * cell_size, board_rect.y + row * cell_size
        rect = pygame.Rect(x + 2, y + 2, cell_size - 4, cell_size - 4)
        rounded(surface, rect, (235, 244, 239), 10)
        food = state.board.cells[i]
        if food and i != drag_index:
            rounded(surface, rect.inflate(-8, -8), ITEMS[food.item_type]["color"], 12)
            text(surface, food.emoji, rect.center, EMOJI, center=True)
            text(surface, str(food.level), (rect.right - 15, rect.top + 7), SMALL, PANEL, center=True)
    if drag_index is not None and state.board.cells[drag_index]:
        food = state.board.cells[drag_index]
        text(surface, food.emoji, pygame.mouse.get_pos(), EMOJI, center=True)

def draw_footer(surface, state, y):
    rounded(surface, (12, y, SCREEN_W - 24, 52), PANEL, 15, 2, ORANGE)
    text(surface, state.message if state.message_timer else "拖动相同食材进行合成", (24, y + 17), SMALL, INK)
    rounded(surface, (298, y + 8, 70, 36), (255, 223, 173), 11, 1, ORANGE)
    text(surface, "重新开始", (333, y + 26), SMALL, ORANGE_DARK, True)
