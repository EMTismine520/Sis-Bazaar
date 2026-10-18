import random
from .config import COLS, ROWS
from .items import Food, can_merge, merge

class Board:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.cells = [None] * (COLS * ROWS)

    def empty_index(self):
        try:
            return self.cells.index(None)
        except ValueError:
            return None

    def spawn(self, item_type=None):
        index = self.empty_index()
        if index is None:
            return None
        item_type = item_type or self.rng.choice(("lettuce", "tomato", "pepper", "broccoli"))
        self.cells[index] = Food(item_type)
        return index

    def move_or_merge(self, source, target):
        if source == target or not (0 <= source < len(self.cells)) or not (0 <= target < len(self.cells)):
            return "invalid"
        item = self.cells[source]
        if item is None:
            return "invalid"
        destination = self.cells[target]
        if destination is None:
            self.cells[target], self.cells[source] = item, None
            return "moved"
        if can_merge(item, destination):
            self.cells[target] = merge(item, destination)
            self.cells[source] = None
            return "merged"
        return "invalid"

    def index_of(self, item):
        return self.cells.index(item)
