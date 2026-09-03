from time import sleep

from tfwr.sim import *


def till_all():
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if get_ground_type() == Grounds.Grassland:
                till()
            move(East)
        move(North)


def show_entities(state, wait: float, coiling: bool = False) -> None:
    clear_screen()
    print_dense_entity_grounds()
    print(state)
    if coiling:
        print("COILING")
    sleep(wait)


def goto(x, y) -> None:
    while get_pos_x() < x:
        move(East)
    while get_pos_x() > x:
        move(West)
    while get_pos_y() < y:
        move(North)
    while get_pos_y() > y:
        move(South)
