import pygame

class Pointer:
    def __init__(self):
        self.down = False
        self.pos = (0, 0)
        self.start = (0, 0)
        self.index = None

    def events(self):
        for event in pygame.event.get():
            if event.type in (pygame.QUIT,):
                yield "quit", None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.down, self.start, self.pos = True, event.pos, event.pos
                yield "down", event.pos
            elif event.type == pygame.MOUSEMOTION and self.down:
                self.pos = event.pos
                yield "move", event.pos
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.down, self.pos = False, event.pos
                yield "up", event.pos
            elif event.type == pygame.FINGERDOWN:
                p = (int(event.x * pygame.display.get_window_size()[0]), int(event.y * pygame.display.get_window_size()[1]))
                self.down, self.start, self.pos = True, p, p
                yield "down", p
            elif event.type == pygame.FINGERMOTION and self.down:
                p = (int(event.x * pygame.display.get_window_size()[0]), int(event.y * pygame.display.get_window_size()[1]))
                self.pos = p
                yield "move", p
            elif event.type == pygame.FINGERUP and self.down:
                p = (int(event.x * pygame.display.get_window_size()[0]), int(event.y * pygame.display.get_window_size()[1]))
                self.down, self.pos = False, p
                yield "up", p
