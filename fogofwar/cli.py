"""命令行入口：跑视野与增量更新样例。"""

import argparse

from .vision import behind_wall_count, sample_a, update, visible


def build_parser():
    parser = argparse.ArgumentParser(prog="fog-of-war", description="战场视野")
    parser.add_argument("--map", default="sample-a", help="sample-a")
    parser.add_argument("--incremental", action="store_true", help="跑增量更新样例")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    level = sample_a()
    if args.incremental:
        first = set(visible(level, level["units"][0]))
        moved = [{"x": 1, "y": 0, "radius": 2}]
        second = update(set(first), level, moved)
        fresh = set()
        for unit in moved:
            fresh |= set(visible(level, unit))
        stale = len(second - fresh)
        print("first=%d second=%d stale=%d" % (len(first), len(second), stale))
        return 0
    cells = visible(level, level["units"][0])
    print("visible=%d behind_wall=%d" % (len(cells), behind_wall_count(level, cells)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
