import tests.test_utils as utility
from tfwr.common import REQUIRES_SOIL, East, North, South, West  # noqa: F401
from tfwr.sim import *

# Test predates timing/growth functionality

utility.test_config(16)
companions = {}

for i in range(get_world_size()):
    for j in range(get_world_size()):
        till()
        if (i + j) % 2 == 0:
            plant(Entities.Tree)
            e, x, y = get_companion()
            if (x, y) in companions:
                print(f"overwriting {companions[(x, y)]} with {e} at {(x, y)}")
            companions[(x, y)] = e
        move(East)
    move(North)

for y in range(get_world_size()):
    for x in range(get_world_size()):
        if (x, y) in companions and (x + y) % 2 != 0:
            print(f"planting {companions[(x, y)]} at {(x, y)}")
            # if companions[(x, y)] in REQUIRES_SOIL and get_ground_type() == Grounds.Grassland:
            #     till()
            plant(companions[(x, y)])
        move(East)
    move(North)

for i in range(get_world_size()):
    for j in range(get_world_size()):
        if get_entity_type() == Entities.Tree:
            old = num_items(Items.Wood)
            c = get_companion()
            harvest()
            harvest_size = num_items(Items.Wood) - old
            if harvest_size > 10_000:
                print(f"harvested {harvest_size} wood, companion is {c}")
        move(East)
    move(North)
