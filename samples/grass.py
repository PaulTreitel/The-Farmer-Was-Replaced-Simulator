from tfwr.sim import *


def grass() -> None:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            plant(Entities.Grass)
            move(East)
        move(North)
