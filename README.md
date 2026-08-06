# The Farmer Was Replaced() Simulator

## Overview

This is a Python simulator for the game The Farmer Was Replaced(). It allows you to write code more or less like you're in the game, run it, and see the results. The idea is to be able to write and test code for the game without the code slowdown that the game imposes. 

This is intended to be a helpful teaching aid for doing more complex coding in a classic environment before using it in the game. I developed this while working at theCoderSchool and hope that others find it useful for teaching coding in the game.

## Installing and Dependencies

This project only depends on the `typing-extensions` package so simply clone the repository and make sure that package is installed. You can then run `python3 main.py`

## Features

The simulator includes nearly every upgrade, hat, function, plant, and resource provided in the game. You can progress a farm save with the simulator just like in the real game. They will behave more or less as they do in the game; if you find any issues where the game behavior is not reflected in the program behavior, please report it to me. In some cases where the game will silently fail and warn you, the simulator will instead crash with one of its own error types. This is intended to aid with using the simulator, since it's less clear what's going on when you don't have any GUI to look at. The only functionalities not implemented are the features below that are omitted for various reasons. Additionally there are load, save, and print featyres to make it possible to maintain a long-term save and have some visibility into what's going on.

### Features Not Implemented

These are features that did not make sense to add to the simulator. The unlocks remain available but they do not actually provide any functionality.

#### Megafarm

Megafarm involves multithreaded drones, which is something that is too complex to be worth trying to implement in this simulator.

#### Simulate

This is already a simulation program, it does not make sense to provide the game's simulate system.

#### Leaderboard

This is a test-and-simulate program meant to be run locally so a leaderboard does not make sense.

#### Hat Unlocks (except Top Hat and Dinosaur Hat)

I'm not entirely sure how most hats are even unlocked so by default they're all available except the two which are gated behind upgrades other than `Unlocks.Hats`

#### The ? Upgrade

The upgrade remains available but its effects have not been implemented. It's a secret!

## Functions Provided

### In-Game Functions

With the exception of the above features, all of the functions provided in the game are available here. The timing related functions do not behave as normal. `get_tick_count()` will still work, but since the simulation cannot account for how the game slows the code down, it will be a massive undercount vs in the game. In the simulation, for example, the A* algorithm will work fine but in-game the slowdown makes it unusably slow. Normally `get_time()` tells you the number of seconds since you started playing this session. Since the only thing that exists is the current run of the simulation, `get_time()` is equivalent to `get_tick_count() / 400`.

The functions `unlock()`, `num_items()`, `num_unlocked()`, and `get_cost()` are normally locked behind various unlocks but for the simulation are freely usable since there is no GUI to interact with.

#### ⚠️ WARNING ABOUT SPIN CODE ⚠️

In the game, you might make a code block to wait for a plant to grow like this:

```Python
while not can_harvest():
    pass
```

The game slows down your code and has the plant growing in the background so this works fine. The simulation does not slow down your code so the only time the plant grows is in the `can_harvest()` function call, which (a) only takes 1 tick, and (b) is computationally very expensive for the simulator. As such, instead of `pass` you should use either `do_a_flip()` or `pet_the_piggy()`.

### Configuration and Load/Save Functions

There are two functions for loading and saving, `load_game()` and `save_game()`. The save function has an optional parameter to save farms that have been shrunk using `set_world_size()` (otherwise the farm is reset).

To make setting up your test simulations easier, the following configuration functions are provided:

```Python
# functions are normally gated behind their relevant unlocks
config_ignore_function_requirements()
config_unlock_all()
config_set_unlocks(unlocks)
config_give_unlock(unlock, level=1)
config_set_items(items)
config_give_items(items)
# waits the given amount of time both in wall-clock time and in simulation time
wait_real_seconds(seconds)
```

### Printing Functions

The following functions print information about the farm state in full. This is not recommended for larger farms since a single row will spill across multiple lines in the terminal.

```Python
print_entities()
print_grounds()
print_full()
```

The following functions print information about the farm or a tile in a compact way suitable for larger farms. Each tile's data is a 2x2 character grid, so each function is very limited in what it can display.

```Python
# Prints the entity, grassland vs soil, and whether the tile is grown.
print_dense_entity_grounds()
# Prints the growth time and water level (1 sig fig each), with magenta text indicating infection.
print_dense_growth_water()
# Ignores values that are coordinates
print_measure()
# Prints the walls/boundaries.
print_pumpkins()
print_maze()
# Single tile print like print_full(). x can be an int or a coordinate tuple.
print_tile(x, y=None)
```

For your resources, there are also provided

```Python
print_items()
print_unlocks()
```

There is additionally a `clear_screen()` function provided to help for keeping the terminal clear and simple.