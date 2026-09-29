"""战场视野：视野半径、墙体遮挡与增量更新。

口径：
- 视线遮挡：目标格与单位之间逐条采样连线，途经墙格（wall_x 列、非门口行）则不可见；
  墙格本身作为目标时可见，门口格（door_y 行）可以看穿。
- 增量更新既加也删：单位走开或消失后，只由它贡献的格子从视野里移除。
- 每格判定与逐格暴力扫描的参考实现完全一致，重复计算结果相同。
"""


def _is_wall(level, x, y):
    """墙格：x 落在墙列且不在门口行。"""
    return x == level["wall_x"] and y != level["door_y"]


def _sampled_los_clear(level, ux, uy, tx, ty):
    """逐条采样连线：从 (ux, uy) 到 (tx, ty) 均匀采样（不含两端点），
    任一采样点落在墙格上则不可见。两端点不参与判定，所以墙格本身可见。"""
    wall_x = level["wall_x"]
    door_y = level["door_y"]
    dx = tx - ux
    dy = ty - uy
    steps = max(abs(dx), abs(dy))
    for i in range(1, steps):
        t = i / steps
        cx = int(ux + dx * t + 0.5)
        cy = int(uy + dy * t + 0.5)
        if cx == wall_x and cy != door_y:
            return False
    return True


def _los_clear(level, ux, uy, tx, ty):
    """与 _sampled_los_clear 结果一致的快速通道：
    线段两端都在墙列同一侧（且都不贴墙列）时，内部采样点的 x 四舍五入后
    不可能落到墙列上，直接判可见，不必逐点采样。"""
    wall_x = level["wall_x"]
    if max(ux, tx) <= wall_x - 1 or min(ux, tx) >= wall_x + 1:
        return True
    return _sampled_los_clear(level, ux, uy, tx, ty)


def visible(level, unit):
    """单位视野：切比雪夫距离不超过 radius 且视线未被墙挡住的地图内格子。

    只扫描视野半径覆盖的格子，不重算整张地图的遮挡。
    """
    ux = unit["x"]
    uy = unit["y"]
    radius = unit["radius"]
    x_lo = max(0, ux - radius)
    x_hi = min(level["width"] - 1, ux + radius)
    y_lo = max(0, uy - radius)
    y_hi = min(level["height"] - 1, uy + radius)
    cells = []
    for ty in range(y_lo, y_hi + 1):
        for tx in range(x_lo, x_hi + 1):
            if _los_clear(level, ux, uy, tx, ty):
                cells.append((tx, ty))
    return cells


def reference_visible(level, unit):
    """参考实现：逐格暴力扫描整张地图，每格按「逐条采样连线 + 墙体阻挡」判定。

    用于对照自证：visible 的结果必须与它完全一致。
    """
    ux = unit["x"]
    uy = unit["y"]
    radius = unit["radius"]
    cells = []
    for ty in range(level["height"]):
        for tx in range(level["width"]):
            if max(abs(tx - ux), abs(ty - uy)) <= radius and _sampled_los_clear(
                level, ux, uy, tx, ty
            ):
                cells.append((tx, ty))
    return cells


def behind_wall_count(level, cells):
    """诊断：有多少「墙后」的格子被标成了可见。"""
    count = 0
    for x, y in cells:
        if x > level["wall_x"] and y != level["door_y"]:
            count += 1
    return count


def update(previous, level, units):
    """增量更新，既加也删：以当前单位集合重新计算视野，
    只由已走开/消失单位贡献的格子被移除。单位集合不变时结果与一次性计算相同。

    没有单位时没有新的观测来源，保留既有视野集合。
    """
    if not units:
        return set(previous)
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
