"""Command line: python -m eui_calculator FILE.csv  or  --energy N --energy-unit U --area N --area-unit U."""
from __future__ import annotations

import argparse
import sys

from .core import Eui, eui, eui_from_csv


def render(rows: list[Eui]) -> str:
    """Format results as a plain text table."""
    width = max([len("building")] + [len(r.building) for r in rows])
    lines = [f"{'building':<{width}}  {'kBtu/sqft':>10}  {'kWh/sqm':>9}"]
    for r in rows:
        lines.append(f"{r.building:<{width}}  {r.kbtu_per_sqft:>10.1f}  {r.kwh_per_sqm:>9.1f}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = argparse.ArgumentParser(prog="eui_calculator", description="Annual site EUI calculator")
    parser.add_argument("csv", nargs="?", help="CSV with building,energy,energy_unit,area,area_unit")
    parser.add_argument("--energy", type=float)
    parser.add_argument("--energy-unit", default="kwh")
    parser.add_argument("--area", type=float)
    parser.add_argument("--area-unit", default="sqft")
    args = parser.parse_args(argv)
    try:
        if args.csv:
            rows = eui_from_csv(args.csv)
        elif args.energy is not None and args.area is not None:
            rows = [eui("single", args.energy, args.energy_unit, args.area, args.area_unit)]
        else:
            parser.error("give a CSV file or both --energy and --area")
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(render(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
