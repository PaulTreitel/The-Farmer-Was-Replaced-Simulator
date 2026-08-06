from tfwr.sim import *
from tfwr.common import North, South, East, West
import tests.test_utils as utility
from tfwr.sim import _farm

# Test predates timing/growth functionality
def plant_pumpkin() -> None:
    utility.test_config(8)
    for i in range(8):
        for j in range(8):
            till()
            plant(Entities.Pumpkin)
            move(East)
        move(West)
        move(West)
        move(North)

# Test postdates timing/growth functionality
def p_test() -> None:
    config_unlock_all()
    config_set_items({item: 10**7 for item in Items})
    for i in range(5):
        for j in range(get_world_size()):
            for k in range(get_world_size()):
                if get_ground_type() != Grounds.Soil:
                    till()
                plant(Entities.Pumpkin)
                move(East)
            move(North)
        print_pumpkins()
        print("\n\n")

p_test()