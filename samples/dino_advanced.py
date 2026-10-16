from typing import Any

# Overall Strategy:
# 1. Start at (0, 0) and move North up the full left column.
# 2. Go East then South to the apple.
# 3. If there is another apple reachable (above the coil) to the East, go to it.
#      Repeat 3 until there are no more reachable apples.
# 4. Go to the bottom right corner.
# 5. If the tail is long enough, coil it along the bottom rows.
# 6. Repeat 1-5 until the tail is long enough to fill the whole world.
#
# Steps 1-2 are essential because they guarantee that we will always be moving
# East to get to the next apple, so our tail will never block us when repeating
# step 3. Steps 4-5 reset us once we run out of apples and keep the tail out of
# the way.
#
# There is possible further optimization where we also collect apples that are
# to the West but South of the furthest we've gone (and hence not yet blocked
# by the tail) but this is difficult to get right.
from samples import utility
from tfwr.sim import *

WORLD_SIZE = get_world_size()
# Minimum coil length is the full bottom row + back and forth + rest of left column
MIN_COIL_LEN = WORLD_SIZE + (2 * (WORLD_SIZE - 1)) + WORLD_SIZE - 3


def dino_move(state, dir) -> None:
    if get_entity_type() == Entities.Apple:
        state["apple x"], state["apple y"] = measure()
        state["tail len"] += 1
    move(dir)


def coil(state) -> None:
    len_coiled = WORLD_SIZE - 1
    num_coils = 1
    dino_goto(state, 0, 0)
    dino_move(state, North)
    while len_coiled < state["tail len"]:
        dino_goto(state, WORLD_SIZE - 2, num_coils)
        dino_move(state, North)
        dino_goto(state, 0, num_coils + 1)
        dino_move(state, North)
        len_coiled += 2 * (WORLD_SIZE - 1)
        num_coils += 2
    state["coil height"] = num_coils


def dino_goto(state, x, y) -> None:
    start_x = get_pos_x()
    start_y = get_pos_y()
    x_dir, y_dir = East, North
    dx, dy = abs(start_x - x), abs(start_y - y)

    if x - start_x < 0:
        x_dir = West
    if y - start_y < 0:
        y_dir = South
    for i in range(dx):
        dino_move(state, x_dir)
    for i in range(dy):
        dino_move(state, y_dir)


def get_to_apple_all(state) -> None:
    dino_goto(state, state["apple x"], state["apple y"])
    state["apple x"], state["apple y"] = measure()
    max_x = get_pos_x()
    while max_x < state["apple x"] < WORLD_SIZE - 1:
        if state["apple y"] <= state["coil height"] + 1:
            break
        dino_goto(state, state["apple x"], state["apple y"])
        state["apple x"], state["apple y"] = measure()
        max_x = get_pos_x()


def dino_setup() -> dict[str, Any]:
    change_hat(Hats.Top_Hat)
    utility.goto(0, 0)
    change_hat(Hats.Dinosaur_Hat)
    apple_x, apple_y = measure()
    return {"tail len": 1, "apple x": apple_x, "apple y": apple_y, "coil height": 1}


def dino_solve():
    while True:
        state = dino_setup()
        while state["tail len"] < WORLD_SIZE**2:
            dino_goto(state, 0, WORLD_SIZE - 1)
            get_to_apple_all(state)
            dino_goto(state, WORLD_SIZE - 1, 0)
            if state["tail len"] >= MIN_COIL_LEN:
                coil(state)
