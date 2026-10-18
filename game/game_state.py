import random
from .board import Board
from .orders import Order

class GameState:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.board = Board(self.rng)
        self.coins = 120
        self.gems = 3
        self.bags = 20
        self.day = 1
        self.order = Order(self.rng)
        self.message = "点击蔬菜包开始备菜"
        self.message_timer = 0
        for kind in ("lettuce", "lettuce", "tomato", "tomato", "pepper", "broccoli"):
            self.board.spawn(kind)

    def toast(self, message, seconds=2.0):
        self.message, self.message_timer = message, seconds

    def spawn_bag(self):
        if self.bags <= 0:
            self.toast("蔬菜包用完啦")
            return False
        if self.board.spawn() is None:
            self.toast("棋盘已满，先合成一些吧")
            return False
        self.bags -= 1
        self.toast("新鲜蔬菜到货！")
        return True

    def submit(self, index):
        food = self.board.cells[index]
        if food is None:
            return False
        if not self.order.matches(food):
            self.toast(f"订单需要 {self.order.label}")
            return False
        self.board.cells[index] = None
        reward = self.order.reward
        self.coins += reward
        self.bags += 5
        self.day += 1
        self.order = Order(self.rng)
        self.toast(f"订单完成！金币 +{reward}，蔬菜包 +5")
        return True

    def tick(self, dt):
        self.message_timer = max(0, self.message_timer - dt)
