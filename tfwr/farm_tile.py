from __future__ import annotations
import copy
import random
from tfwr.common import *
from typing import Any

class FarmTile:
    def __init__(self, coords: Coords):
        self.coords = coords
        self.water_level = 0
        self.clear()

    def till(self) -> None:
        if self.grounds == Grounds.Grassland:
            self.grounds = Grounds.Soil
            self.entity = None
            self.companion = None
            self.data = {}
            self.growth_left = 0
            self.infected = False
        else:
            self.clear()

    def plant(self, plant_type: Entities) -> None:
        if plant_type == Entities.Cactus:
            self.data["cactus size"] = random.randint(0, 9)
        elif plant_type == Entities.Sunflower:
            self.data["sunflower petals"] = random.randint(7, 15)
        else:
            self.data = {}
        self.infected = False
        self.entity = plant_type
        if plant_type in PLANT_GROWTH_TIME_SECS:
            time_range = PLANT_GROWTH_TIME_SECS[plant_type]
            self.growth_left = random.uniform(*time_range) * TICKS_PER_SECOND
        else:
            self.growth_left = 0
        self._set_companion()

    def harvest(self) -> Entities|None:
        if self.entity is None or self.growth_left > 0:
            return None
        tmp = self.entity
        if self.grounds == Grounds.Grassland:
            self.entity = Entities.Grass
            self.growth_left = 200
            self._set_companion()
        else:
            self.entity = None
            self.companion = None
        self.data = {}
        self.infected = False
        return tmp

    def clear(self):
        self.grounds: Grounds = Grounds.Grassland
        self.entity: Entities|None = Entities.Grass
        self.data: dict[str, Any] = {}
        self.infected: bool = False
        self.growth_left = 200
        self._set_companion()

    def measure(self) -> Any:
        match self.entity:
            case Entities.Sunflower:
                return self.data["sunflower petals"]
            case Entities.Cactus:
                return self.data["cactus size"]
            case _:
                return None

    def toggle_infection(self) -> None:
        wrong_entity = self.entity == Entities.Hedge or self.entity == Entities.Apple
        if self.entity == None or wrong_entity:
            return
        self.infected = not self.infected

    def get_companion(self) -> tuple[Entities, int, int]|None:
        if self.companion is None:
            return None
        x = self.coords[0] + self.companion[1]
        y = self.coords[1] + self.companion[2]
        return (self.companion[0], x, y)

    def is_grown(self) -> bool:
        return self.entity is not None and self.growth_left <= 0

    def reduce_water_level(self) -> None:
        # The game says there's some randomness but I don't know any details and
        # it seems like it would be extremely difficult to find out how much.
        new_water = self.water_level * 0.99
        if new_water < 0.01:
            new_water = 0
        self.water_level = new_water

    def water(self) -> None:
        self.water_level = min(1, self.water_level + 0.25)

    def to_dense_farm_print(self) -> tuple[str, str]:
        e = "--"
        if self.entity is not None:
            e = entity_to_dense_print(self.entity)
        g = "s" if self.grounds == Grounds.Soil else "g"
        if self.is_grown() and self.entity not in UNHARVESTABLE:
            g += "✓"
        else:
            g += ' '
        return (e, g)

    def to_dense_tile_print(self) -> tuple[str, str]:
        top = ""
        bottom = ""
        if self.growth_left <= 0:
            top = "0 "
        else:
            if self.growth_left / 400 >= 1:
                top = str(self.growth_left / 400)[:2]
            else:
                top = str(self.growth_left / 400)[1:3]
        if self.water_level == 1:
            bottom = "1 "
        elif self.water_level == 0:
            bottom = "  "
        else:
            bottom = str(self.water_level)[1:3]
        if self.infected:
            top = "\033[95m" + top + "\033[0m"
            bottom = "\033[95m" + bottom + "\033[0m"
        return top, bottom

    def get_print(self) -> list[str]:
        width = 10
        if self.entity:
            width = max(width, len(self.entity.name))
        entity_print = "None"
        if self.entity:
            entity_print = self.entity.name
        infected_print = str(self.measure())
        if self.entity == Entities.Pumpkin:
            infected_print = "?"
        if self.infected:
            infected_print += f",infect"
        if self.growth_left < 0:
            self.growth_left = 0
            
        return [
            str(self.coords),
            entity_print,
            self.grounds.name,
            f"{round2(self.growth_left / 400)}s left",
            f"{round2(self.water_level)} water",
            infected_print
        ]

    def _set_companion(self) -> None:
        if self.entity is None or self.entity not in COMPANION_PLANTS:
            self.companion = None
            return
        companion = self.entity
        while companion == self.entity:
            companion = random.choice(COMPANION_PLANTS)
        dx, dy = 0, 0
        while dx == 0 and dy == 0:
            dx = random.randint(-3, 3)
            dy = random.randint(-3, 3)
        self.companion: Companion|None = (companion, dx, dy)

    def __str__(self):
        return "\n".join(self.get_print())