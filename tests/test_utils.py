from tfwr.common import East, North, South, West
from tfwr.sim import *


def goto(x, y=None) -> None:
    if y is None:
        x, y = x
    while get_pos_x() < x:
        move(East)
    while get_pos_x() > x:
        move(West)
    while get_pos_y() < y:
        move(North)
    while get_pos_y() > y:
        move(South)


def test_config(size) -> None:
    config_unlock_all()
    resources = {x: 10**9 for x in Items}
    config_set_items(resources)
    set_world_size(size)
