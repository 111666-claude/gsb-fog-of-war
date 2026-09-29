"""战场视野：视野半径、墙体遮挡与增量更新。

口径（README 为准）：
- 目标格与单位之间的连线穿过墙体就不可见；墙格本身可见，门口那一列能看穿。
- 遮挡按「采样连线」判定：线段与墙列（wall_x）至多有一个交点，取交点所在行
  （四舍五入到最近的格子行），该行不是门口 door_y 即被墙体挡住；
  目标在墙列上、或线段根本不穿过墙列时，不受墙体影响。
- update 既加也删：结果等于当前单位集合一次性计算的视野并集；
  单位走开或消失后，只由它贡献的格子随之移除。
"""


def _los_clear(wall_x, door_y, ux, uy, x, y):
    """采样连线：线段 (ux, uy)->(x, y) 与墙列的交点是否落在非门口的墙格上。"""
    du = ux - wall_x
    dt = x - wall_x
    if du == 0 or dt == 0 or (du > 0) == (dt > 0):
        return True
    dx = x - ux
    num = 2 * (uy * dx + (wall_x - ux) * (y - uy)) + dx
    den = 2 * dx
    if den < 0:
        num = -num
        den = -den
    return num // den == door_y


def visible(level, unit):
    """单位当前可见的格子列表（行优先顺序，只含地图内的格子）。"""
    ux = unit["x"]
    uy = unit["y"]
    radius = unit["radius"]
    wall_x = level["wall_x"]
    door_y = level["door_y"]
    x_lo = max(0, ux - radius)
    x_hi = min(level["width"] - 1, ux + radius)
    y_lo = max(0, uy - radius)
    y_hi = min(level["height"] - 1, uy + radius)
    cells = []
    du = ux - wall_x
    if du == 0 or (du > 0 and x_lo > wall_x) or (du < 0 and x_hi < wall_x):
        for y in range(y_lo, y_hi + 1):
            for x in range(x_lo, x_hi + 1):
                cells.append((x, y))
        return cells
    for y in range(y_lo, y_hi + 1):
        dy = y - uy
        for x in range(x_lo, x_hi + 1):
            dt = x - wall_x
            if dt == 0 or (dt > 0) == (du > 0):
                cells.append((x, y))
                continue
            dx = x - ux
            num = 2 * (uy * dx + (wall_x - ux) * dy) + dx
            den = 2 * dx
            if den < 0:
                num = -num
                den = -den
            if num // den == door_y:
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
    """增量更新：既加也删。

    结果等于当前单位集合一次性计算的视野并集；单位走开或消失后，
    只由它贡献的格子随之移除。没有单位时保留既有视野（只剔除地图外的格子）。
    """
    if not units:
        width = level["width"]
        height = level["height"]
        return {(x, y) for (x, y) in previous if 0 <= x < width and 0 <= y < height}
    current = set()
    for unit in units:
        current.update(visible(level, unit))
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
