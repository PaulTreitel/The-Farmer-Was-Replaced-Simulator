from tfwr.sim import *


def bush() -> None:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            plant(Entities.Bush)
            move(East)
        move(North)
