import copy
from typing import Callable
from tfwr.common import *
import tfwr.disjoint_set as disjoint_set
from operator import le, ge

# Pumpkin infected formula
# * Weird Substance = 0.5 * base value * size mult * # of infected tiles
# Cactus infected formula
# * Weird Substance = 0.5 * base value * total # of tiles * # of infected tiles
# Sunflower infected
# * no effect in 1-yield, half of 8-yield

DINO_DATA_KEYS = [
    "dinosaur tail", "apple coords", "next apple coords", "dinosaur tail set"
]
MAZE_DATA_KEYS = [
    "maze tiles", "treasure coords", "next treasure coords", "times reused", 
    "walls", "possible walls", "maze size", "wall remove counter"
]

class Harvester:
    def __init__(self, farm):
        from tfwr.farm import Farm
        self.farm: Farm = farm
        self._last_sunflower_highest = True
        self.data = {}
        self.set_sunflower_data()

    def harvest(self) -> bool:
        plant_type = self.farm.current_tile.entity
        ret = False
        match plant_type:
            case Entities.Grass | Entities.Bush | Entities.Carrot | Entities.Tree:
                if not self.farm.current_tile.is_grown():
                    self.farm.timer.clear_unchecked_ticks()
                ret = self._basic_harvest()
            case Entities.Pumpkin:
                self.farm.timer.clear_unchecked_ticks()
                ret = self._pumpkin_harvest()
            case Entities.Sunflower:
                if not self.farm.current_tile.is_grown():
                    self.farm.timer.clear_unchecked_ticks()
                ret = self._sunflower_harvest()
            case Entities.Treasure:
                ret = self._maze_harvest()
            case Entities.Hedge:
                ret = self.maze_delete()
            case Entities.Cactus:
                self.farm.timer.clear_unchecked_ticks()
                ret = self._cactus_harvest()
            case Entities.Dead_Pumpkin | Entities.Apple | None:
                self.farm.current_tile.harvest()
                ret = False
        if ret:
            self.farm.timer.unchecked_ticks += 200
        else:
            self.farm.timer.unchecked_ticks += 1
        return ret

    def dinosaur_harvest(self) -> None:
        if "dinosaur tail" not in self.farm.data:
            return
        mult = self._get_harvest_mult(Entities.Apple)
        bones_earned = mult * (len(self.farm.data["dinosaur tail"]))**2
        self.farm.add_item(Items.Bone, bones_earned)
        for coords in self.farm.data["dinosaur tail"]:
            self.farm.get_tile(*coords).entity = None
        self.farm.get_tile(*self.farm.data["apple coords"]).entity = None
        for k in DINO_DATA_KEYS:
            self.data.pop(k, None)
        return

    def _basic_harvest(self) -> bool:
        tile = self.farm.current_tile
        self.farm.timer.remove_queue(tile)
        infected = tile.infected
        plant_type = tile.harvest()
        if plant_type is None:
            return True
        item = ENTITY_TO_ITEM[plant_type]
        mult = self._get_harvest_mult(plant_type)
        companion_mult = self._get_companion_mult(tile.get_companion())
        resources_earned = mult * companion_mult
        if infected:
            weird_amt = resources_earned // 2
            self.farm.add_item(item, resources_earned - weird_amt)
            self.farm.add_item(Items.Weird_Substance, weird_amt)
        else:
            self.farm.add_item(item, resources_earned)
        return True

    def _pumpkin_harvest(self) -> bool:
        tile = self.farm.current_tile
        if not tile.is_grown():
            self.farm.timer.remove_queue(tile)
            tile.harvest()
            return True

        subsets = self.farm.data["pumpkins"]
        p_extents: dict[tuple[int, int], int] = self.farm.data["pumpkin sizes"]
        p_sized_extents: dict[int, set[tuple[int, int]]] = (
            self.farm.data["pumpkin size locations"]
        )
        
        coords = (self.farm.x, self.farm.y)
        base_mult = self._get_harvest_mult(Entities.Pumpkin)
        infected_count = 0
        min_x, min_y = 32, 32
        for c in subsets.get_subset(coords):
            min_x = min(min_x, c[0])
            min_y = min(min_y, c[1])
            tile = self.farm.get_tile(*c)
            if tile.infected:
                infected_count += 1
            self.farm.timer.remove_queue(tile)
            tile.harvest()
            self.farm.data["pumpkin prefix"].add(*c, -1)

        size = p_extents[(min_x, min_y)]
        p_sized_extents[size].remove((min_x, min_y))
        p_extents.pop((min_x, min_y))
        subsets.remove_subset((min_x, min_y))
        harvest_size_mult = min(6, size)
        pumpkins_earned = base_mult * harvest_size_mult * size**2
        if infected_count > 0:
            weird_substance = base_mult * size * infected_count // 2
            pumpkins_earned -= weird_substance
            self.farm.add_item(Items.Weird_Substance, weird_substance)
        self.farm.add_item(Items.Pumpkin, pumpkins_earned)
        return True

    def _sunflower_harvest(self) -> bool:
        tile = self.farm.current_tile
        self.farm.timer.remove_queue(tile)
        def remove_sunflower():
            self.data["sunflower count"] -= 1
            self.data["sunflower sizes"][petal_count].discard(tile.coords)
            tile.harvest()
        assert "sunflower petals" in tile.data
        petal_count = tile.data["sunflower petals"]
        if not tile.is_grown():
            remove_sunflower()
            return True
        if self.data["sunflower count"] < 10:
            remove_sunflower()
            self.farm.add_item(Items.Power, 1)
            return True
            
        highest = self._get_highest_sunflower()
        current_matches_highest = tile.data["sunflower petals"] == highest
        if not self._last_sunflower_highest:
            self._last_sunflower_highest = current_matches_highest
            remove_sunflower()
            self.farm.add_item(Items.Power, 1)
            return True
        if current_matches_highest:
            if tile.infected:
                self.farm.add_item(Items.Power, 4)
                self.farm.add_item(Items.Weird_Substance, 4)
            else:
                self.farm.add_item(Items.Power, 8)
        else:
            self.farm.add_item(Items.Power, 1)
            self._last_sunflower_highest = False
        remove_sunflower()
        return True

    def set_sunflower_data(self) -> None:
        self.data["sunflower count"] = 0
        self.data["sunflower sizes"] = {i: set() for i in range(15, 6, -1)}
        for y in range(self.farm.farm_y):
            for x in range(self.farm.farm_x):
                tile = self.farm.get_tile(x, y)
                if tile.entity != Entities.Sunflower:
                    continue
                self.data["sunflower count"] += 1
                self.data["sunflower sizes"][tile.measure()].add((x, y))

    def _maze_harvest(self) -> bool:
        assert "maze tiles" in self.farm.data
        mult = self._get_harvest_mult(Entities.Treasure)
        gold_earned = mult * len(self.farm.data["maze tiles"])
        self.farm.add_item(Items.Gold, gold_earned)
        return self.maze_delete()

    def maze_delete(self) -> bool:
        all_coords = self.farm.data["maze tiles"]
        for coords in all_coords:
            tile = self.farm.get_tile(*coords)
            tile.clear()
            self.farm.timer.add_queue(tile)
        for k in MAZE_DATA_KEYS:
            self.farm.data.pop(k, None)
        return True

    def _cactus_harvest(self) -> bool:
        if not self.farm.current_tile.is_grown():
            self.farm.current_tile.harvest()
            return True
        valid, infected_count = self._get_valid_cacti()
        if len(valid) == 0:
            return True
        for coords in valid:
            self.farm.get_tile(*coords).harvest()
        mult = self._get_harvest_mult(Entities.Cactus)
        num_cacti_earned = len(valid)**2 * mult
        if infected_count > 0:
            weird_substance = mult * len(valid) * infected_count // 2
            self.farm.add_item(Items.Weird_Substance, weird_substance)
            num_cacti_earned -= weird_substance
        self.farm.add_item(Items.Cactus, num_cacti_earned)
        return True

    def _get_harvest_mult(self, plant_type: Entities) -> int:
        if plant_type not in PLANT_YIELD_MULTS:
            raise EntityTypeError(f"Entity type {plant_type} does not have a harvest multiplier")
        upgrade_track = entity_to_upgrade_track(plant_type)
        tree_locked = self.farm.unlocks[Unlocks.Trees] == 0
        if plant_type == Entities.Bush and tree_locked:
            upgrade_track = Unlocks.Plant
        upgrade_level = self.farm.unlocks[upgrade_track]
        mult = PLANT_YIELD_MULTS[plant_type][upgrade_level - 1]
        if plant_type == Entities.Tree:
            mult *= 5
        return mult

    def _get_companion_mult(self, companion_type: Companion|None) -> int:
        POLYCULTURE_MULTS = [5, 10, 20, 40, 80, 160]
        if companion_type is None:
            return 1
        x, y = self.farm.get_pos_x(), self.farm.get_pos_y()
        companion_coords = (x + companion_type[1], y + companion_type[2])
        tile = self.farm.get_tile(*self.farm.wrap_coords(companion_coords))
        if tile.entity != companion_type[0]:
            return 1
        polyculture_level = self.farm.unlocks[Unlocks.Polyculture]
        return POLYCULTURE_MULTS[polyculture_level]

    def _get_highest_sunflower(self) -> int:
        for i in range(15, 6, -1):
            if len(self.data["sunflower sizes"][i]) > 0:
                return i
        return -1

    def _get_valid_cacti(self) -> tuple[set[Coords], int]:
        open = [(self.farm.get_pos_x(), self.farm.get_pos_y())]
        infected_count: int = 0
        visited: set[Coords] = set()
        valid: set[Coords] = set()
        while open:
            curr_coords = open.pop()
            if curr_coords in visited:
                continue
            curr = self.farm.get_tile(*curr_coords)
            assert "cactus size" in curr.data
            size: int = curr.data["cactus size"]
            visited.add(curr_coords)
            
            south_coords = coords_in_dir(South, curr_coords)
            north_coords = coords_in_dir(North, curr_coords)
            east_coords = coords_in_dir(East, curr_coords)
            west_coords = coords_in_dir(West, curr_coords)
            tiles_added: list[Coords] = []
            # Check if the neighbor tiles are sorted vs current tile. Only if
            # they are is this considered a valid productive cactus.
            expected = 4
             # Yes this code is a bit of a mess. But it does work.
            if self._acceptable_cactus_coords(south_coords, size, visited, le):
                tiles_added.append(south_coords)
            elif not self.farm.valid_coords(south_coords):
                expected -= 1
            if self._acceptable_cactus_coords(west_coords, size, visited, le):
                tiles_added.append(west_coords)
            elif not self.farm.valid_coords(west_coords):
                expected -= 1
            if self._acceptable_cactus_coords(north_coords, size, visited, ge):
                tiles_added.append(north_coords)
            elif not self.farm.valid_coords(north_coords):
                expected -= 1
            if self._acceptable_cactus_coords(east_coords, size, visited, ge):
                tiles_added.append(east_coords)
            elif not self.farm.valid_coords(east_coords):
                expected -= 1
            if len(tiles_added) < expected:
                continue
            open += tiles_added
            valid.add(curr_coords)
            if curr.infected:
                infected_count += 1
        return valid, infected_count

    def _acceptable_cactus_coords(self, 
                                  coords: Coords, 
                                  curr_size: int,
                                  visited: set[Coords], 
                                  size_condition
                                 ) -> bool:
        # helper for cactus adjacency validation
        if not self.farm.valid_coords(coords):
            return False
        tile = self.farm.get_tile(*coords)
        sized = size_condition(tile.data["cactus size"], curr_size)
        ret = sized and tile.is_grown()
        return ret
        