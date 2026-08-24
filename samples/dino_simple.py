from tfwr.sim import *


def finished():
    n = can_move(North)
    e = can_move(East)
    s = can_move(South)
    w = can_move(West)
    return not (n or e or s or w)


def dino_simple():
    clear()
    change_hat(Hats.Dinosaur_Hat)
    while not finished():
        for i in range(get_world_size() - 1):
            move(North)
        for i in range((get_world_size() - 2) // 2):
            move(East)
            for i in range(get_world_size() - 2):
                move(South)
            move(East)
            for i in range(get_world_size() - 2):
                move(North)
        move(East)
        for i in range(get_world_size() - 1):
            move(South)
        for i in range(get_world_size() - 1):
            move(West)
    change_hat(Hats.Top_Hat)
