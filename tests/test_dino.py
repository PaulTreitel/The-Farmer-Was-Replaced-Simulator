from tfwr.sim import *
from tfwr.common import North, South, East, West, Coords
import tests.test_utils as utility
from tfwr.sim import _farm

def test_hat() -> None:
    utility.test_config(9)
    base_bones = num_items(Items.Bone)
    change_hat(Hats.Dinosaur_Hat)
    change_hat(Hats.Top_Hat)
    assert num_items(Items.Bone) == base_bones
    change_hat(Hats.Dinosaur_Hat)


def test_harvest() -> None:
    base_bones = num_items(Items.Bone)
    next = measure()
    utility.test_config(8)
    for i in range(4):
        utility.goto(next)
        print(get_time())
        next = measure()
        print(next)
        print_entities()
        print("\n")
        change_hat(Hats.Top_Hat)
        assert num_items(Items.Bone) == base_bones + 32 * 4**2
        print_entities()

def test_collision() -> None:
    utility.test_config(16)
    change_hat(Hats.Dinosaur_Hat)
    assert not can_move(West)
    assert not can_move(South)
    _farm.data["next apple coords"] = (1, 0)
    move(East)
    for i in range(1, 13):
        _farm.data["next apple coords"] = (1, i)
        move(North)
    assert not can_move(South)
    assert can_move(East)
    move(East)
    assert not can_move(West)
    assert can_move(East)
    move(East)
    assert can_move(South)
    move(South)
    assert not can_move(North)
    assert can_move(South)
    move(South)
    assert can_move(West)
    move(West)
    assert not can_move(East)
    assert can_move(North)
    move(North)
    assert not can_move(East)
    assert not can_move(South)
    assert not can_move(West)
    assert not can_move(North)
    for i in range(5):
        move(South)
    for i in range(5):
        move(East)
    print_dense_entity_grounds()
    

test_hat()
test_harvest()
test_collision()
    