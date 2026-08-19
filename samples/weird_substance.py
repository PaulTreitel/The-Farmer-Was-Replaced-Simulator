from tfwr.sim import *


# Since trees give a lot of resources, this should get fertilizer pretty fast.
def weird_substance_strat() -> None:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            if (get_pos_x() + get_pos_y()) % 2 == 0:
                plant(Entities.Tree)
                use_item(Items.Fertilizer)
            else:
                plant(Entities.Bush)
            move(East)
        move(North)


def weird_substance_constant() -> None:
    for i in range(get_world_size()):
        for j in range(get_world_size()):
            if can_harvest():
                harvest()
            plant(Entities.Grass)
            use_item(Items.Fertilizer)
            move(East)
        move(North)
