"""Unit conversion and energy use intensity (EUI) maths."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

# kBtu per one unit of energy
ENERGY_TO_KBTU: dict[str, float] = {
    "kbtu": 1.0,
    "mmbtu": 1000.0,
    "therm": 100.0,
    "kwh": 3.412142,
    "mwh": 3412.142,
    "gj": 947.817,
    "mj": 0.947817,
}

# square feet per one unit of area
AREA_TO_SQFT: dict[str, float] = {
    "sqft": 1.0,
    "sqm": 10.763910,
}

KWH_PER_KBTU = 1 / ENERGY_TO_KBTU["kwh"]
SQM_PER_SQFT = 1 / AREA_TO_SQFT["sqm"]


@dataclass(frozen=True)
class Eui:
    """Result of one EUI calculation."""

    building: str
    kbtu_per_sqft: float
    kwh_per_sqm: float


def to_kbtu(value: float, unit: str) -> float:
    """Convert an energy value to kBtu. Raises ValueError on unknown unit or negative value."""
    key = unit.strip().lower()
    if key not in ENERGY_TO_KBTU:
        raise ValueError(f"unknown energy unit: {unit!r}")
    if value < 0:
        raise ValueError("energy cannot be negative")
    return value * ENERGY_TO_KBTU[key]


def to_sqft(value: float, unit: str) -> float:
    """Convert a floor area to square feet. Raises ValueError on unknown unit or area <= 0."""
    key = unit.strip().lower()
    if key not in AREA_TO_SQFT:
        raise ValueError(f"unknown area unit: {unit!r}")
    if value <= 0:
        raise ValueError("area must be greater than zero")
    return value * AREA_TO_SQFT[key]


def eui(building: str, energy: float, energy_unit: str, area: float, area_unit: str) -> Eui:
    """Compute annual site EUI in kBtu/sqft and kWh/sqm."""
    kbtu = to_kbtu(energy, energy_unit)
    sqft = to_sqft(area, area_unit)
    per_sqft = kbtu / sqft
    per_sqm = kbtu * KWH_PER_KBTU / (sqft * SQM_PER_SQFT)
    return Eui(building, per_sqft, per_sqm)


def eui_from_csv(path: str | Path) -> list[Eui]:
    """Read rows (building, energy, energy_unit, area, area_unit) and return one Eui per row."""
    results: list[Eui] = []
    with open(path, newline="", encoding="utf-8") as handle:
        for line_no, row in enumerate(csv.DictReader(handle), start=2):
            try:
                results.append(
                    eui(
                        row["building"],
                        float(row["energy"]),
                        row["energy_unit"],
                        float(row["area"]),
                        row["area_unit"],
                    )
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(f"line {line_no}: {exc}") from exc
    return results
