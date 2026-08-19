from tfwr.sim import *


def tree() -> None:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            if (get_pos_x() + get_pos_y()) % 2 == 0:
                plant(Entities.Tree)
            else:
                plant(Entities.Bush)
            move(East)
        move(North)
