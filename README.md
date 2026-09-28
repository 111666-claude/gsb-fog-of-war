# fog-of-war

战场视野：视野半径、墙体遮挡与增量更新，只用 Python 标准库。

```
python3 -m fogofwar.cli --map sample-a
python3 -m fogofwar.cli --map sample-a --incremental
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **视线要被墙挡住**：目标格与单位之间的连线如果穿过墙体，就不可见；墙格本身可见。
  `--map sample-a` 现在只看距离，把墙后（`x > wall_x` 且不在门口那一行）的 8 个格子也算成可见，
  给 `behind_wall=8`；按口径必须是 `behind_wall=0`。
- **增量更新要既加也删**：单位走开或死亡后，只由它贡献的格子必须从视野里移除。
  `--incremental`（单位从 (2,4) 挪到 (1,0)）按口径是 `stale=0`，现在只做并集，留下大量已过期的格子。
- **与暴力实现一致**：每个格子按「逐条采样连线 + 墙体阻挡」判定，结果要与逐格暴力扫描完全一致，
  并且同一张地图重复计算结果相同。
- 规模：200×200 地图、100 个单位、半径 20，每帧更新 0.5 秒内完成，内存 O(地图格数 + 单位数)；
  不许每个单位都重算整张地图的遮挡。

## 现在的行为

- `visible` 只判断切比雪夫距离，完全没有读墙体信息。
- `update` 只做 `current |= visible(...)`：旧视野永远留在集合里。
- `behind_wall_count` 是诊断用的对照函数，用来量化「墙后可见」的格子数。

## 计划新增的能力

```
--map sample-a
--incremental
```

## 输出

```
visible=63 behind_wall=0
first=63 second=25 stale=0
```

## 目录

```
fogofwar/vision.py   视野、遮挡与增量更新
fogofwar/cli.py      命令行入口
tests/               unittest 用例
```
