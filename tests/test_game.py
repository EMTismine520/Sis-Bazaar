import random
from game.board import Board
from game.game_state import GameState
from game.items import Food, can_merge, merge

def test_same_food_merges():
    assert can_merge(Food("lettuce", 1), Food("lettuce", 1))
    assert merge(Food("lettuce", 2), Food("lettuce", 2)).level == 3

def test_different_food_does_not_merge():
    assert not can_merge(Food("lettuce"), Food("tomato"))

def test_level_three_is_max():
    assert not can_merge(Food("pepper", 3), Food("pepper", 3))

def test_full_board_does_not_spawn():
    board = Board(random.Random(1))
    for i in range(56): board.spawn("lettuce")
    assert board.spawn("tomato") is None

def test_spawn_uses_allowed_type():
    board = Board(random.Random(1))
    index = board.spawn()
    assert board.cells[index].item_type in {"lettuce", "tomato", "pepper", "broccoli"}

def test_order_completion_rewards():
    state = GameState(seed=1)
    state.order.item_type, state.order.level = "lettuce", 2
    state.board.cells[0] = Food("lettuce", 2)
    coins, bags = state.coins, state.bags
    assert state.submit(0)
    assert state.coins > coins and state.bags == bags + 5

def test_wrong_order_does_not_complete():
    state = GameState(seed=1)
    state.order.item_type, state.order.level = "tomato", 3
    state.board.cells[0] = Food("lettuce", 2)
    assert not state.submit(0)
