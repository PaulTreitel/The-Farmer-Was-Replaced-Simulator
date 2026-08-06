import random
from tfwr.sim import *
import tests.test_utils as utility
from cProfile import Profile
from pstats import SortKey, Stats


def sunflower_perf_test() -> None:
    import samples.sunflower
    for i in range(100):
        samples.sunflower.sunflower_dict()
    print_items()
    print(num_items(Items.Power))
    print((num_items(Items.Power) - 10**9) / (get_tick_count() / TICKS_PER_SECOND))


def pumpkin_perf_test() -> None:
    import samples.pumpkin
    for i in range(10):
        samples.pumpkin.pumpkin()
    print_items()
    print(num_items(Items.Pumpkin))


def cactus_perf_test() -> None:
    import samples.cactus
    for i in range(10):
        samples.cactus.cactus()
    print_items()
    print(num_items(Items.Cactus))


def carrot_perf_test() -> None:
    import samples.carrot
    for i in range(100):
        samples.carrot.carrot()
    print_items()
    print(num_items(Items.Carrot))


def tree_perf_test() -> None:
    import samples.tree
    for i in range(100):
        samples.tree.tree()
    print_items()
    print(num_items(Items.Wood))


def maze_perf_test() -> None:
    import samples.maze
    for i in range(100):
        samples.maze.maze()
    print_items()
    print(num_items(Items.Gold))


def weird_substance_perf_test() -> None:
    import samples.weird_substance
    for i in range(100):
        samples.weird_substance.weird_substance_constant()
    print_items()
    print(num_items(Items.Weird_Substance))


def dinosaur_perf_test() -> None:
    # This one doesn't really work because it's using my broken dino sample code.
    import samples.dino as dino
    from tfwr.sim import _farm
    state = dino.dino_setup()
    while state[dino.KEY_TAIL] < 500:
        dino.dino_goto(state, 0, 31)
        if dino.get_to_apple_all(state):
            print("Test ended early")
            print(f"my coords: {(get_pos_x(), get_pos_y())}")
            print(f"state is {state}")
            print(f'apple coords: {_farm.data["apple coords"]}')
            print_dense_entity_grounds()
            print("Test ended early")
            return
        dino.dino_goto(state, 31, 0)
        if state[dino.KEY_TAIL] >=  dino.MIN_COIL_LEN:
            dino.coil(state)
    print_dense_entity_grounds()
    
def run_test(f) -> None:
    config_unlock_all()
    config_give_items({item: 10**9 for item in Items})
    with Profile() as profile:
        f()
        (Stats(profile).strip_dirs().sort_stats(SortKey.TIME).print_stats(10))

def run_all_perf_tests() -> None:
    ALL_TESTS = {
        "Sunflower": sunflower_perf_test,
        "Pumpkin": pumpkin_perf_test,
        "Cactus": cactus_perf_test,
        "Carrot": carrot_perf_test,
        "Tree": tree_perf_test,
        "Maze": maze_perf_test,
        "Weird Substance": weird_substance_perf_test,
        "Dinosaur": dinosaur_perf_test
    }
    for test_name, test in ALL_TESTS.items():
        print("\n" * 4)
        print(f"STARTING {test_name} PERFORMANCE TEST".upper())
        print()
        run_test(test)
