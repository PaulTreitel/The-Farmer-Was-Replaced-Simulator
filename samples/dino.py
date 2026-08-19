from typing import Any

from tfwr.sim import *

# THIS CODE DOES NOT WORK

KEY_TAIL = "tail len"
KEY_X = "apple x"
KEY_Y = "apple y"
KEY_COIL = "coil height"
MIN_COIL_LEN = 32 + (2 * 31) + 29
MAX_LEN = get_world_size() ** 2


def goto(x, y) -> None:
    while get_pos_x() < x:
        move(East)
    while get_pos_x() > x:
        move(West)
    while get_pos_y() < y:
        move(North)
    while get_pos_y() > y:
        move(South)


def dino_move(state, dir) -> None:
    if get_entity_type() == Entities.Apple:
        state[KEY_X], state[KEY_Y] = measure()
        state[KEY_TAIL] += 1
    move(dir)


def coil(state) -> None:
    len_coiled = 31
    num_coils = 1
    dino_goto(state, 0, 0)
    dino_move(state, North)
    while len_coiled < state[KEY_TAIL]:
        dino_goto(state, 30, num_coils)
        dino_move(state, North)
        dino_goto(state, 0, num_coils + 1)
        dino_move(state, North)
        len_coiled += 62
        num_coils += 2
    state[KEY_COIL] = num_coils


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


def get_to_apple(state) -> None:
    dx = state[KEY_X] - get_pos_x()
    dy = get_pos_y() - state[KEY_Y]
    for i in range(dx):
        # while get_pos_x() != state[KEY_X]:
        dino_move(state, East)
    for i in range(dy):
        # while get_pos_y() != state[KEY_Y]:
        dino_move(state, South)


def can_reach_all(state, max_x, min_y) -> None:
    x_right_valid = max_x < state[KEY_X] < 31
    # y_below_valid = state[KEY_COIL] < state[KEY_Y] < get_pos_y()
    # is_left = state[KEY_X] < get_pos_x()
    # above_min_y = min_y < get_pos_y()
    return x_right_valid  # or (y_below_valid and not (is_left and above_min_y))


def get_to_apple_all(state) -> bool | None:
    max_x = state[KEY_X]
    min_y = state[KEY_Y]
    get_to_apple(state)
    if finished(state) or get_entity_type() != Entities.Apple:
        print(
            f"1: finished {finished(state)}, entity {get_entity_type() != Entities.Apple}"
        )
        return True
    state[KEY_X], state[KEY_Y] = measure()
    while can_reach_all(state, max_x, min_y):
        # if state[KEY_X] < get_pos_x() and not can_move(West):
        # dino_move(state, South)
        if state[KEY_Y] <= state[KEY_COIL] + 1:
            break
        if state[KEY_X] == get_pos_x():
            break
        if state[KEY_X] == 31 and state[KEY_Y] > get_pos_y():
            break
        dino_goto(state, state[KEY_X], state[KEY_Y])
        if get_pos_x() != state[KEY_X]:
            dino_goto(state, state[KEY_X], state[KEY_Y])
        if finished(state) or get_entity_type() != Entities.Apple:
            print(
                f"2: finished {finished(state)}, entity {get_entity_type() != Entities.Apple}"
            )
            return True
        state[KEY_X], state[KEY_Y] = measure()
        max_x = max(max_x, get_pos_x())
        min_y = min(min_y, get_pos_y())


def dino_setup() -> dict[str, Any]:
    change_hat(Hats.Top_Hat)
    goto(0, 0)
    change_hat(Hats.Dinosaur_Hat)
    apple_x, apple_y = measure()
    return {KEY_TAIL: 2, KEY_X: apple_x, KEY_Y: apple_y, KEY_COIL: 1}


def finished(state) -> bool:
    moveable = False
    for dir in [North, South, East, West]:
        moveable = moveable or can_move(dir)
    return not moveable and state[KEY_TAIL] >= 1000


def dino_solve() -> None:
    while True:
        state = dino_setup()
        while True:
            dino_goto(state, 0, 31)
            if get_to_apple_all(state):
                break
            dino_goto(state, 31, 0)
            if state[KEY_TAIL] >= MIN_COIL_LEN:
                coil(state)
    change_hat(Hats.Top_Hat)
