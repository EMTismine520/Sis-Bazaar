import pygame
from .config import SCREEN_W, SCREEN_H, MARGIN, TOP_H, SCENE_H, BOARD_GAP, COLS, ROWS
from .game_state import GameState
from .input_adapter import Pointer
from .ui import draw_background, draw_hud, draw_scene, draw_board, draw_footer

def run():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED | pygame.RESIZABLE)
    pygame.display.set_caption("肥鹅美食街 · 合成小厨房")
    clock, state, pointer = pygame.time.Clock(), GameState(seed=7), Pointer()
    dragging = None
    running = True
    while running:
        dt = clock.tick(60) / 1000
        state.tick(dt)
        width, height = screen.get_size()
        sx, sy = width / SCREEN_W, height / SCREEN_H
        board_top = TOP_H + SCENE_H + BOARD_GAP
        board_width = SCREEN_W - MARGIN * 2
        cell = board_width / COLS
        board_rect = pygame.Rect(MARGIN, board_top, board_width, cell * ROWS)
        order_rect = pygame.Rect(215, 91, 158, 91)
        for action, raw_pos in pointer.events():
            if action == "quit":
                running = False
                continue
            pos = (raw_pos[0] / sx, raw_pos[1] / sy)
            if action == "down":
                if 305 <= pos[0] <= 375 and 17 <= pos[1] <= 57:
                    state.spawn_bag()
                elif 298 <= pos[0] <= 368 and board_rect.bottom + 14 <= pos[1] <= board_rect.bottom + 56:
                    state = GameState(seed=None)
                elif board_rect.collidepoint(pos):
                    col = int((pos[0] - board_rect.x) // cell); row = int((pos[1] - board_rect.y) // cell)
                    index = row * COLS + col
                    if state.board.cells[index]: dragging = index
            elif action == "up" and dragging is not None:
                target = None
                if board_rect.collidepoint(pos):
                    col = int((pos[0] - board_rect.x) // cell); row = int((pos[1] - board_rect.y) // cell)
                    target = row * COLS + col
                if target is not None:
                    result = state.board.move_or_merge(dragging, target)
                    if result == "merged": state.coins += 3; state.toast("合成成功！金币 +3")
                    elif result == "moved": state.toast("摆放完成")
                    elif state.submit(target): pass
                    else: state.toast("这里不能放置")
                elif order_rect.collidepoint(pos):
                    state.submit(dragging)
                dragging = None
        draw_background(screen); draw_hud(screen, state); draw_scene(screen, state, order_rect)
        draw_board(screen, state, board_rect, cell, dragging); draw_footer(screen, state, board_rect.bottom + 14)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__": run()
