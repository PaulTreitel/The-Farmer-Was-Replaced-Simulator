import tests.test_utils as utility
from tfwr.common import East, North, South, West
from tfwr.sim import *


def gen_maze() -> None:
    utility.test_config(32)
    till()
    while get_entity_type() != Entities.Pumpkin:
        plant(Entities.Pumpkin)
    for i in range(4):
        move(East)
        till()
        while get_entity_type() != Entities.Pumpkin:
            plant(Entities.Pumpkin)
        move(North)
        till()
        while get_entity_type() != Entities.Pumpkin:
            plant(Entities.Pumpkin)
    plant(Entities.Bush)
    use_item(Items.Weird_Substance, 32 * 9)


def solve_maze() -> None:
    right = {North: East, East: South, South: West, West: North}
    left = {North: West, West: South, South: East, East: North}
    back = {North: South, South: North, East: West, West: East}
    dir = North
    while get_entity_type() != Entities.Treasure:
        if can_move(right[dir]):
            move(right[dir])
            dir = right[dir]
        elif can_move(dir):
            move(dir)
        elif can_move(left[dir]):
            move(left[dir])
            dir = left[dir]
        else:
            move(back[dir])
            dir = back[dir]
    harvest()


gen_maze()
