from tfwr.sim import *
from tfwr.common import North, South, East, West
import tests.test_utils as utility
from tfwr.sim import _farm

utility.test_config(32)

petal_coords = {}
for i in range(get_world_size()):
    for j in range(get_world_size()):
        if get_ground_type() == Grounds.Grassland:
            till()
        plant(Entities.Sunflower)
        petals = measure()
        if petals in petal_coords:
            petal_coords[petals].append((get_pos_x(), get_pos_y()))
        else:
            petal_coords[petals] = [(get_pos_x(), get_pos_y())]
        move(East)
    move(North)

for i in range(10):
    do_a_flip()
    
utility.goto(petal_coords[15][0])
print("first max")
print(num_items(Items.Power))
harvest()
print(num_items(Items.Power))
utility.goto(petal_coords[15][1])
print("second max")
print(num_items(Items.Power))
harvest()
print(num_items(Items.Power))
utility.goto(petal_coords[7][0])
print("first min")
print(num_items(Items.Power))
harvest()
print(num_items(Items.Power))
utility.goto(petal_coords[15][2])
print("third max")
print(num_items(Items.Power))
harvest()
print(num_items(Items.Power))
utility.goto(petal_coords[15][3])
print("fourth max")
print(num_items(Items.Power))
harvest()
print(num_items(Items.Power))
