from tfwr.sim import *


def sort(dir):
    for i in range(get_world_size()):
        swapped = False  # optimization to prevent unnecessary passes if already sorted
        for j in range(get_world_size()):
            # Checks to prevent swaps over farm boundaries. Not
            # needed if you're okay with the error messages.
            if dir == North and get_pos_y() == get_world_size() - 1:
                move(dir)
                continue
            if dir == East and get_pos_x() == get_world_size() - 1:
                move(dir)
                continue
            curr = measure()
            next = measure(dir)
            if next < curr:
                if swap(dir):
                    swapped = True
            move(dir)
        if not swapped:
            return


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
        sort(East)
        move(North)
    for i in range(get_world_size()):
        sort(North)
        move(East)
    harvest()
