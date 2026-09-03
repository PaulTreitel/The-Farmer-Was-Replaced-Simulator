from typing import Any

from samples.utility import show_entities, till_all
from tfwr.sim import *

# Overall Strategy:
# 1. Start at (0, 0) and circle the edge of the farm.
# 2. If we are moving North or South and there is an apple in the same row, go
#    to it and come back on the following row. The whole path must be clear.
# 3. Once the tail is long enough, coil it along the bottom rows. For coiling,
#    we will ignore space that we already used to get apples before coiling.
#
# A further optimization is to continue collecting apples as long as they are in
# the same row as the one we're already collecting.

WORLD_SIZE = get_world_size()
# Total ring of the farm is 4 * WORLD_SIZE - 2 but 3x affords us a safety margin.
# There's a risk of collecting apples along the edge so in a single cycle we
# might not be able to coil the entire tail. 3x is a conservative safety margin.
MIN_COIL_LEN = 3 * WORLD_SIZE
COILING = False
SHOW_TIME = 0.1


def dino_setup() -> dict[str, Any]:
    clear()
    till_all()
    change_hat(Hats.Dinosaur_Hat)
    apple_x, apple_y = measure()
    return {
        "tail len": 1,
        "apple x": apple_x,
        "apple y": apple_y,
        "tail": [(0, 0)],
    }


def dino_move(state, dir) -> None:
    if get_entity_type() == Entities.Apple:
        state["apple x"], state["apple y"] = measure()
    else:
        state["tail"].pop(0)
    state["tail"].append((get_pos_x(), get_pos_y()))
    if move(dir) and get_entity_type() == Entities.Apple:
        state["tail len"] += 1
    show_entities(state, SHOW_TIME, COILING)


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


def valid_apple_target(state, dir_moving) -> bool:
    valid = state["apple y"] == get_pos_y()
    if dir_moving == North:
        valid = valid and get_pos_y() < WORLD_SIZE - 2
        valid = valid and state["apple x"] != 0
        valid = valid and (state["apple x"], state["apple y"] + 1) not in state["tail"]
    if dir_moving == South:
        valid = valid and state["apple x"] != WORLD_SIZE - 1
        valid = valid and get_pos_y() > 1
        valid = valid and (state["apple x"], state["apple y"] - 1) not in state["tail"]
    return valid


def coil(state) -> None:
    global COILING

    def coil_collide_west() -> bool:
        for i in range(1, get_pos_x()):
            if (i, get_pos_y() + 1) not in state["tail"]:
                return True
        return False

    def coil_goto(x) -> None:
        if get_pos_x() < x:
            for i in range(x - get_pos_x()):
                dino_move(state, East)
        else:
            for i in range(get_pos_x() - x):
                if not coil_collide_west():
                    break
                dino_move(state, West)

    COILING = True
    len_coiled = WORLD_SIZE - 1
    num_coils = 1
    if state["tail len"] >= WORLD_SIZE**2:
        return
    # We know we will go West then South so we can reduce the amount of coiling
    # that we need.
    while len_coiled < state["tail len"] - 2 * WORLD_SIZE:
        dino_move(state, North)
        x = get_pos_x()
        # dino_goto(state, 1, num_coils)
        coil_goto(1)
        len_coiled += x - get_pos_x()
        dino_move(state, North)
        x = get_pos_x()
        # dino_goto(state, WORLD_SIZE - 1, num_coils + 1)
        coil_goto(WORLD_SIZE - 1)
        len_coiled += get_pos_x() - x
        len_coiled += 2
        num_coils += 2
    COILING = False


def dino_cycle() -> None:
    state = dino_setup()
    while state["tail len"] < WORLD_SIZE**2:
        for i in range(WORLD_SIZE - 1):
            dino_move(state, East)

        if state["tail len"] >= MIN_COIL_LEN:
            coil(state)

        # micro-optimization: if there's an apple further along in the same row, get it
        for i in range(WORLD_SIZE - 1):
            dino_move(state, North)

            if valid_apple_target(state, North):
                while get_entity_type() != Entities.Apple:
                    dino_move(state, West)
                dino_move(state, North)
                while get_pos_x() < WORLD_SIZE - 1:
                    dino_move(state, East)

        for i in range(WORLD_SIZE - 1):
            dino_move(state, West)

        for i in range(WORLD_SIZE - 1):
            dino_move(state, South)

            if valid_apple_target(state, South):
                while get_entity_type() != Entities.Apple:
                    dino_move(state, East)
                dino_move(state, South)
                while get_pos_x() > 0:
                    dino_move(state, West)
