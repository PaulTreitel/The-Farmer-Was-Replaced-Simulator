from tfwr.sim import *

def goto(x, y) -> None:
    while get_pos_x() < x:
        move(East)
    while get_pos_x() > x:
        move(West)
    while get_pos_y() < y:
        move(North)
    while get_pos_y() > y:
        move(South)

def sunflower_simple() -> None:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Sunflower)
            move(East)
        move(North)

def sunflower_dict() -> None:
    locations = {15: [], 14: [], 13: [], 12: [], 11: [], 10: [], 9: [], 8: [], 7: []}
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            plant(Entities.Sunflower)
            coords = (get_pos_x(), get_pos_y())
            locations[measure()].append(coords)
            move(East)
        move(North)
    for i in range(15, 6, -1):
        for coords in locations[i]:
            goto(coords[0], coords[1])
            while not can_harvest():
                # this would normally be `pass` but repeated calls to `can_harvest`
                # are actually horribly slow for the simulation
                do_a_flip()
            harvest()