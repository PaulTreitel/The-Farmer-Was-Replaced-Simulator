from tfwr.sim import *

def pumpkin() -> None:
    num_grown = 0
    while num_grown != get_world_size()**2:
        num_grown = 0
        for i in range(get_world_size()):
            for j in range(get_world_size()):
                if can_harvest():
                    if get_entity_type() == Entities.Pumpkin:
                        num_grown += 1
                    else:
                        harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                move(East)
            move(North)
    harvest()
