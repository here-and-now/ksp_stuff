"""Native pytest gates for physics_warp (rails 0, never WarpTo)."""

from __future__ import annotations

from pathlib import Path

from physics_warp import COAST_RATE, PAD_RATE, apply_coast, rails_zero, set_factor, set_rate


def _sc(rails: int = 0, phys: int = 0):
    return type(
        "SC",
        (),
        {"rails_warp_factor": rails, "physics_warp_factor": phys},
    )()


def _sess(sc):
    return type("S", (), {"space_center": sc})()


def test_coast_rate_is_3x():
    assert COAST_RATE == 3
    assert PAD_RATE == 3


def test_set_rate_3x_is_factor_2_rails_0():
    sc = _sc(rails=4, phys=0)
    n = set_rate(_sess(sc), 3)
    assert n == 2
    assert sc.physics_warp_factor == 2
    assert sc.rails_warp_factor == 0


def test_apply_coast_false_is_1x():
    sc = _sc(phys=3, rails=2)
    last = ["3x"]
    logs: list[str] = []
    n = apply_coast(_sess(sc), coast=False, on_log=logs.append, last=last)
    assert n == 0
    assert sc.physics_warp_factor == 0
    assert sc.rails_warp_factor == 0
    assert last[0] == "1x"
    assert any("hop physics 1x" in x for x in logs)


def test_apply_coast_default_3x():
    sc = _sc()
    last: list[str] = [""]
    logs: list[str] = []
    n = apply_coast(_sess(sc), coast=True, on_log=logs.append, last=last)
    assert n == 2
    assert sc.physics_warp_factor == 2
    assert sc.rails_warp_factor == 0
    assert last[0] == "3x"
    assert any("hop coast physics 3x rails=0" in x for x in logs)


def test_apply_coast_uplink_1x():
    sc = _sc(phys=2)
    n = apply_coast(_sess(sc), coast=True, uplink_rate=1, last=[""])
    assert n == 0
    assert sc.physics_warp_factor == 0


def test_apply_coast_uplink_4x():
    sc = _sc()
    last = [""]
    n = apply_coast(_sess(sc), coast=True, uplink_rate=4, last=last)
    assert n == 3
    assert sc.physics_warp_factor == 3
    assert last[0] == "4x"


def test_rails_zero_never_raises_without_sc():
    rails_zero(type("S", (), {})())
    set_factor(type("S", (), {})(), 0)


def test_source_never_warpto():
    for path in ("physics_warp.py", "hop.py", "hop_factory.py", "pad.py"):
        text = Path(path).read_text(encoding="utf-8")
        assert "WarpTo(" not in text
        assert "warp_to(" not in text
    warp = Path("physics_warp.py").read_text(encoding="utf-8")
    assert "rails_warp_factor = 0" in warp
    assert "rails_warp_factor = 1" not in warp


def test_live_records_false_under_pytest():
    from flightlog import live_records

    assert live_records() is False
