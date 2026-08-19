from tfwr.sim import *


def sort_rowcol(dir) -> None:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            current = measure()
            next = measure(dir)
            if current > next:
                swap(dir)
            move(dir)


def cactus() -> None:
    clear()
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Cactus)
            move(East)
        move(North)
    for i in range(get_world_size()):
        sort_rowcol(East)
        move(North)
    for i in range(get_world_size()):
        sort_rowcol(North)
        move(East)
    harvest()
