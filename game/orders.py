import random
from .items import Food, ITEMS

class Order:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.item_type = self.rng.choice(tuple(ITEMS))
        self.level = self.rng.choice((2, 3))
        self.reward = 16 + self.level * 8

    def matches(self, food: Food):
        return food.item_type == self.item_type and food.level == self.level

    @property
    def label(self):
        return f"{ITEMS[self.item_type]['name']} Lv.{self.level}"
