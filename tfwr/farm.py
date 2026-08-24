from __future__ import annotations

import random
from typing import Any

import tfwr.fenwick_tree as fenwick
from tfwr import disjoint_set, harvester, maze, timer
from tfwr.common import *
from tfwr.farm_tile import FarmTile


class Farm:
    def __init__(self, d=None):
        if d is not None:
            for k, v in d.items():
                setattr(self, k, v)
        self.items: dict[Items, float] = {i: 0 for i in Items}
        self.unlocks: dict[Unlocks, int] = {u: 0 for u in Unlocks}
        self.unlocks[Unlocks.Grass] = 1
        self.farm_x: int = 1
        self.farm_y: int = 1
        self.x = 0
        self.y = 0
        self.hat = Hats.Straw_Hat
        self.farm: list[list[FarmTile]] = [[FarmTile((0, 0))]]
        self.current_tile = self.farm[0][0]
        self.harvester = harvester.Harvester(self)
        self.timer = timer.Timer(self)
        self.timer.set_queue()
        self._clear_data()
        self._func_unlocked: set[str] = set()
        self._warning_issued: dict[str, int] = {}
        self._require_func_unlocks = True

    def override_func_unlock_requirements(self) -> None:
        self._require_func_unlocks = False

    def set_unlocks(self, unlocks: dict[Unlocks, int]) -> None:
        self.unlocks = unlocks
        self._update_func_unlocks()
        self._update_size()
        self.timer.update_speed()

    def set_items(self, items: dict[Items, float]) -> None:
        for item, value in items.items():
            if item != Items.Power:
                self.items[item] = int(value)

    def give_unlock(self, unlock: Unlocks) -> None:
        if unlock in self.unlocks:
            if self.unlocks[unlock] == UNLOCK_COUNTS[unlock]:
                raise UnlockError(
                    f"You have already unlocked {unlock} to the maximum level"
                )
            self.unlocks[unlock] += 1
        else:
            self.unlocks[unlock] = 1
        if unlock == Unlocks.Expand:
            self._update_size()
        if unlock == Unlocks.Speed:
            self.timer.update_speed()
        self._update_func_unlocks()

    def add_item(self, item: Items, quantity: float) -> None:
        self.items[item] += quantity

    def get_tile(self, x, y) -> FarmTile:
        return self.farm[y][x]

    def valid_coords(self, coords: Coords) -> bool:
        x_valid = 0 <= coords[0] < self.farm_x
        y_valid = 0 <= coords[1] < self.farm_y
        return x_valid and y_valid

    def wrap_coords(self, coords: Coords) -> Coords:
        return (coords[0] % self.farm_x, coords[1] % self.farm_y)

    # GAME INTERFACE

    def clear(self) -> None:
        if self._require_func_unlocks and "clear" not in self._func_unlocked:
            raise UnlockError("function clear() is not unlocked")
        self.x = 0
        self.y = 0
        self.hat = Hats.Straw_Hat
        self.current_tile = self.farm[0][0]
        for row in self.farm:
            for tile in row:
                tile.clear()
        self._clear_data()
        self.timer.set_queue()
        self.timer.unchecked_ticks += 200
        self.timer.clear_unchecked_ticks()

    def plant(self, plant_type: Entities) -> bool:
        if self._require_func_unlocks and "plant" not in self._func_unlocked:
            raise UnlockError("function plant() is not unlocked")
        tile = self.current_tile
        if self.unlocks[ENTITY_TO_UNLOCK[plant_type]] == 0:
            raise UnlockError(f"{plant_type} is not yet unlocked")
        if plant_type not in PLANTABLE:
            raise EntityTypeError(f"{plant_type} cannot be planted")
        if tile.grounds == Grounds.Grassland and plant_type in REQUIRES_SOIL:
            soil_warning = f"[WARNING]: Cannot plant {plant_type} in Grounds.Grassland"
            self._send_warning(soil_warning)
            self.timer.unchecked_ticks += 1
            return False
        if tile.entity == Entities.Pumpkin and not tile.is_grown():
            self.timer.clear_unchecked_ticks()
        if tile.entity not in [None, Entities.Grass, Entities.Dead_Pumpkin]:
            self.timer.unchecked_ticks += 1
            return False
        cost = self._get_plant_cost(plant_type)
        if not self._spend(cost):
            self.timer.unchecked_ticks += 1
            no_resources = f"[WARNING] Not enough resources to plant {plant_type}"
            self._send_warning(no_resources)
            return False
        tile.plant(plant_type)
        self.timer.add_queue(tile)
        self.timer.unchecked_ticks += 200
        if plant_type == Entities.Sunflower:
            self.harvester.data["sunflower count"] += 1
            sizes = self.harvester.data["sunflower sizes"]
            sizes[tile.measure()].add((self.x, self.y))
        if plant_type == Entities.Pumpkin:
            # 16 to prevent conflicts with sunflowers/cacti
            id = random.randint(16, 2147483647)
            self.data["pumpkin ids"][(self.x, self.y)] = id
        return True

    def change_hat(self, hat: Hats) -> None:
        if self._require_func_unlocks and "change_hat" not in self._func_unlocked:
            raise UnlockError("function change_hat() is not unlocked")
        self.timer.unchecked_ticks += 200
        if hat == Hats.Dinosaur_Hat and self.unlocks[Unlocks.Dinosaurs] == 0:
            dino_hat_req = f"[WARNING] {hat} requires Unlocks.Dinosaurs"
            self._send_warning(dino_hat_req)
            return
        elif hat == Hats.Dinosaur_Hat:
            self._spawn_dino()
        if hat == Hats.Top_Hat and self.unlocks[Unlocks.Top_Hat] == 0:
            top_hat_req = f"[WARNING] {hat} requires Unlocks.Top_Hat"
            self._send_warning(top_hat_req)
            return
        if self.hat == Hats.Dinosaur_Hat:
            self.harvester.dinosaur_harvest()
        self.hat = hat

    def can_harvest(self) -> bool:
        if self._require_func_unlocks and "can_harvest" not in self._func_unlocked:
            raise UnlockError("function can_harvest() is not unlocked")
        tile = self.current_tile
        self.timer.unchecked_ticks += 1
        if not tile.is_grown() and tile.entity not in UNHARVESTABLE:
            self.timer.clear_unchecked_ticks()
        return tile.is_grown() and tile.entity not in UNHARVESTABLE

    def get_world_size(self) -> int:
        if self._require_func_unlocks and "get_world_size" not in self._func_unlocked:
            raise UnlockError("function get_world_size() is not unlocked")
        self.timer.unchecked_ticks += 1
        return self.farm_y

    def till(self) -> None:
        if self._require_func_unlocks and "till" not in self._func_unlocked:
            raise UnlockError("function till() is not unlocked")
        self.timer.unchecked_ticks += 200
        self.current_tile.till()

    def move(self, dir: Direction) -> bool:
        if self._require_func_unlocks and "move" not in self._func_unlocked:
            raise UnlockError("function move() is not unlocked")
        if not self.can_move(dir, internal=True):
            self.timer.unchecked_ticks += 1
            return False
        new_coords = coords_in_dir(dir, (self.x, self.y))
        if self.hat != Hats.Dinosaur_Hat:
            self.x, self.y = self.wrap_coords(new_coords)
            self.current_tile = self.farm[self.y][self.x]
            self.timer.unchecked_ticks += 200
            return True

        # dinosaur movement
        is_apple = self.current_tile.entity == Entities.Apple
        # constant expression for the for loop version given in game
        dino_ticks = int(400 * 0.97 ** len(self.data["dinosaur tail"]))
        self.data["dinosaur tail"].append((self.x, self.y))
        self.data["dinosaur tail set"].add((self.x, self.y))
        self.current_tile.entity = Entities.Dinosaur
        self.x, self.y = new_coords
        self.current_tile = self.farm[self.y][self.x]
        if self.current_tile.grounds != Grounds.Soil:
            self.current_tile.till()
        if is_apple:
            if self.data["next apple coords"] is None:
                next_coords = self._get_next_apple_coords()
                self.data["apple coords"] = next_coords
            else:
                self.data["apple coords"] = self.data["next apple coords"]
                self.data["next apple coords"] = None
            if self.data["apple coords"] is not None:
                new_apple_tile = self.get_tile(*self.data["apple coords"])
                new_apple_tile.clear()
                new_apple_tile.entity = Entities.Apple
                new_apple_tile.grounds = Grounds.Soil
                new_apple_tile.growth_left = 0
                new_apple_tile.companion = None
            elif self.current_tile.entity != Entities.Apple:
                self.data["dinosaur tail"].append((self.x, self.y))
                self.data["dinosaur tail set"].add((self.x, self.y))
        else:
            c = self.data["dinosaur tail"].pop(0)
            self.data["dinosaur tail set"].discard(c)
            self.get_tile(*c).entity = None
        self.timer.unchecked_ticks += dino_ticks
        is_last_apple = len(self.data["dinosaur tail"]) == self.farm_y * self.farm_x - 1
        if self.current_tile.entity == Entities.Apple and is_last_apple:
            self.current_tile.entity = None
            self.data["dinosaur tail"].append((self.x, self.y))
            self.data["dinosaur tail set"].add((self.x, self.y))
        return True

    def get_ground_type(self) -> Grounds:
        if self._require_func_unlocks and "get_ground_type" not in self._func_unlocked:
            raise UnlockError("function get_ground_type() is not unlocked")
        self.timer.unchecked_ticks += 1
        return self.current_tile.grounds

    def get_entity_type(self) -> Entities | None:
        if self._require_func_unlocks and "get_entity_type" not in self._func_unlocked:
            raise UnlockError("function get_entity_type() is not unlocked")
        self.timer.unchecked_ticks += 1
        return self.current_tile.entity

    def get_pos_x(self) -> int:
        if self._require_func_unlocks and "get_pos_x" not in self._func_unlocked:
            raise UnlockError("function get_pos_x() is not unlocked")
        self.timer.unchecked_ticks += 1
        return self.x

    def get_pos_y(self) -> int:
        if self._require_func_unlocks and "get_pos_y" not in self._func_unlocked:
            raise UnlockError("function get_pos_y() is not unlocked")
        self.timer.unchecked_ticks += 1
        return self.y

    def get_water(self) -> float:
        if self._require_func_unlocks and "get_water" not in self._func_unlocked:
            raise UnlockError("function get_water() is not unlocked")
        return round2(self.current_tile.water_level)

    def use_item(self, item: Items, quantity: int = 1) -> bool:
        # Usage fails if:
        # * cannot afford
        # * not a usable item
        # * using Fertilizer in a maze
        # * using Weird Substance on a Hedge
        # * using Weird Substance on a Treasure but not the correct amount
        tile = self.current_tile
        if item not in USABLE_ITEMS:
            raise ItemError(f"{item} is not usable")
        if quantity < 1:
            raise ItemError("You cannot use less than 1 of an item")
        if self.items[item] < quantity:
            self.timer.clear_unchecked_ticks()
            if self.items[item] < quantity:
                self.timer.unchecked_ticks += 1
                no_resources = f"[WARNING] Insufficient resources to use {item}"
                self._send_warning(no_resources)
            return False
        if item == Items.Fertilizer:
            if tile.entity in MAZE_ENTITIES or tile.entity == Entities.Apple:
                self.timer.unchecked_ticks += 1
                return False
            if tile.entity is not None:
                tile.infected = True
            tile.growth_left -= 2 * TICKS_PER_SECOND
        elif item == Items.Weird_Substance:
            return self._use_weird_substance(tile, quantity)
        else:  # use water
            self.timer.clear_unchecked_ticks()
            for i in range(min(quantity, 4)):
                self.current_tile.water()
        assert self._spend({item: quantity})
        self.timer.unchecked_ticks += 200
        return True

    def can_move(self, dir: Direction, internal=False) -> bool:
        not_unlocked = "can_move" not in self._func_unlocked
        if not internal and self._require_func_unlocks and not_unlocked:
            raise UnlockError("function can_move() is not unlocked")
        if not internal:
            self.timer.unchecked_ticks += 1
        e = self.current_tile.entity
        new_coords = coords_in_dir(dir, (self.x, self.y))
        wrapped_coords = self.wrap_coords(new_coords)
        if e in MAZE_ENTITIES:
            if wrapped_coords != new_coords:
                return False
            next_tile = self.get_tile(*new_coords)
            if next_tile.entity not in MAZE_ENTITIES:
                return False
            curr_coords = (self.x, self.y)
            e1 = (curr_coords, new_coords)
            e2 = (new_coords, curr_coords)
            if e1 in self.data["walls"] or e2 in self.data["walls"]:
                return False
        if self.hat == Hats.Dinosaur_Hat:
            if wrapped_coords != new_coords:
                return False
            return new_coords not in self.data["dinosaur tail set"]
        return True

    def get_companion(self) -> tuple[Entities, tuple[int, int]] | None:
        if self._require_func_unlocks and "get_companion" not in self._func_unlocked:
            raise UnlockError("function get_companion() is not unlocked")
        self.timer.unchecked_ticks += 1
        tmp = self.current_tile.get_companion()
        if tmp is None:
            return None
        c = self.wrap_coords((tmp[1], tmp[2]))
        return (tmp[0], c)

    def measure(self, dir: Direction | None = None) -> Any:
        if self._require_func_unlocks and "measure" not in self._func_unlocked:
            raise UnlockError("function measure() is not unlocked")
        self.timer.unchecked_ticks += 1
        if dir:
            coords = self.wrap_coords(coords_in_dir(dir, (self.x, self.y)))
            return self.get_tile(*coords).measure()
        match self.current_tile.entity:
            case Entities.Apple:
                if self.data["next apple coords"] is None:
                    c = self._get_next_apple_coords()
                    self.data["next apple coords"] = c
                return self.data["next apple coords"]
            case Entities.Hedge:
                return self.data["treasure coords"]
            case Entities.Treasure:
                return self.data["next treasure coords"]
            case Entities.Pumpkin:
                coords = (self.x, self.y)
                if coords not in self.data["pumpkins"]:
                    return self.data["pumpkin ids"][coords]
                root_coords = self.data["pumpkins"].find(coords)
                return self.data["pumpkin ids"][root_coords]
            case _:
                return self.current_tile.measure()

    def swap(self, dir: Direction) -> bool:
        if self._require_func_unlocks and "swap" not in self._func_unlocked:
            raise UnlockError("function swap() is not unlocked")
        self.timer.unchecked_ticks += 200
        current = self.current_tile
        other_coords = coords_in_dir(dir, (self.x, self.y))
        if not self.valid_coords(other_coords):
            bounds_swap = "[WARNING] Cannot swap across farm boundaries"
            self._send_warning(bounds_swap)
            return False
        other = self.get_tile(*other_coords)
        current_valid = current.entity is None or current.entity == Entities.Cactus
        other_valid = other.entity is None or other.entity == Entities.Cactus
        if not current_valid:
            swap_error = f"[WARNING] {current.entity} cannot be swapped"
            self._send_warning(swap_error)
            return False
        if not other_valid:
            swap_error = f"[WARNING] {other.entity} cannot be swapped"
            self._send_warning(swap_error)
            return False
        current.data, other.data = other.data, current.data
        current.entity, other.entity = other.entity, current.entity
        return True

    def num_unlocked(self, thing: Unlocks | Items | Entities | Grounds) -> int:
        # Function is not unlock-limited since you can't see unlock levels.
        # Normally requires Unlocks.Senses.
        self.timer.unchecked_ticks += 1
        if isinstance(thing, Grounds):
            return thing == Grounds.Grassland or self.unlocks[Unlocks.Carrots] > 0
        elif isinstance(thing, Entities):
            thing = ENTITY_TO_UNLOCK[thing]
        elif isinstance(thing, Items):
            thing = item_to_unlock(thing)
        return self.unlocks[thing]

    def num_items(self, item: Items, takes_time=True) -> float:
        # Function is not unlock-limited since you can't see item counts.
        # Normally requires Unlocks.Senses.
        if takes_time:
            self.timer.unchecked_ticks += 1
        if item == Items.Power:
            return round2(self.items[item])
        return int(self.items[item])

    def get_cost(
        self, thing: Entities | Unlocks, upgrade_level: int = -1, takes_time=True
    ) -> dict[Items, int] | None:
        # Function is not unlock-limited since there's no visual buyability
        # indicator.
        # Normally requires Unlocks.Costs.
        if takes_time:
            self.timer.unchecked_ticks += 1
        if thing in Unlocks:
            if upgrade_level == -1:
                upgrade_level = self.unlocks[thing]
            if upgrade_level == UNLOCK_COUNTS[thing] + 1 or upgrade_level <= 0:
                return None
            return UNLOCK_COSTS[thing][upgrade_level - 1]
        requirement = ENTITY_TO_UNLOCK[thing]
        if self.unlocks[requirement] == 0:
            raise UnlockError(f"Cannot get cost of {thing}: {requirement} not unlocked")
        if thing == Entities.Treasure or thing == Entities.Hedge:
            base = BASE_PLANT_COSTS[Entities.Treasure]
            upgrades = self.unlocks[Unlocks.Mazes]
            mult = PLANT_COST_MULTS[Entities.Treasure][upgrades - 1]
            return {x: base[x] * mult for x in base}
        return self._get_plant_cost(thing)

    def set_world_size(self, size: int) -> None:
        if self._require_func_unlocks and "set_world_size" not in self._func_unlocked:
            raise UnlockError("function set_world_size() is not unlocked")
        actual_size = EXPAND_SIZES[self.unlocks[Unlocks.Expand]]
        if size < 3 or size > actual_size[0]:
            self._create_blank_farm(*actual_size)
            self.current_tile = self.farm[self.y][self.x]
            self.farm_x, self.farm_y = actual_size
        else:
            self._create_blank_farm(size, size)
            self.current_tile = self.farm[self.y][self.x]
            self.farm_x = size
            self.farm_y = size
        self.x = 0
        self.y = 0
        self.timer.unchecked_ticks += 200

    def unlock(self, unlock: Unlocks) -> bool:
        # Function is not unlock-limited since there's clickable upgrade tree.
        # Normally requires Unlocks.Auto_Unlock.
        prereq = UNLOCK_PREREQS[unlock]
        if prereq is not None and self.unlocks[prereq] == 0:
            unsatisfied_prereq = (
                f"[WARNING] You cannot unlock {unlock}, you need {prereq} first"
            )
            self._send_warning(unsatisfied_prereq)
            self.timer.unchecked_ticks += 1
            return False
        if self.unlocks[unlock] == UNLOCK_COUNTS[unlock]:
            max_unlocked = (
                f"[WARNING] You have already unlocked {unlock} to the maximum level"
            )
            self._send_warning(max_unlocked)
            self.timer.unchecked_ticks += 1
            return False
        cost = self.get_cost(unlock, False)
        assert cost is not None
        if self._spend(cost):
            self.timer.unchecked_ticks += 200
            self.give_unlock(unlock)
            return True
        no_resources = f"[WARNING] You do not have enough resources to unlock {unlock}"
        self._send_warning(no_resources)
        self.timer.unchecked_ticks += 1
        return False

    # INTERNAL IMPLEMENTATION

    def _update_func_unlocks(self) -> None:
        self._func_unlocked = set()
        for f, reqs in FUNC_PREREQS.items():
            for r in reqs:
                if self.unlocks[r[0]] >= r[1]:
                    self._func_unlocked.add(f)

    def _clear_data(self) -> None:
        self.data: dict[str, Any] = {
            "pumpkins": disjoint_set.DisjointSet(),
            "pumpkin sizes": {},
            "pumpkin size locations": {i: set() for i in range(1, 33)},
            "pumpkin prefix": fenwick.FenwickTree(self.farm_x, self.farm_y),
            "pumpkin ids": {},
        }

    def _update_size(self) -> None:
        if self.unlocks[Unlocks.Expand] == 0:
            self.farm = [[FarmTile((0, 0))]]
            return
        new_size = EXPAND_SIZES[self.unlocks[Unlocks.Expand]]
        self.x = 0
        self.y = 0
        self._create_blank_farm(new_size)

    def _create_blank_farm(self, x, y=None) -> None:
        if y is None:
            x, y = x
        self.farm_x = x
        self.farm_y = y
        self.farm = []
        for yy in range(y):
            row = []
            for xx in range(x):
                row.append(FarmTile((xx, yy)))
            self.farm.append(row)
        self.x = 0
        self.y = 0
        self.current_tile = self.farm[0][0]
        self._clear_data()
        self.timer.set_queue()

    def _spend(self, spend_items: dict[Items, float]) -> bool:
        for item, cost in spend_items.items():
            if self.items[item] < cost:
                return False
        for item, quantity in spend_items.items():
            self.items[item] -= quantity
        return True

    def _use_weird_substance(self, tile: FarmTile, quantity: float) -> bool:
        wrong_quantity = f"[WARNING] You used {quantity} Items.Weird_Substance, which isn't exactly the number needed to create a maze"
        cost = self.get_cost(Entities.Treasure, False)
        assert cost is not None
        cost = cost[Items.Weird_Substance]
        wrong_entity = tile.entity == Entities.Hedge or tile.entity == Entities.Apple
        if tile.entity is None or wrong_entity:
            self.timer.unchecked_ticks += 1
            return False
        elif tile.entity == Entities.Treasure:
            return self._reuse_maze(quantity, cost)
        elif quantity < cost:
            self.timer.unchecked_ticks += 200
            if quantity != 1:
                self._send_warning(wrong_quantity)
            self._toggle_infection()
            assert self._spend({Items.Weird_Substance: quantity})
            return True
        elif quantity % cost != 0:
            self._send_warning(wrong_quantity)
        maze.spawn_maze(self, quantity)
        assert self._spend({Items.Weird_Substance: quantity})
        self.timer.unchecked_ticks += 200
        return True

    def _reuse_maze(self, quantity: float, cost: float) -> bool:
        if quantity != self.data["maze size"] * cost:
            self.timer.unchecked_ticks += 1
            return False
        if self.data["times reused"] == 299:
            self.timer.unchecked_ticks += 1
            max_uses = "[WARNING] You have reused the maze the maximum number of times"
            self._send_warning(max_uses)
            # TODO what to do here to properly simulate game
            self.data["treasure coords"] = None
            self.harvester.maze_delete()
            return False
        self.timer.unchecked_ticks += 200
        assert self._spend({Items.Weird_Substance: quantity})
        maze.reuse_maze(self)
        return True

    def _get_plant_cost(self, plant_type: Entities) -> dict[Items, int]:
        if plant_type not in BASE_PLANT_COSTS:
            return {}
        costs = BASE_PLANT_COSTS[plant_type]
        upgrade_track = entity_to_upgrade_track(plant_type)
        if plant_type == Entities.Bush and self.unlocks[Unlocks.Trees] == 0:
            upgrade_track = Unlocks.Plant
        mult = PLANT_COST_MULTS[plant_type][self.unlocks[upgrade_track] - 1]
        return {item: c * mult for item, c in costs.items()}

    def _spawn_dino(self) -> None:
        apple_coords = (self.x, self.y)
        next_coords = self._get_next_apple_coords()
        self.data["dinosaur tail"] = []
        self.data["dinosaur tail set"] = set()
        if next_coords is None:
            return
        apple_tile = self.get_tile(*apple_coords)
        apple_tile.clear()
        apple_tile.entity = Entities.Apple
        apple_tile.grounds = Grounds.Soil
        self.data["apple coords"] = apple_coords
        self.data["next apple coords"] = next_coords

    def _toggle_infection(self) -> None:
        tile = self.current_tile
        tile.toggle_infection()
        for dir in ALL_DIRECTIONS:
            c = coords_in_dir(dir, (self.x, self.y))
            if not self.valid_coords(c):
                continue
            self.get_tile(*c).toggle_infection()

    def _get_next_apple_coords(self):
        spawnable = []
        for row in self.farm:
            for tile in row:
                if self._valid_apple_coords(tile.coords):
                    spawnable.append(tile.coords)
        if len(spawnable) == 0:
            return None
        ret = random.choice(spawnable)
        return ret

    def _valid_apple_coords(self, coords) -> bool:
        if coords == (self.x, self.y):
            return False
        tile = self.get_tile(*coords)
        return tile.entity in [None, Entities.Grass]

    def _send_warning(self, msg: str) -> None:
        warnings = self._warning_issued.get(msg, 0)
        curr_msg = msg
        if warnings == 9:
            curr_msg += " (further warnings suppressed)vaild_coord"
        if warnings < 10:
            print(curr_msg)
            self._warning_issued[msg] = warnings + 1
