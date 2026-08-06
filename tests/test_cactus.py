from tfwr.sim import *
from tfwr.common import North, South, East, West
import tests.test_utils as utility
from tfwr.sim import _farm

utility.test_config(4)

values = [
    [
        [3, 6, 6, 4],
        [6, 7, 8, 5],
        [9, 9, 2, 2],
        [2, 9, 6, 0]
    ],
    [
        [5, 1, 4, 3],
        [3, 5, 9, 9],
        [1, 5, 9, 1],
        [9, 5, 7, 4]
    ],
    [
        [8, 3, 1, 9],
        [2, 1, 4, 4],
        [6, 1, 1, 2],
        [7, 1, 3, 7]
    ],
    [
        [7, 6, 8, 0],
        [8, 7, 2, 3],
        [5, 4, 5, 2],
        [9, 8, 9, 1]
    ]
]
expects = [
    [
        [512, 512, 0, 0],
        [512, 512, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ],
    [
        [0, 0, 0, 0],
        [0, 288, 288, 0],
        [0, 288, 0, 0],
        [0, 0, 0, 0]
    ],
    [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 128, 128]
    ],
    [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ]
]

def set_cacti(iter) -> None:
    for y in range(get_world_size()):
        for x in range(get_world_size()):
            till()
            plant(Entities.Cactus)
            tile = _farm.current_tile
            tile.data["cactus size"] = values[iter][y][x]
            move(East)
        move(North)

def harvest_cacti(iter) -> None:
    for y in range(get_world_size()):
        for x in range(get_world_size()):
            valid, _ = _farm.harvester._get_valid_cacti()
            mult = _farm.harvester._get_harvest_mult(Entities.Cactus)
            num_cacti_earned = len(valid)**2 * mult
            if len(valid) == 0:
                num_cacti_earned = 0
            assert num_cacti_earned == expects[iter][y][x]
            move(East)
        move(North)

for i in range(len(values)):
    utility.test_config(4)
    set_cacti(i)
    for j in range(5):
        do_a_flip()
    print("cacti set")
    harvest_cacti(i)
    print("cacti harvested")