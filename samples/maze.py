from tfwr.sim import *

right_of = {North:East, East:South, South:West, West:North}
left_of = {North:West, West:South, South:East, East:North}
backwards = {North:South, South:North, East:West, West:East}

def maze() -> None:
    clear()
    plant(Entities.Bush)
    substance = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
    use_item(Items.Weird_Substance, substance)
    facing = North
    while get_entity_type() != Entities.Treasure:
        if can_move(right_of[facing]):
            move(right_of[facing])
            facing = right_of[facing]
        elif can_move(facing):
            move(facing)
        elif can_move(left_of[facing]):
            move(left_of[facing])
            facing = left_of[facing]
        else:
            move(backwards[facing])
            facing = backwards[facing]
    harvest()
