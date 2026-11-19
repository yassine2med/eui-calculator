import pytest

from eui_calculator.__main__ import main, render
from eui_calculator.core import eui, eui_from_csv, to_kbtu, to_sqft


def test_kwh_to_kbtu():
    assert to_kbtu(1000, "kWh") == pytest.approx(3412.142)


def test_therm_and_mmbtu():
    assert to_kbtu(10, "therm") == 1000
    assert to_kbtu(2, "MMBtu") == 2000


def test_unit_is_case_and_space_insensitive():
    assert to_kbtu(1, " KWH ") == pytest.approx(3.412142)


def test_unknown_energy_unit():
    with pytest.raises(ValueError, match="unknown energy unit"):
        to_kbtu(1, "barrel")


def test_negative_energy_rejected():
    with pytest.raises(ValueError):
        to_kbtu(-1, "kwh")


def test_zero_area_rejected():
    with pytest.raises(ValueError, match="greater than zero"):
        to_sqft(0, "sqft")


def test_sqm_to_sqft():
    assert to_sqft(100, "sqm") == pytest.approx(1076.391)


def test_eui_simple():
    r = eui("X", 100000, "kbtu", 1000, "sqft")
    assert r.kbtu_per_sqft == 100
    assert r.kwh_per_sqm == pytest.approx(100 / 3.412142 * 10.76391, rel=1e-6)


def test_eui_metric_area():
    r = eui("Y", 1000, "kwh", 100, "sqm")
    assert r.kwh_per_sqm == pytest.approx(10.0)


def test_csv_example(tmp_path):
    rows = eui_from_csv("examples/buildings.csv")
    assert [r.building for r in rows][0] == "Building A"
    assert len(rows) == 5


def test_csv_bad_row_reports_line(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("building,energy,energy_unit,area,area_unit\nZ,10,kwh,0,sqft\n")
    with pytest.raises(ValueError, match="line 2"):
        eui_from_csv(p)


def test_cli_exit_codes(capsys):
    assert main(["--energy", "5000", "--energy-unit", "therm", "--area", "10000"]) == 0
    assert "single" in capsys.readouterr().out
    assert main(["missing.csv"]) == 1


def test_render_has_header():
    assert render([eui("B", 1, "kbtu", 1, "sqft")]).startswith("building")
