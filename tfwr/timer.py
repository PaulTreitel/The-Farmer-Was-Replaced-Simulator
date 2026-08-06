import time
from tfwr.common import *
import random
from tfwr.farm_tile import FarmTile
from tfwr.disjoint_set import DisjointSet

# Overall strategy:
# When functions are called, we add unchecked ticks. These are the raw original
# tick speeds (e.g., 200 for a `move()`) before speed upgrades and power. On
# functions where the user requires up-to-date information, the unchecked 
# ticks can be cleared and the farm is updated to its new state.



TICKS_SPEEDUP_PER_POWER = 6000

class Timer:
    def __init__(self, farm):
        from tfwr.farm import Farm
        self.farm: Farm = farm
        self._ticks: Numeric = 0
        self.unchecked_ticks: Numeric = 0
        self._last_water_second: int = 0
        self.growth_queue: dict[FarmTile, tuple[Numeric, Numeric]] = {}
        self.water_queue: set[FarmTile] = set()
        self.update_speed()

    def get_time(self) -> float:
        return round2(self._ticks / TICKS_PER_SECOND)

    def get_tick_count(self) -> float:
        return round2(self._ticks)

    def clear_unchecked_ticks(self) -> None:
        if self.unchecked_ticks == 0:
            return
        tick_div = self._speed
        power = self.farm.num_items(Items.Power, False)
        if power > 0:
            power_used = self.unchecked_ticks / TICKS_SPEEDUP_PER_POWER
            tick_div *= 2
            # Technically you shouldn't be able to fully speed up if you don't
            # have enough power for the whole time, but I'm not fixing it.
            self.farm.add_item(Items.Power, -min(power_used, power))
        real_ticks = self.unchecked_ticks / tick_div
        self._update_queue_ticks(tick_div)
        self.unchecked_ticks = 0
        self._ticks += real_ticks
        self._update_farm(real_ticks)

    def set_execution_speed(self, value: float) -> None:
        self._speed = value

    def update_speed(self) -> None:
        self.clear_unchecked_ticks()
        self._speed = SPEED_MULTS[self.farm.unlocks[Unlocks.Speed]]

    def add_real_ticks(self, ticks: int) -> None:
        self._ticks += ticks
        self._update_farm(ticks)

    def set_queue(self) -> None:
        self.growth_queue = {}
        self.water_queue = set()
        for y in range(self.farm.farm_y):
            for x in range(self.farm.farm_x):
                self.add_queue(self.farm.get_tile(x, y))

    def add_queue(self, tile: FarmTile) -> None:
        if tile.water_level > 0:
            self.water_queue.add(tile)
        if tile.entity is not None and tile.growth_left > 0:
            # We have to record the time when the plant is planted (or at least
            # last updated) so that if we update the farm after an extended
            # period we don't update it as if it had been around the whole time.
            self.growth_queue[tile] = (self._ticks, self.unchecked_ticks)

    def remove_queue(self, tile: FarmTile) -> None:
        # Water queue is only updated and removed within this class.
        self.growth_queue.pop(tile, None)

    def _update_farm(self, real_ticks: float) -> None:
        real_seconds = real_ticks / TICKS_PER_SECOND
        self._add_water(real_seconds)
        self._add_fertilizer(real_seconds)

        remove = []
        for tile, planted_ticks in self.growth_queue.items():
            self._grow_plant(tile, real_ticks, planted_ticks)
            self.growth_queue[tile] = (self._ticks, 0)
            if tile.is_grown():
                remove.append(tile)
        for tile in remove:
            self.growth_queue.pop(tile, None)

        if self.farm.unlocks[Unlocks.Watering] > 0:
            while self._ticks // TICKS_PER_SECOND > self._last_water_second:
                self._last_water_second += 1
                self._reduce_water_levels()

    def _grow_plant(self, 
                    tile: FarmTile, 
                    real_ticks: float, 
                    planted_ticks: tuple[Numeric, Numeric]
                   ) -> None:
        true_real_ticks = self._ticks - planted_ticks[0] 
        new_growth = true_real_ticks * (1 + 4 * tile.water_level)
        if tile.entity == Entities.Tree:
            x, y = tile.coords
            n_coords = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            for n in n_coords:
                if not self.farm.valid_coords(n):
                    continue
                if self.farm.get_tile(*n).entity == Entities.Tree:
                    new_growth /= 2
        tile.growth_left -= new_growth
        if tile.entity == Entities.Pumpkin and tile.is_grown():
            if random.random() < 0.2:
                tile.entity = Entities.Dead_Pumpkin
            else:
                self._merge_pumpkin(tile.coords)

    def _reduce_water_levels(self) -> None:
        rem = []
        for tile in self.water_queue:
            tile.reduce_water_level()
            if tile.water_level == 0:
                rem.append(tile)
        for tile in rem:
            self.water_queue.discard(tile)

    def _add_water(self, real_seconds: float) -> None:
        level = self.farm.unlocks[Unlocks.Watering]
        water_added = real_seconds * WATER_PER_SECOND[level - 1]
        # This adds a non-integer amount of water but the user only receives
        # an integer value from num_items() (save for Power) and spending
        # can only be done in integer increments so it's actually fine.
        self.farm.add_item(Items.Water, water_added)

    def _add_fertilizer(self, real_seconds: float) -> None:
        level = self.farm.unlocks[Unlocks.Fertilizer]
        fetilizer_added = real_seconds * FERTILIZER_PER_SECOND[level - 1]
        self.farm.add_item(Items.Fertilizer, fetilizer_added)

    def _update_queue_ticks(self, tick_div) -> None:
        for tile, (plant_real, plant_unchecked) in self.growth_queue.items():
            new_real = plant_real + plant_unchecked / tick_div
            self.growth_queue[tile] = (new_real, 0)

    
    # PUMPKIN MERGING

    
    def _merge_pumpkin(self, coords: Coords) -> None:
        self._update_new_pumpkin(coords)
        best = None
        max_size = min(self.farm.farm_x, self.farm.farm_y)
        for size in range(max_size, 1, -1):
            left, right, top, bottom = self._get_search_bounds(coords, size)
            found = False
            for y_start in range(bottom, top + 1):
                for x_start in range(left, right + 1):
                    new = (x_start, y_start, size)
                    if not self._square_full(*new):
                        continue
                    if self._check_pumpkin_bounds(new):
                        continue
                    best = new
                    found = True
                    break
                if found:
                    break
            if found:
                break
        if best:
            self._apply_pumpkin_merge(*best)
            p_extents = self.farm.data["pumpkin sizes"]
            p_size_extents = self.farm.data["pumpkin size locations"]
            p_extents[(best[0], best[1])] = best[2]
            p_size_extents[best[2]].add((best[0], best[1]))

    def _update_new_pumpkin(self, coords: Coords) -> None:
        subsets = self.farm.data["pumpkins"]
        p_extents = self.farm.data["pumpkin sizes"]
        p_size_extents = self.farm.data["pumpkin size locations"]
        subsets.add(coords)
        p_extents[coords] = 1
        if 1 not in p_size_extents:
            p_size_extents[1] = set()
        p_size_extents[1].add(coords)
        self.farm.data["pumpkin prefix"].add(*coords, 1)

    def _get_search_bounds(self, 
                           coords: Coords, 
                           size: int
                          ) -> tuple[int, int, int, int]:
        px, py = coords
        left = max(0, px - size + 1)
        right = min(px, self.farm.farm_x - size)
        bottom = max(0, py - size + 1)
        top = min(py, self.farm.farm_y - size)
        left, right = self._bound_search_row(coords, left, right)
        top, bottom = self._bound_search_col(coords, top, bottom)
        for y in range(bottom, top + 1):
            new_coords = (coords[0], y)
            new_left, new_right = self._bound_search_row(new_coords, left, right)
            right = min(right, new_right)
            left = max(left, new_left)
        for x in range(left, right + 1):
            new_coords = (x, coords[1])
            new_top, new_bottom = self._bound_search_col(new_coords, top, bottom)
            top = min(top, new_top)
            bottom = max(bottom, new_bottom)
        return left, right, top, bottom

    def _bound_search_row(self, 
                          c: Coords, 
                          left: int, 
                          right: int
                         ) -> tuple[int, int]:
        for x in range(c[0] - 1, left, -1):
            tile = self.farm.get_tile(x, c[1])
            if tile.entity != Entities.Pumpkin or tile.growth_left > 0:
                left = x
                break
        for x in range(c[0], right):
            tile = self.farm.get_tile(x, c[1])
            if tile.entity != Entities.Pumpkin or tile.growth_left > 0:
                right = x
                break
        return left, right

    def _bound_search_col(self, 
                          c: Coords, 
                          top: int, 
                          bottom: int
                         ) -> tuple[int, int]:
        for y in range(c[1] - 1, bottom, -1):
            tile = self.farm.get_tile(c[0], y)
            if tile.entity != Entities.Pumpkin or tile.growth_left > 0:
                bottom = y
                break
        for y in range(c[1], top):
            tile = self.farm.get_tile(c[0], y)
            if tile.entity != Entities.Pumpkin or tile.growth_left > 0:
                top = y
                break
        return top, bottom

    def _check_pumpkin_bounds(self, new_p: tuple[int, int, int]) -> bool:
        pumpkin_sets = self.farm.data["pumpkin size locations"]
        right_x = new_p[0] + new_p[2] - 1
        top_y = new_p[1] + new_p[2] - 1
        new_corners = [
            (new_p[0], new_p[1]), 
            (right_x, new_p[1]), 
            (new_p[0], top_y), 
            (right_x, top_y)
        ]
        def old_in_new_square(c: Coords) -> bool:
            return new_p[0] <= c[0] <= right_x and new_p[1] <= c[1] <= top_y

        def new_in_old_square(c: Coords, square: tuple[int, int, int]) -> bool:
            right = square[0] + square[2] - 1
            top = square[1] + square[2] - 1
            return square[0] <= c[0] <= right and square[1] <= c[1] <= top

        for i in range(2, 32):
            # For each possible pumpkin size, go through each pumpkin and check
            # if the new pumpkin square and the old one overlap.
            if len(pumpkin_sets[i]) == 0:
                continue
            for (x, y) in pumpkin_sets[i]:
                if x > right_x or x + i - 1 < new_p[0]:
                    continue
                if y > top_y or y + i - 1 < new_p[1]:
                    continue
                corners = [
                    (x, y), 
                    (x + i - 1, y), 
                    (x, y + i - 1), 
                    (x + i - 1, y + i - 1)
                ]
                s = (x, y, i)
                c_inside = [old_in_new_square(c) for c in corners]
                fully_inside = sum(c_inside) == 4
                if 0 < sum(c_inside) < 4:
                    return True
                c_inside = [new_in_old_square(c, s) for c in new_corners]
                # If the old square is fully inside the new one and they share
                # one corner, then it's a valid new pumpkin. This caused 
                # substantial pain.
                if sum(c_inside) == 1 and fully_inside:
                    continue
                if 0 < sum(c_inside) < 4:
                    return True
        return False
        

    def _square_full(self, x: int, y: int, size: int) -> bool:
        count = self.farm.data["pumpkin prefix"].rect(x, y, x + size, y + size)
        return count == size**2

    def _apply_pumpkin_merge(self, x_start: int, y_start: int, size: int) -> None:
        subsets = self.farm.data["pumpkins"]
        p_extents = self.farm.data["pumpkin sizes"]
        p_size_extents = self.farm.data["pumpkin size locations"]
        assert isinstance(subsets, DisjointSet)
        for x in range(x_start, x_start + size):
            for y in range(y_start, y_start + size):
                s = p_extents.pop((x, y), None)
                if s is not None:
                    p_size_extents[s].discard((x, y))
                if (x, y) in subsets:
                    subsets.merge((x_start, y_start), (x, y))
