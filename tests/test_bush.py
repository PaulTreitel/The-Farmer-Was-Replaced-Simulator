from tfwr.sim import *
from tfwr.common import North, South, East, West
import tests.test_utils as utility
from tfwr.sim import _farm

# Test predates timing/growth functionality

utility.test_config(8)

print_entities()

for i in range(get_world_size()):
    for j in range(get_world_size()):
        plant(Entities.Bush)
        move(East)
    move(North)

print_entities()
print(num_items(Items.Wood))
for i in range(get_world_size()):
    for j in range(get_world_size()):
        harvest()
        print(num_items(Items.Wood))
        move(East)
    move(North)