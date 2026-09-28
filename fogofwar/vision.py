"""战场视野：视野半径、墙体遮挡与增量更新。

缺陷：视野只按距离算（隔墙也能看到）、增量更新只做并集（单位离开后旧视野残留）。
"""


def visible(level, unit):
    """缺陷：只看切比雪夫距离，完全不看墙。"""
    cells = []
    for y in range(level["height"]):
        for x in range(level["width"]):
            if max(abs(x - unit["x"]), abs(y - unit["y"])) <= unit["radius"]:
                cells.append((x, y))
    return cells


def behind_wall_count(level, cells):
    """诊断：有多少「墙后」的格子被标成了可见。"""
    count = 0
    for x, y in cells:
        if x > level["wall_x"] and y != level["door_y"]:
            count += 1
    return count


def update(previous, level, units):
    """缺陷：只把新视野并进来，不删除已经不该可见的格子。"""
    current = set(previous)
    for unit in units:
        current |= set(visible(level, unit))
    return current


def sample_a():
    """9×9 的地图，x=5 有一堵墙，y=4 是门；单位在 (2,4)，视野半径 4。"""
    return {
        "width": 9,
        "height": 9,
        "wall_x": 5,
        "door_y": 4,
        "units": [{"x": 2, "y": 4, "radius": 4}],
    }
