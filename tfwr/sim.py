import os
import time

import tfwr.farm_print
import tfwr.persist
from tfwr.common import (
    TICKS_PER_SECOND,
    UNLOCK_COUNTS,
    Direction,
    Entities,
    Grounds,
    Hats,
    Items,
    Unlocks,
)
from tfwr.farm import Farm

# These are redefinitions from tfwr/common.py given so that the simulation can
# work by only importing this file.
North = Direction.North
East = Direction.East
South = Direction.South
West = Direction.West


_farm = Farm()


#####################
###   FUNCTIONS   ###
#####################


def save_game(filepath, allow_small_farm=False) -> None:
    """
    Save the game to the given filepath.

    Keyword arguments:
    allow_small_farm -- if the farm is sized below its full size using `set_world_size()` then it will be saved at that size (default False)
    """
    tfwr.persist.save_game(filepath, _farm, allow_small_farm)


def load_game(filepath) -> None:
    """Load the game from the given filepath."""
    global _farm
    _farm = tfwr.persist.load_game(filepath)


def reset_game() -> None:
    """Reset the farm to its base state, effectively restarting the game."""
    global _farm
    _farm = Farm()


# CONFIG FUNCTIONS


def config_ignore_function_requirements() -> None:
    """Ignore all function call unlock requirements from now on."""
    _farm.override_func_unlock_requirements()


def config_set_unlocks(unlocks: dict[Unlocks, int]) -> None:
    """
    Override the farm's current unlocks to the given input.
    """
    _farm.set_unlocks(unlocks)


def config_unlock_all() -> None:
    """Unlock everything to the maximum level."""
    _farm.set_unlocks(UNLOCK_COUNTS)


def config_give_unlock(unlock: Unlocks, level: int = 1) -> None:
    """
    Grant yourself a specific unlock.

    Keyword arguments:
    level -- the level to grant the unlock, for example 5 to get the maximum Unlocks.Speed (default 1)
    """
    _farm.give_unlock(unlock)


def config_set_items(items) -> None:
    """
    Replaces the farm's current items with the input. The input should be dict[Items, int | float].
    """
    _farm.set_items(items)


def config_give_items(items) -> None:
    """
    Add the given items to the farm. Each item is added to the farm's current stockpiles. The input should be dict[Items, int | float].
    """
    for item, count in items.items():
        _farm.add_item(item, count)


def wait_real_seconds(seconds: float) -> None:
    """Progress the farm by the given amount of time and sleep the program for that long."""
    _farm.timer.add_real_ticks(int(seconds * TICKS_PER_SECOND))
    time.sleep(seconds)


# PRINT FUNCTIONS


def print_entities() -> None:
    """
    Print the entities on each tile of the farm.

    The entities are printed using their entity name (e.g., Carrot), or None if there is no entity. The value is printed in all caps if that tile has the drone. Note that this is not a very dense representation and so will be quite wide for larger farms.
    """
    _farm.timer.clear_unchecked_ticks()
    tfwr.farm_print.print_entities_internal(_farm)


def print_grounds() -> None:
    """
    Print the ground types of each tile of the farm.

    The grounds are printed as "GLand" for Grassland and "Soil" for soil. The value is printed in all caps if that tile has the drone. Note that this is not a very dense representation and so will be quite wide for larger farms.
    """
    tfwr.farm_print.print_grounds_internal(_farm)


def print_dense_entity_grounds() -> None:
    """
    Print information about the farm densely so it fits on one screen.

    Each tile is represented by a 2x2 grid of characters. The top two represent the entity on the tile, described using the key below. The bottom left character represents the ground type, "g" for Grassland and "s" for Soil. The bottom right character is a check mark when the tile is harvestable and blank otherwise. The tile's values are printed in all caps if that tile has the drone.

    Entity key:
    "--" -- None
    "gr" -- Grass
    "bu" -- Bush
    "ca" -- Carrot
    "tr" -- Tree
    "pu" -- Pumpkin
    "dp" -- Dead_Pumpkin
    "sf" -- Sunflower
    "ta" -- Treasure
    "cc" -- Cactus
    "ap" -- Apple
    "di" -- Dinosaur
    "he" -- Hedge
    """
    _farm.timer.clear_unchecked_ticks()
    tfwr.farm_print.print_dense_farm_internal(_farm)


def print_dense_growth_water() -> None:
    """
    Print information about tile growth time and water levels, as well as infection status.

    Each tile is represented by a 2x2 grid of characters. The top contains the remaining growth time. Due to space limitations this appears as 'X.' for a plant with X-point-some seconds remaining and '.Y' for a plant with zero-point-Y seconds remaining. The bottom contains the current water level of the tile, expressed in the '.Y' format, or left blank if the tile is completely dry. If the tile is infected, this information will appear in bright magenta.
    """
    _farm.timer.clear_unchecked_ticks()
    tfwr.farm_print.print_dense_tile_data_internal(_farm)


def print_tile(x: int | tuple[int, int], y: int | None = None) -> None:
    """
    Print all of the relevant information about a farm tile.

    Example:
    +------------+
    | (2, 2)     |
    | Sunflower  |
    | Soil       |
    | 2.16s left |
    | 0.23 water |
    | 12,infect  |
    +------------+
    """
    _farm.timer.clear_unchecked_ticks()
    tfwr.farm_print.print_tile_internal(_farm, x, y)


def print_full() -> None:
    """
    Print the full information about the entire farm.

    Effectively, this prints each tile as in the `print_tile()` function except the tiles are nicely visually arranged according to the grid of the farm.

    NOTE: This is not recommended on larger farms as the length of each line will exceed the width of the terminal.
    """
    _farm.timer.clear_unchecked_ticks()
    tfwr.farm_print.print_full_internal(_farm)


def print_items() -> None:
    """Print each item and how many the player has with numbers displayed as in game."""
    _farm.timer.clear_unchecked_ticks()
    tfwr.farm_print.print_items(_farm)


def print_unlocks() -> None:
    """
    Print each unlock and the unlock level the player has.
    """
    tfwr.farm_print.print_unlocks(_farm)


def print_measure() -> None:
    """
    Print the result of calling measure() on each tile, except that tiles that return coordinates are blank.

    This follows the print structure of dense_print_farm so printing full-size farms is readable.
    """
    tfwr.farm_print.print_dense_measure_internal(_farm)


def print_pumpkins() -> None:
    """
    Print a dense farm grid showing how the pumpkins on the farm have merged.

    The grid has Xs for non-pumpkins and empty spaces for pumpkins. Growing pumpkins are marked with "gr/wg". The internal edges of the grid are omitted between merged pumpkins.
    """
    _farm.timer.clear_unchecked_ticks()
    tfwr.farm_print.print_pumpkin_bounds(_farm)


def print_maze() -> None:
    """
    Print the walls of the maze on the farm (if there is one).
    """
    tfwr.farm_print.print_maze_internal(_farm)


def clear_screen() -> None:
    """Clear the screen."""
    os.system("cls" if os.name == "nt" else "clear")


# GAME INTERFACE


def do_a_flip() -> None:
    """Do a flip and progress the farm by 1 second."""
    _farm.timer.add_real_ticks(400)


def pet_the_piggy() -> None:
    """Pet the piggy and progress the farm by 1 second."""
    _farm.timer.add_real_ticks(400)


def harvest() -> bool:
    """Harvest the entity under the drone and return True if an entity was removed."""
    return _farm.harvester.harvest()


def can_harvest() -> bool:
    """Return if the plant under the drone can be harvested for resources."""
    return _farm.can_harvest()


def move(dir: Direction) -> bool:
    """
    Move the drone in the specified direction by one tile.

    If the drone moves over the edge of the farm it wraps back to the other side of the farm.
    Returns True if the drone has moved, False otherwise.
    """
    return _farm.move(dir)


def get_world_size() -> int:
    """Return the side-length of the farm in the north-to-south direction."""
    return _farm.get_world_size()


def plant(entity: Entities) -> bool:
    """
    Spends the cost of the specified `entity` and plants it under the drone.

    It fails if you can't afford the plant, the ground type is wrong, or there's already a plant there. Returns True if it succeeded, False otherwise.
    """
    return _farm.plant(entity)


def till() -> None:
    """Tills the square, converting it from Grassland to Soil or back."""
    _farm.till()


def get_ground_type() -> Grounds:
    """Return the ground type underneath the drone."""
    return _farm.get_ground_type()


def get_entity_type():
    """Return the entity under the drone, or None if there is no entity."""
    return _farm.get_entity_type()


def get_pos_x() -> int:
    """Return the x position of the drone."""
    return _farm.get_pos_x()


def get_pos_y() -> int:
    """Return the y position of the drone."""
    return _farm.get_pos_y()


def use_item(item: Items, quantity: int = 1) -> bool:
    """
    Attempts to use the specified `item` `quantity` times.

    Can only be used with some items including Items.Water and Items.Fertilizer. Returns True if an item was used, False otherwise.
    """
    return _farm.use_item(item, quantity)


def can_move(dir: Direction) -> bool:
    """Return if the drone can move in the given direction."""
    return _farm.can_move(dir)


def get_companion():
    """Return the companion information, or None if there is no companion."""
    return _farm.get_companion()


def get_cost(thing: Entities | Unlocks, upgrade_level=-1):
    """
    Return the cost of the input.

    The input must be an entity or an unlock. Returns a `dict[Items, int]` giving the cost of the thing, or None if the upgrade is already purchased/maxed.

    Keyword arguments:
    upgrade level -- If the input is an unlock, specifies the level of the unlock to retreive the cost of. Defaults to the next unlock level.
    """
    return _farm.get_cost(thing, upgrade_level)


def get_water():
    """Return the water level of the current tile."""
    return _farm.get_water()


def measure(direction: Direction | None = None):
    """
    Can measure some values on some entities. The effect depends on the entity.

    If `direction` is not None it measures the neighboring entity in that direction.
    Returns the number of petals of a sunflower.
    Returns the next position for a treasure or apple.
    Returns the size of a cactus.
    Returns a mysterious number for a pumpkin.
    Returns None for all other entities.
    """
    return _farm.measure(direction)


def num_items(item: Items) -> int | float:
    """Return how many of the given item you currently possess."""
    return _farm.num_items(item)


def num_unlocked(unlock: Unlocks | Items | Entities | Grounds) -> int:
    """
    Returns the number of times the given thing has been unlocked.

    If the input is an Unlock it will return the number of times that unlock has been unlocked/upgraded, or 0 if it hasn't been. If it's an Item, Entity, or Grounds, it will return 1 if it has been unlocked and 0 otherwise.
    """
    return _farm.num_unlocked(unlock)


def swap(dir: Direction) -> bool:
    """
    Swaps the entity under the drone with the entity next to the drone in the specified `direction`.

    Works only on Entities.Cactus and None.
    Returns True if it succeeded, False otherwise.
    """
    return _farm.swap(dir)


def clear() -> None:
    """Clear the farm and resets the drone to (0, 0)."""
    _farm.clear()


def set_world_size(size: int) -> None:
    """
    Limits the size of the farm to better see what's happening. Also clears and resets the farm.

    Sets the farm to a `size` x `size` grid. The smallest size possible is 3. A size smaller than 3 or greater than the current Expand unlock level will change it back to its full size.
    """
    _farm.set_world_size(size)


def unlock(unlock: Unlocks) -> bool:
    """Spend the resources to unlock the given unlock and return if it was successfully unlocked."""
    return _farm.unlock(unlock)


def change_hat(hat: Hats) -> None:
    """Change the hat on the drone."""
    _farm.change_hat(hat)


def get_tick_count() -> int | float:
    """
    Returns the number of ticks that have passed since the start of execution, rounded to the nearest hundredth.

    There are 400 ticks per second.
    IMPORTANT NOTE: In the game, regular code operations like addition, range(), etc also take ticks. This simulation **only counts ticks expended by the provided functions.** As such, this will always be a substantial undercount from real-game performance. For computationally expensive code (A* for example), this will vastly undercount leading to code that appears to run far faster than it would in the game.
    """
    return _farm.timer.get_tick_count()


def get_time() -> int | float:
    """
    Returns the number of seconds that have passed since the start of execution.

    Equivalent to get_tick_count() / 400 rounded to the nearest hundredth.
    IMPORTANT NOTE: In the game, regular code operations like addition, range(), etc also take time. This simulation **only counts time expended by the provided functions.** As such, this will always be a substantial undercount from real-game performance. For computationally expensive code (A* for example), this will vastly undercount leading to code that appears to run far faster than it would in the game.
    """
    return _farm.timer.get_time()


def set_execution_speed(speed) -> None:
    """
    Causes the drone to take operations at the set speed.

    Speed should be a decimal value, i.e., 1.5 represents 150% of base speed.

    Note that the in-game behavior sets limits on how fast this can be whereas this does not since it simply alters the tick counting.
    """
    _farm.timer.set_execution_speed(speed)
