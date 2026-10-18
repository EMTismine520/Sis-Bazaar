from dataclasses import dataclass

ITEMS = {
    "lettuce": {"name": "生菜", "emoji": "🥬", "color": (104, 178, 73)},
    "tomato": {"name": "番茄", "emoji": "🍅", "color": (221, 78, 54)},
    "pepper": {"name": "彩椒", "emoji": "🫑", "color": (238, 159, 43)},
    "broccoli": {"name": "西兰花", "emoji": "🥦", "color": (62, 156, 82)},
}

@dataclass
class Food:
    item_type: str
    level: int = 1

    @property
    def name(self):
        return ITEMS[self.item_type]["name"]

    @property
    def emoji(self):
        return ITEMS[self.item_type]["emoji"]

    @property
    def label(self):
        return f"{self.name} Lv.{self.level}"

def can_merge(a: Food | None, b: Food | None) -> bool:
    return bool(a and b and a.item_type == b.item_type and a.level == b.level and a.level < 3)

def merge(a: Food, b: Food) -> Food:
    if not can_merge(a, b):
        raise ValueError("foods cannot merge")
    return Food(a.item_type, a.level + 1)
