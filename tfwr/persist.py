import copy
import json
from typing import Any

import tfwr.fenwick_tree as fenwick
from tfwr import disjoint_set
from tfwr.common import *
from tfwr.farm import Farm
from tfwr.farm_tile import FarmTile

_COORD_KEYS = [
    "apple coords",
    "next apple coords",
    "treasure coords",
    "next treasure coords",
]


def save_game(filepath, farm: Farm, allow_small_farm: bool) -> None:
    repr_json = _farm_to_json(farm, allow_small_farm)
    with open(filepath, "w") as f:
        f.write(json.dumps(repr_json))
        return
    raise FileNotFoundError(f"File {filepath} could not be written to!")


def load_game(filepath) -> Farm:
    with open(filepath) as f:
        repr_json = json.loads(f.read())
        return _farm_from_json(repr_json)
    raise FileNotFoundError(f"File {filepath} not found!")


def _tile_to_json(tile: FarmTile) -> dict[str, Any]:
    repr_json: dict[str, Any] = {}
    if tile.grounds != Grounds.Grassland:
        repr_json["ground"] = "Soil"
    if tile.entity is not None:
        repr_json["entity"] = tile.entity.name
    if tile.companion is not None:
        companion = [tile.companion[0].name, tile.companion[1], tile.companion[2]]
        repr_json["companion"] = companion
    if tile.infected:
        repr_json["infected"] = True
    if tile.data:
        repr_json["data"] = _tile_data_to_json(tile)
    if tile.water_level > 0:
        repr_json["water level"] = tile.water_level
    if tile.growth_left > 0:
        repr_json["growth left"] = tile.growth_left
    return repr_json


def _tile_data_to_json(tile: FarmTile) -> dict[str, Any]:
    return copy.deepcopy(tile.data)


def _farm_to_json(farm: Farm, allow_small_farm: bool) -> dict[str, Any]:
    items = {k.name: v for k, v in farm.items.items()}
    unlocks = {k.name: v for k, v in farm.unlocks.items()}
    farm_tiles = _farm_tiles_to_json(farm, allow_small_farm)
    data = _farm_data_to_json(farm.data)
    repr_json = {
        "items": items,
        "unlocks": unlocks,
        "farm_x": farm.farm_x,
        "farm_y": farm.farm_y,
        "x": farm.x,
        "y": farm.y,
        "hat": farm.hat.name,
        "farm": farm_tiles,
        "data": data,
        "require func unlocks": farm._require_func_unlocks,
    }
    return repr_json


def _farm_data_to_json(data: dict[str, Any]) -> dict[str, Any]:
    repr_json = copy.deepcopy(data)
    repr_json.pop("pumpkin prefix")
    for k in _COORD_KEYS:
        if k in data:
            repr_json[k] = list(data[k])
    if "dinosaur tail" in data:
        tail = [list(coords) for coords in data["dinosaur tail"]]
        repr_json["dinosaur tail"] = tail
    if "walls" in data:
        _maze_data_to_json(data, repr_json)
    _pumpkin_data_to_json(data, repr_json)
    return repr_json


def _maze_data_to_json(data: dict[str, Any], repr_json: dict[str, Any]) -> None:
    def edge_to_list(e):
        return [list(e[0]), list(e[1])]

    # maze size, wall remove counter, and times reused do not require transformation.
    tiles = [list(coords) for coords in data["maze tiles"]]
    repr_json["maze tiles"] = tiles
    walls = [edge_to_list(e) for e in data["walls"]]
    repr_json["walls"] = walls
    walls = [edge_to_list(e) for e in data["possible walls"]]
    repr_json["possible walls"] = walls
    repr_json["treasure coords"] = list(data["treasure coords"])
    repr_json["next treasure coords"] = list(data["next treasure coords"])


def _pumpkin_data_to_json(data: dict[str, Any], repr_json: dict[str, Any]) -> None:
    def tuple_to_str(t):
        return str(t)[1:-1]

    ps = data["pumpkins"]._data
    str_pumpkin = {tuple_to_str(k): tuple_to_str(v) for k, v in ps.items()}
    repr_json["pumpkins"] = str_pumpkin

    sizes_by_coords = {}
    for coords, p_size in data["pumpkin sizes"].items():
        sizes_by_coords[tuple_to_str(coords)] = p_size
    repr_json["pumpkin sizes"] = sizes_by_coords

    coords_by_sizes = {}
    for p_size, coords_set in data["pumpkin size locations"].items():
        coords_by_sizes[p_size] = [tuple_to_str(c) for c in coords_set]
    repr_json["pumpkin size locations"] = coords_by_sizes

    pumpkin_ids = {}
    for coords, id in data["pumpkin ids"].items():
        pumpkin_ids[tuple_to_str(coords)] = id
    repr_json["pumpkin ids"] = pumpkin_ids


def _farm_tiles_to_json(farm: Farm, allow_small: bool) -> list[list[dict[str, Any]]]:
    json_tiles = []
    expected = EXPAND_SIZES[farm.unlocks[Unlocks.Expand]]
    size_mismatch = farm.farm_x != expected[0] or farm.farm_y != expected[1]
    # resets so we don't accidentally save an undersized farm
    if size_mismatch and not allow_small:
        farm._create_blank_farm(expected)
    for y in range(farm.farm_y):
        row = []
        for x in range(farm.farm_x):
            tile = farm.get_tile(x, y)
            tile_json = _tile_to_json(tile)
            row.append(tile_json)
        json_tiles.append(row)
    return json_tiles


def _tile_from_json(repr_json: dict[str, Any], coords: Coords) -> FarmTile:
    t = FarmTile(coords)
    if "ground" in repr_json:
        t.grounds = Grounds.Soil
    if "infected" in repr_json:
        t.infected = True
    if "data" in repr_json:
        t.data = repr_json["data"]
        if "pumpkin root" in t.data:
            t.data["pumpkin root"] = tuple(t.data["pumpkin root"])
    if "entity" in repr_json:
        t.entity = Entities(repr_json["entity"])
    else:
        t.entity = None
    if "companion" in repr_json:
        e, dx, dy = repr_json["companion"]
        t.companion = (Entities(e), dx, dy)
    else:
        t.companion = None
    if "water level" in repr_json:
        t.water_level = repr_json["water level"]
    t.growth_left = repr_json.get("growth left", 0)
    return t


def _farm_from_json(repr_json: dict[str, Any]) -> Farm:
    f = Farm()
    f.items = {Items(k): v for k, v in repr_json["items"].items()}
    unlocks = {Unlocks(k): v for k, v in repr_json["unlocks"].items()}
    f.set_unlocks(unlocks)
    f.farm_x = repr_json["farm_x"]
    f.farm_y = repr_json["farm_y"]
    f.x = repr_json["x"]
    f.y = repr_json["y"]
    f.hat = Hats(repr_json["hat"])
    f.farm = _farm_tiles_from_json(repr_json["farm"])
    f.data = _farm_data_from_json(repr_json["data"])
    _create_pumpkin_prefixes(f)
    f._require_func_unlocks = repr_json["require func unlocks"]
    f.current_tile = f.farm[f.y][f.x]
    f.timer.set_queue()
    f.harvester.set_sunflower_data()
    return f


def _farm_tiles_from_json(
    repr_json: list[list[dict[str, Any]]],
) -> list[list[FarmTile]]:
    farm_tiles: list[list[FarmTile]] = []
    for y in range(len(repr_json)):
        row = []
        for x in range(len(repr_json[0])):
            tile = _tile_from_json(repr_json[y][x], (x, y))
            row.append(tile)
        farm_tiles.append(row)
    return farm_tiles


def _farm_data_from_json(repr_json: dict[str, Any]) -> dict[str, Any]:
    data = {}
    for k in _COORD_KEYS:
        if k in repr_json:
            data[k] = tuple(repr_json[k])
    if "dinosaur tail" in repr_json:
        tail = [tuple(coords) for coords in repr_json["dinosaur tail"]]
        data["dinosaur tail"] = tail
    if "walls" in repr_json:
        _maze_data_from_json(repr_json, data)
    _pumpkin_data_from_json(repr_json, data)
    return data


def _maze_data_from_json(repr_json: dict[str, Any], data: dict[str, Any]) -> None:
    def list_to_edge(l):
        return (tuple(l[0]), tuple(l[1]))

    data["maze size"] = repr_json["maze size"]
    data["wall remove counter"] = repr_json["wall remove counter"]
    data["times reused"] = repr_json["times reused"]
    tiles = {tuple(coords) for coords in repr_json["maze tiles"]}
    data["maze tiles"] = tiles
    walls = {list_to_edge(l) for l in repr_json["walls"]}
    data["walls"] = walls
    walls = {list_to_edge(l) for l in repr_json["possible walls"]}
    data["possible walls"] = walls
    data["treasure coords"] = tuple(repr_json["treasure coords"])
    data["next treasure coords"] = tuple(repr_json["next treasure coords"])


def _pumpkin_data_from_json(repr_json: dict[str, Any], data: dict[str, Any]) -> None:
    def str_to_int_tuple(s):
        return tuple(map(int, s.split(",")))

    ps = repr_json["pumpkins"]
    p_sets = {str_to_int_tuple(k): str_to_int_tuple(v) for k, v in ps.items()}
    data["pumpkins"] = disjoint_set.DisjointSet(p_sets)

    sizes = {}
    for coords, p_size in repr_json["pumpkin sizes"].items():
        sizes[str_to_int_tuple(coords)] = p_size
    data["pumpkin sizes"] = sizes

    locations = {}
    for p_size, coords_list in repr_json["pumpkin size locations"].items():
        locations[p_size] = {str_to_int_tuple(c) for c in coords_list}
    data["pumpkin size locations"] = locations

    pumpkin_ids = {}
    for coords, id in repr_json["pumpkin ids"].items():
        pumpkin_ids[str_to_int_tuple(coords)] = id
    data["pumpkin ids"] = pumpkin_ids


def _create_pumpkin_prefixes(f: Farm) -> None:
    f_tree = fenwick.FenwickTree(f.farm_x, f.farm_y)
    for y in range(f.farm_y):
        for x in range(f.farm_x):
            tile = f.get_tile(x, y)
            if tile.entity == Entities.Pumpkin and tile.is_grown():
                f_tree.add(x, y, 1)
    f.data["pumpkin prefix"] = f_tree
