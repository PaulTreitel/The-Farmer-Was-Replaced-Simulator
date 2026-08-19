from typing import Any

from tfwr.common import Coords, Entities, Grounds, Unlocks, round2
from tfwr.disjoint_set import DisjointSet
from tfwr.farm import Farm

VBAR = "│"
HBAR = "─"
FOURWAY = "┼"
LEFT_TEE = "├"
RIGHT_TEE = "┤"
TEE = "┬"
DOWN_TEE = "┴"
DOWN_RIGHT = "┌"
DOWN_LEFT = "┐"
UP_RIGHT = "└"
UP_LEFT = "┘"


def print_entities_internal(farm: Farm) -> None:
    longest = [4 for i in range(farm.farm_x)]
    for y in range(farm.farm_y - 1, -1, -1):
        for x in range(farm.farm_x):
            tile = farm.get_tile(x, y)
            if tile.entity is None:
                continue
            longest[x] = max(longest[x], len(tile.entity.name))

    top_spacer, spacer, bottom_spacer = _get_dynamic_spacers(farm, longest)
    x_legend_digits = [f"{i}".ljust(longest[i] + 1) for i in range(farm.farm_x)]
    x_legend = "    " + "".join(x_legend_digits)
    if farm.farm_y > 16:
        print(x_legend)
    print(top_spacer)
    for y in range(farm.farm_y - 1, -1, -1):
        str = f"{y}".rjust(2) + VBAR
        for x in range(farm.farm_x):
            tile = farm.get_tile(x, y)
            new_entity = ""
            if tile.entity:
                new_entity = tile.entity.name.center(longest[x]) + f"{VBAR}"
            else:
                new_grounds = "None".center(longest[x]) + f"{VBAR}"
            if tile.coords == (farm.x, farm.y):
                new_grounds = new_grounds.upper()
            str += new_entity
        print(str)
        if y == 0:
            print(bottom_spacer)
        else:
            print(spacer)
    print(x_legend)


def print_grounds_internal(farm: Farm) -> None:
    longest = [4 for i in range(farm.farm_x)]
    for y in range(farm.farm_y - 1, -1, -1):
        for x in range(farm.farm_x):
            tile = farm.get_tile(x, y)
            if tile.grounds == Grounds.Grassland:
                longest[x] = 5

    top_spacer, spacer, bottom_spacer = _get_dynamic_spacers(farm, longest)
    x_legend_digits = [f"{i}".ljust(longest[i] + 1) for i in range(farm.farm_x)]
    x_legend = "    " + "".join(x_legend_digits)
    if farm.farm_y > 16:
        print(x_legend)
    print(top_spacer)
    for y in range(farm.farm_y - 1, -1, -1):
        str = f"{y}".rjust(2) + f"{VBAR}"
        for x in range(farm.farm_x):
            tile = farm.get_tile(x, y)
            new_grounds = ""
            if tile.grounds == Grounds.Grassland:
                new_grounds = f"GLand{VBAR}"
            else:
                new_grounds = "Soil".ljust(longest[x]) + VBAR
            if tile.coords == (farm.x, farm.y):
                new_grounds = new_grounds.upper()
            str += new_grounds
        print(str)
        if y == 0:
            print(bottom_spacer)
        else:
            print(spacer)
    print(x_legend)


def print_tile_internal(farm: Farm, x, y=None) -> None:
    if y is None:
        x, y = x
    lines = farm.get_tile(x, y).get_print()
    width = max(len(l) for l in lines)
    top_spacer = DOWN_RIGHT + HBAR * (width + 2) + DOWN_LEFT
    bottom_spacer = UP_RIGHT + HBAR * (width + 2) + UP_LEFT
    print(top_spacer)
    for line in lines:
        print(VBAR + " " + line.ljust(width) + " " + VBAR)
    print(bottom_spacer)


def print_dense_farm_internal(farm: Farm) -> None:
    top_spacer, spacer, bottom_spacer = _get_spacers(farm)
    x_legend = _get_legend(farm)
    if farm.farm_y > 16:
        print(x_legend)
    print(top_spacer)
    for y in range(farm.farm_y - 1, -1, -1):
        top = "  " + VBAR
        bottom = f"{y}".center(2) + VBAR
        for c in range(farm.farm_x):
            tile = farm.get_tile(c, y)
            t, b = tile.to_dense_farm_print()
            if tile.coords == (farm.x, farm.y):
                t, b = t.upper(), b.upper().replace("✓", "✔")
            top += t + VBAR
            bottom += b + VBAR
        if y == 0:
            print(f"{top}\n{bottom}\n{bottom_spacer}")
        else:
            print(f"{top}\n{bottom}\n{spacer}")
    print(x_legend)


def print_dense_tile_data_internal(farm: Farm) -> None:
    top_spacer, spacer, bottom_spacer = _get_spacers(farm)
    x_legend = _get_legend(farm)
    if farm.farm_y > 16:
        print(x_legend)
    print(top_spacer)
    for y in range(farm.farm_y - 1, -1, -1):
        top = "  " + VBAR
        bottom = f"{y}".center(2) + VBAR
        for x in range(farm.farm_x):
            tile = farm.get_tile(x, y)
            t, b = tile.to_dense_tile_print()
            top += t + VBAR
            bottom += b + VBAR
        if y == 0:
            print(f"{top}\n{bottom}\n{bottom_spacer}")
        else:
            print(f"{top}\n{bottom}\n{spacer}")
    print(x_legend)


def print_dense_measure_internal(farm: Farm) -> None:
    top_spacer, spacer, bottom_spacer = _get_spacers(farm)
    x_legend = _get_legend(farm)
    if farm.farm_y > 16:
        print(x_legend)
    print(top_spacer)
    for y in range(farm.farm_y - 1, -1, -1):
        top = "  " + VBAR
        bottom = f"{y}".center(2) + VBAR
        for c in range(farm.farm_x):
            tile = farm.get_tile(c, y)
            m = tile.measure()
            new_top, new_bottom = _measure_to_print(m)
            top += new_top
            bottom += new_bottom
        if y == 0:
            print(f"{top}\n{bottom}\n{bottom_spacer}")
        else:
            print(f"{top}\n{bottom}\n{spacer}")
    print(x_legend)


def _measure_to_print(m: Any) -> tuple[str, str]:
    top, bottom = "", ""
    if m is None:
        top = "  " + VBAR
        bottom = "  " + VBAR
    elif isinstance(m, int):
        if m > 15:
            top = "??" + VBAR
        else:
            top = str(m).ljust(2) + VBAR
        bottom = "  " + VBAR
    elif isinstance(m, tuple):
        top = str(m[0]).ljust(2) + VBAR
        bottom = str(m[1]).ljust(2) + VBAR
    else:
        top = "??" + VBAR
        bottom = "??" + VBAR
    return top, bottom


def _add_tile_prints_to_lists(
    tile_prints: list[str], existing: list[str], width: int
) -> None:
    if len(existing[-1]) == 0:
        if tile_prints[0] == "(0, 0)":
            hsep = UP_RIGHT + HBAR * (width + 2)
        else:
            hsep = LEFT_TEE + HBAR * (width + 2)
    elif "(0, 0)" in existing[0]:
        hsep = DOWN_TEE + HBAR * (width + 2)
    else:
        hsep = FOURWAY + HBAR * (width + 2)
    for i, print_row in enumerate(tile_prints):
        existing[i] += print_row.ljust(width) + f" {VBAR} "
    existing[-1] += hsep


def print_full_internal(farm: Farm) -> None:
    # Collect all the content text for each tile and how wide each column needs to be.
    tile_prints: list[list[list[str]]] = []
    lengths = [0 for _ in range(farm.farm_x)]
    for y in range(farm.farm_y):
        row_print: list[list[str]] = []
        for x in range(farm.farm_x):
            prints = farm.get_tile(x, y).get_print()
            row_print.append(prints)
            longest = max(len(p) for p in prints)  # entity text
            lengths[x] = max(lengths[x], longest)  # growth text
        tile_prints.append(row_print)

    # Combine the content text for each row and add visual separators
    final_tile_prints: list[list[str]] = []
    for y, tile_row_print in enumerate(tile_prints):
        print_rows: list[str] = [VBAR + " " for _ in tile_row_print[0]]
        print_rows.append("")  # for the horizontal separator
        for x, tile_print in enumerate(tile_row_print):
            _add_tile_prints_to_lists(tile_print, print_rows, lengths[x])
        if y == 0:
            print_rows[-1] += UP_LEFT
        else:
            print_rows[-1] += RIGHT_TEE
        final_tile_prints.append(print_rows)
    # final horizontal separator, prints at the top
    top_hsep = final_tile_prints[0][-1]
    top_hsep = top_hsep.replace(DOWN_TEE, TEE)
    top_hsep = top_hsep.replace(UP_RIGHT, DOWN_RIGHT)
    top_hsep = top_hsep.replace(UP_LEFT, DOWN_LEFT)
    final_tile_prints.append([top_hsep])
    for p in final_tile_prints[::-1]:
        for line in p:
            print(line)


def quantity_to_display(n: float) -> str:
    # I'm not bothering with doing trillion+ formatting (I don't know if it's
    # even there).
    if n < 10**3:
        if n % 1 != 0:
            n = round2(n)
        return str(n)
    postfix = ""
    if n >= 10**9:
        postfix = "B"
    elif n >= 10**6:
        postfix = "M"
    elif n >= 10**3:
        postfix = "k"
    while n >= 1000:
        n /= 1000
    n = int(n * 10) / 10
    if n % 1 == 0:
        n = int(n)
    return str(n) + postfix


def print_maze_internal(farm: Farm) -> None:
    if "walls" not in farm.data:
        farm._send_warning("[WARNING] There is no maze to print")
        return
    walls = farm.data["walls"]
    top_spacer, _, bottom_spacer = _get_spacers(farm)
    x_legend = _get_legend(farm)
    lines: list[str] = [top_spacer]
    if farm.farm_y > 16:
        lines = [x_legend, top_spacer]
    for y in range(farm.farm_y - 1, -1, -1):
        center = f"{y}".ljust(2) + VBAR
        bottom = "  " + LEFT_TEE
        for x in range(farm.farm_x):
            new_center, new_bottom = _maze_get_tile_print((x, y), walls)
            center += new_center
            bottom += new_bottom
        bottom = bottom[:-1] + RIGHT_TEE
        lines.extend([center, bottom])
    lines[-1] = bottom_spacer
    lines.append(x_legend)
    print("\n".join(lines))


def _maze_get_tile_print(
    coords: Coords, walls: set[tuple[Coords, Coords]]
) -> tuple[str, str]:
    center = "  "
    bottom = ""
    right = (coords[0] + 1, coords[1])
    down = (coords[0], coords[1] - 1)
    right_e1, right_e2 = (coords, right), (right, coords)
    down_e1, down_e2 = (coords, down), (down, coords)
    wall_right = right_e1 in walls or right_e2 in walls
    wall_down = down_e1 in walls or down_e2 in walls
    if wall_right:
        center += VBAR
    else:
        center += " "
    if wall_down:
        bottom += HBAR * 2 + "+"
    elif wall_right:
        bottom += "  +"
    else:
        bottom += "  +"
    return center, bottom


def print_pumpkin_bounds(farm: Farm) -> None:
    subsets = farm.data["pumpkins"]
    assert isinstance(subsets, DisjointSet)
    top_spacer, _, bottom_spacer = _get_spacers(farm)
    x_legend = "   " + "".join([f"{i}".ljust(3) for i in range(farm.farm_x)])
    lines: list[str] = [top_spacer]
    if farm.farm_y > 16:
        lines = [x_legend, top_spacer]
    for y in range(farm.farm_y - 1, -1, -1):
        top = "  " + VBAR
        center = f"{y}".ljust(2) + VBAR
        bottom = "  " + LEFT_TEE
        for x in range(farm.farm_x):
            top_symbol, center_symbol = _pumpkin_get_symbol(farm, (x, y))
            new_top, new_center, new_bottom = _pumpkin_get_borders((x, y), subsets)
            top += top_symbol + new_top
            center += center_symbol + new_center
            bottom += new_bottom
        bottom = bottom[:-1] + RIGHT_TEE
        lines.extend([top, center, bottom])
    lines[-1] = bottom_spacer
    lines.append(x_legend)
    print("\n".join(lines))


def _pumpkin_get_symbol(farm: Farm, coords: Coords) -> tuple[str, str]:
    tile = farm.get_tile(*coords)
    if tile.entity == Entities.Pumpkin:
        top = "  " if tile.growth_left <= 0 else "gr"
        center = "  " if tile.growth_left <= 0 else "wg"
    else:
        top = "╲╱"
        center = "╱╲"
    return top, center


def _pumpkin_get_borders(coords: Coords, subsets: DisjointSet) -> tuple[str, str, str]:
    top = ""
    center = ""
    bottom = ""
    right = (coords[0] + 1, coords[1])
    down = (coords[0], coords[1] - 1)
    if coords not in subsets:
        return VBAR, VBAR, HBAR * 2 + "+"
    if right in subsets and subsets.connected(coords, right):
        center += " "
        top += " "
    else:
        center += VBAR
        top += VBAR
    if down in subsets and subsets.connected(coords, down):
        if right in subsets and subsets.connected(coords, right):
            bottom += "   "
        else:
            bottom += "  +"
    else:
        bottom += HBAR * 2 + "+"
    return top, center, bottom


def print_items(farm: Farm) -> None:
    print()
    item_strs = []
    for item, quantity in farm.items.items():
        # Maximum item name is 15 characters. Giving 25 characters for number
        # plus a colon and extra space. On an 80-character wide terminal that's
        # 3 items/row.
        s = f"{item.name}: {quantity_to_display(quantity)}".ljust(18)
        item_strs.append(s)
    for i in range(0, len(item_strs), 3):
        # matching the spacing of the items printout
        if i + 3 < len(item_strs):
            line = "".join(item_strs[i : i + 2]) + "  " + item_strs[i + 2]
        else:
            line = "".join(item_strs[i : i + 2])
        print(line)


def print_unlocks(farm: Farm) -> None:
    # This looks very ugly and yes it hardcodes everything but it makes it easy
    # to have them ordered correctly. They are ordered by a BFS through the
    # upgrade tree.
    l = farm.unlocks[Unlocks.Loops]
    h = farm.unlocks[Unlocks.Hats]
    s = farm.unlocks[Unlocks.Speed]
    g = farm.unlocks[Unlocks.Grass]
    print(f"Loops: {l}          Hats: {h}             Speed: {s}           Grass: {g}")
    e = farm.unlocks[Unlocks.Expand]
    p = farm.unlocks[Unlocks.Plant]
    c = farm.unlocks[Unlocks.Carrots]
    d = farm.unlocks[Unlocks.Debug]
    print(
        f"Expand: {e}         Plant: {p}            Carrots: {str(c).ljust(2)}        Debug: {d}"
    )
    o = farm.unlocks[Unlocks.Operators]
    w = farm.unlocks[Unlocks.Watering]
    t = farm.unlocks[Unlocks.Trees]
    d = farm.unlocks[Unlocks.Debug_2]
    print(
        f"Operators: {o}      Watering: {w}         Trees: {str(t).ljust(2)}          Debug_2: {d}"
    )
    t = farm.unlocks[Unlocks.Timing]
    s = farm.unlocks[Unlocks.Senses]
    v = farm.unlocks[Unlocks.Variables]
    f = farm.unlocks[Unlocks.Fertilizer]
    print(
        f"Timing: {t}         Senses: {s}           Variables: {v}       Fertilizer: {f}"
    )
    s = farm.unlocks[Unlocks.Sunflowers]
    p = farm.unlocks[Unlocks.Pumpkins]
    s2 = farm.unlocks[Unlocks.Simulation]
    l = farm.unlocks[Unlocks.Lists]
    print(
        f"Sunflowers: {s}     Pumpkins: {str(p).ljust(2)}        Simulation: {s2}      Lists: {l}"
    )
    f = farm.unlocks[Unlocks.Functions]
    m = farm.unlocks[Unlocks.Mazes]
    c = farm.unlocks[Unlocks.Cactus]
    p = farm.unlocks[Unlocks.Polyculture]
    print(
        f"Functions: {f}      Mazes: {m}            Cactus: {c}          Polyculture: {p}"
    )
    l = farm.unlocks[Unlocks.Leaderboard]
    d = farm.unlocks[Unlocks.Dictionaries]
    i = farm.unlocks[Unlocks.Import]
    u = farm.unlocks[Unlocks.Utilities]
    print(
        f"Leaderboard: {l}    Dictionaries: {d}     Import: {i}          Utilities: {u}"
    )
    t = farm.unlocks[Unlocks.Top_Hat]
    m = farm.unlocks[Unlocks.Megafarm]
    d = farm.unlocks[Unlocks.Dinosaurs]
    c = farm.unlocks[Unlocks.Costs]
    print(f"Top_Hat: {t}        Megafarm: {m}         Dinosaurs: {d}       Costs: {c}")
    q = farm.unlocks[Unlocks.Question_Mark]
    a = farm.unlocks[Unlocks.Auto_Unlock]
    print(f"?: {q}              Auto_Unlock: {a}")


def _get_spacers(farm: Farm) -> tuple[str, str, str]:
    top_spacer_start = f"  {DOWN_RIGHT}" + HBAR * 2
    spacer_start = f"  {LEFT_TEE}" + HBAR * 2
    bottom_spacer_start = f"  {UP_RIGHT}" + HBAR * 2
    top_spacer_core = (TEE + HBAR * 2) * (farm.farm_x - 1)
    spacer_core = (FOURWAY + HBAR * 2) * (farm.farm_x - 1)
    bottom_spacer_core = (DOWN_TEE + HBAR * 2) * (farm.farm_x - 1)

    top_spacer = top_spacer_start + top_spacer_core + DOWN_LEFT
    spacer = spacer_start + spacer_core + RIGHT_TEE
    bottom_spacer = bottom_spacer_start + bottom_spacer_core + UP_LEFT
    return top_spacer, spacer, bottom_spacer


def _get_dynamic_spacers(farm: Farm, lengths: list[int]) -> tuple[str, str, str]:
    top_spacer_start = f"  {DOWN_RIGHT}" + HBAR * lengths[0]
    spacer_start = f"  {LEFT_TEE}" + HBAR * lengths[0]
    bottom_spacer_start = f"  {UP_RIGHT}" + HBAR * lengths[0]
    top_spacer_core = ""
    spacer_core = ""
    bottom_spacer_core = ""
    for l in lengths[1:]:
        tmp = HBAR * l
        top_spacer_core += TEE + tmp
        spacer_core += FOURWAY + tmp
        bottom_spacer_core += DOWN_TEE + tmp
    top_spacer = top_spacer_start + top_spacer_core + DOWN_LEFT
    spacer = spacer_start + spacer_core + RIGHT_TEE
    bottom_spacer = bottom_spacer_start + bottom_spacer_core + UP_LEFT
    return top_spacer, spacer, bottom_spacer


def _get_legend(farm: Farm) -> str:
    return "   " + "".join([f"{i}".ljust(3) for i in range(farm.farm_x)])
