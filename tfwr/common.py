import json
from enum import Enum

###########################
####                   ####
####     DATA TYPES    ####
####                   ####
###########################


class UnlockError(Exception):
    pass


class EntityTypeError(Exception):
    pass


class ItemError(Exception):
    pass


class Direction(Enum):
    North = "North"
    East = "East"
    South = "South"
    West = "West"

    def __repr__(self):
        return self.name


class Grounds(Enum):
    Grassland = 0
    Soil = 1

    def __repr__(self):
        return f"Grounds.{self.name}"


class Entities(Enum):
    Grass = "Grass"
    Bush = "Bush"
    Tree = "Tree"
    Carrot = "Carrot"
    Pumpkin = "Pumpkin"
    Dead_Pumpkin = "Dead_Pumpkin"
    Sunflower = "Sunflower"
    Treasure = "Treasure"
    Hedge = "Hedge"
    Cactus = "Cactus"
    Apple = "Apple"
    Dinosaur = "Dinosaur"

    def __repr__(self):
        return f"Entities.{self.name}"


class Items(Enum):
    Hay = "Hay"
    Wood = "Wood"
    Carrot = "Carrot"
    Pumpkin = "Pumpkin"
    Cactus = "Cactus"
    Power = "Power"
    Gold = "Gold"
    Bone = "Bone"
    Weird_Substance = "Weird_Substance"
    Water = "Water"
    Fertilizer = "Fertilizer"

    def __repr__(self):
        return f"Items.{self.name}"


class Unlocks(Enum):
    Hats = "Hats"
    Cactus = "Cactus"
    Auto_Unlock = "Auto_Unlock"
    Carrots = "Carrots"
    Costs = "Costs"
    Debug = "Debug"
    Debug_2 = "Debug_2"
    Watering = "Watering"
    Variables = "Variables"
    Utilities = "Utilities"
    Trees = "Trees"
    Top_Hat = "Top_Hat"
    Timing = "Timing"
    Question_Mark = "Question_Mark"
    Sunflowers = "Sunflowers"
    Speed = "Speed"
    Simulation = "Simulation"
    Senses = "Senses"
    Pumpkins = "Pumpkins"
    Polyculture = "Polyculture"
    Plant = "Plant"
    Operators = "Operators"
    Megafarm = "Megafarm"
    Mazes = "Mazes"
    Loops = "Loops"
    Lists = "Lists"
    Leaderboard = "Leaderboard"
    Import = "Import"
    Grass = "Grass"
    Functions = "Functions"
    Fertilizer = "Fertilizer"
    Expand = "Expand"
    Dinosaurs = "Dinosaurs"
    Dictionaries = "Dictionaries"

    def __repr__(self):
        return f"Unlocks.{self.name}"


class Hats(Enum):
    Straw_Hat = "Straw_Hat"
    Brown_Hat = "Brown_Hat"
    Gray_Hat = "Gray_Hat"
    Green_Hat = "Green_Hat"
    Purple_Hat = "Purple_Hat"
    Cactus_Hat = "Cactus_Hat"
    Carrot_Hat = "Carrot_Hat"
    Gold_Hat = "Gold_Hat"
    Golden_Sunflower_Hat = "Golden_Sunflower_Hat"
    Pumpkin_Hat = "Pumpkin_Hat"
    Sunflower_Hat = "Sunflower_Hat"
    Traffic_Cone = "Traffic_Cone"
    Tree_Hat = "Tree_Hat"
    Wizard_Hat = "Wizard_Hat"
    Top_Hat = "Top_Hat"
    Dinosaur_Hat = "Dinosaur_Hat"

    def __repr__(self):
        return f"Hats.{self.name}"


Coords = tuple[int, int]
Companion = tuple[Entities, int, int]


###########################
####                   ####
####     CONST DATA    ####
####                   ####
###########################


def _load_costs() -> dict[Unlocks, list[dict[Items, int]]]:
    _costs = {}
    with open("tfwr/unlock_costs.json") as f:
        _costs = json.loads(f.read())
    unlock_costs = {}
    for str_unlock, str_cost_list in _costs.items():
        u = Unlocks(str_unlock)
        cost_list = []
        for level_cost_dict in str_cost_list:
            level_cost = {}
            for str_item, value in level_cost_dict.items():
                level_cost[Items(str_item)] = value
            cost_list.append(level_cost)
        unlock_costs[u] = cost_list
    return unlock_costs


UNLOCK_COSTS = _load_costs()

UNLOCK_PREREQS = {
    Unlocks.Loops: None,
    Unlocks.Grass: None,
    Unlocks.Hats: Unlocks.Loops,
    Unlocks.Speed: Unlocks.Loops,
    Unlocks.Expand: Unlocks.Speed,
    Unlocks.Plant: Unlocks.Speed,
    Unlocks.Carrots: Unlocks.Plant,
    Unlocks.Debug: Unlocks.Plant,
    Unlocks.Operators: Unlocks.Plant,
    Unlocks.Watering: Unlocks.Carrots,
    Unlocks.Trees: Unlocks.Carrots,
    Unlocks.Debug_2: Unlocks.Debug,
    Unlocks.Timing: Unlocks.Debug,
    Unlocks.Senses: Unlocks.Operators,
    Unlocks.Variables: Unlocks.Operators,
    Unlocks.Fertilizer: Unlocks.Watering,
    Unlocks.Sunflowers: Unlocks.Watering,
    Unlocks.Pumpkins: Unlocks.Trees,
    Unlocks.Simulation: Unlocks.Timing,
    Unlocks.Lists: Unlocks.Variables,
    Unlocks.Functions: Unlocks.Variables,
    Unlocks.Mazes: Unlocks.Fertilizer,
    Unlocks.Cactus: Unlocks.Pumpkins,
    Unlocks.Polyculture: Unlocks.Pumpkins,
    Unlocks.Leaderboard: Unlocks.Simulation,
    Unlocks.Dictionaries: Unlocks.Lists,
    Unlocks.Import: Unlocks.Functions,
    Unlocks.Utilities: Unlocks.Functions,
    Unlocks.Top_Hat: Unlocks.Mazes,
    Unlocks.Megafarm: Unlocks.Mazes,
    Unlocks.Dinosaurs: Unlocks.Cactus,
    Unlocks.Costs: Unlocks.Dictionaries,
    Unlocks.Question_Mark: Unlocks.Dinosaurs,
    Unlocks.Auto_Unlock: Unlocks.Costs,
}

BASE_PLANT_COSTS = {
    Entities.Carrot: {Items.Wood: 1, Items.Hay: 1},
    Entities.Cactus: {Items.Pumpkin: 2},
    Entities.Sunflower: {Items.Carrot: 1},
    Entities.Treasure: {Items.Weird_Substance: 1},
    Entities.Hedge: {Items.Weird_Substance: 1},
    Entities.Pumpkin: {Items.Carrot: 1},
    Entities.Dead_Pumpkin: {Items.Carrot: 1},
    Entities.Apple: {Items.Cactus: 2},
    Entities.Dinosaur: {Items.Cactus: 2},
}

PLANT_COST_MULTS = {
    Entities.Carrot: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
    Entities.Cactus: [1, 2, 4, 8, 16, 32],
    Entities.Sunflower: [1],
    Entities.Treasure: [1, 2, 4, 8, 16, 32],
    Entities.Hedge: [1, 2, 4, 8, 16, 32],
    Entities.Pumpkin: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
    Entities.Dead_Pumpkin: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
    Entities.Apple: [1, 2, 4, 8, 16, 32],
    Entities.Dinosaur: [1, 2, 4, 8, 16, 32],
}

EXPAND_SIZES = {
    0: (1, 1),
    1: (1, 3),
    2: (3, 3),
    3: (4, 4),
    4: (6, 6),
    5: (8, 8),
    6: (12, 12),
    7: (16, 16),
    8: (22, 22),
    9: (32, 32),
}

PLANT_GROWTH_TIME_SECS = {
    Entities.Grass: (0.5, 0.5),
    Entities.Bush: (3.2, 4.8),
    Entities.Carrot: (4.8, 7.2),
    Entities.Tree: (5.6, 8.4),
    Entities.Pumpkin: (0.2, 3.8),
    Entities.Cactus: (1.0, 1.0),
    Entities.Sunflower: (5.6, 8.4),
    # Entities.Dinosaur: (0.18, 0.22) # meaningless so far as I can tell
}

PLANT_YIELD_MULTS = {
    Entities.Grass: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
    Entities.Bush: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
    Entities.Tree: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
}

FUNC_PREREQS = {
    # Lists represent a boolean OR
    "plant": [(Unlocks.Plant, 1)],
    "clear": [(Unlocks.Plant, 1)],
    "change_hat": [(Unlocks.Hats, 1)],
    "can_harvest": [(Unlocks.Speed, 1)],
    "get_world_size": [(Unlocks.Expand, 2)],
    "till": [(Unlocks.Carrots, 1)],
    "move": [(Unlocks.Expand, 1)],
    "get_ground_type": [(Unlocks.Senses, 1)],
    "get_entity_type": [(Unlocks.Senses, 1)],
    "get_pos_x": [(Unlocks.Senses, 1)],
    "get_pos_y": [(Unlocks.Senses, 1)],
    "use_item": [(Unlocks.Watering, 1)],
    "can_move": [(Unlocks.Mazes, 1)],
    "get_companion": [(Unlocks.Polyculture, 1)],
    "measure": [(Unlocks.Sunflowers, 1), (Unlocks.Cactus, 1)],
    "swap": [(Unlocks.Cactus, 1)],
    "set_world_size": [(Unlocks.Debug_2, 1)],
    "get_water": [(Unlocks.Watering, 1)],
}

PLANT_YIELD_MULTS.update(PLANT_COST_MULTS)

UNLOCK_COUNTS = {x: len(UNLOCK_COSTS[x]) for x in UNLOCK_COSTS}

COMPANION_PLANTS = [Entities.Tree, Entities.Grass, Entities.Bush, Entities.Carrot]

REQUIRES_SOIL = [Entities.Carrot, Entities.Pumpkin, Entities.Cactus, Entities.Sunflower]

PLANTABLE = [
    Entities.Grass,
    Entities.Bush,
    Entities.Tree,
    Entities.Carrot,
    Entities.Pumpkin,
    Entities.Sunflower,
    Entities.Cactus,
]

MAZE_ENTITIES = [Entities.Hedge, Entities.Treasure]

UNHARVESTABLE = [Entities.Dead_Pumpkin, Entities.Apple]

USABLE_ITEMS = [Items.Weird_Substance, Items.Water, Items.Fertilizer]

North = Direction.North
East = Direction.East
South = Direction.South
West = Direction.West

ALL_DIRECTIONS = [North, East, South, West]

TICKS_PER_SECOND = 400

SPEED_MULTS = [1, 1.5, 2.25, 3.375, 5.0625, 7.59375]

WATER_PER_SECOND = [0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4, 12.8, 25.6]
FERTILIZER_PER_SECOND = [0.1, 0.2, 0.4, 0.8]

ENTITY_TO_ITEM = {
    Entities.Grass: Items.Hay,
    Entities.Bush: Items.Wood,
    Entities.Tree: Items.Wood,
    Entities.Carrot: Items.Carrot,
    Entities.Pumpkin: Items.Pumpkin,
    Entities.Cactus: Items.Cactus,
    Entities.Sunflower: Items.Power,
    Entities.Treasure: Items.Gold,
    Entities.Apple: Items.Bone,
    Entities.Dinosaur: Items.Bone,
}

ENTITY_TO_UNLOCK = {
    Entities.Grass: Unlocks.Grass,
    Entities.Bush: Unlocks.Plant,
    Entities.Tree: Unlocks.Trees,
    Entities.Carrot: Unlocks.Carrots,
    Entities.Pumpkin: Unlocks.Pumpkins,
    Entities.Dead_Pumpkin: Unlocks.Pumpkins,
    Entities.Cactus: Unlocks.Cactus,
    Entities.Sunflower: Unlocks.Sunflowers,
    Entities.Treasure: Unlocks.Mazes,
    Entities.Hedge: Unlocks.Mazes,
    Entities.Apple: Unlocks.Dinosaurs,
    Entities.Dinosaur: Unlocks.Dinosaurs,
}

###########################
####                   ####
####     FUNCTIONS     ####
####                   ####
###########################


def entity_to_upgrade_track(e: Entities) -> Unlocks:
    if e == Entities.Bush:
        return Unlocks.Trees
    return ENTITY_TO_UNLOCK[e]


def entity_to_dense_print(e: Entities) -> str:
    match e:
        case Entities.Grass:
            return "gr"
        case Entities.Bush:
            return "bu"
        case Entities.Tree:
            return "tr"
        case Entities.Carrot:
            return "ca"
        case Entities.Pumpkin:
            return "pu"
        case Entities.Dead_Pumpkin:
            return "dp"
        case Entities.Cactus:
            return "cc"
        case Entities.Sunflower:
            return "sf"
        case Entities.Treasure:
            return "ta"
        case Entities.Apple:
            return "ap"
        case Entities.Dinosaur:
            return "di"
        case Entities.Hedge:
            return "he"


def item_to_unlock(item: Items) -> Unlocks:
    match item:
        case Items.Hay:
            return Unlocks.Grass
        case Items.Wood:
            return Unlocks.Plant
        case Items.Carrot:
            return Unlocks.Carrots
        case Items.Pumpkin:
            return Unlocks.Pumpkins
        case Items.Cactus:
            return Unlocks.Cactus
        case Items.Power:
            return Unlocks.Sunflowers
        case Items.Gold:
            return Unlocks.Mazes
        case Items.Bone:
            return Unlocks.Dinosaurs
        case Items.Weird_Substance | Items.Fertilizer:
            return Unlocks.Fertilizer
        case Items.Water:
            return Unlocks.Watering


def round2(value: float) -> float:
    return int(value * 100) / 100


def coords_in_dir(dir: Direction, start: Coords) -> Coords:
    match dir:
        case Direction.North:
            return (start[0], start[1] + 1)
        case Direction.South:
            return (start[0], start[1] - 1)
        case Direction.East:
            return (start[0] + 1, start[1])
        case Direction.West:
            return (start[0] - 1, start[1])
