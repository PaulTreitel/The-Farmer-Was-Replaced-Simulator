from tfwr.sim import *


def carrot() -> None:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Carrot)
            move(East)
        move(North)
