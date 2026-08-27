"""Native pytest gates for physics_warp (rails 0, never WarpTo)."""

from __future__ import annotations

from pathlib import Path

from physics_warp import (
    CHUTE_DEPLOY_ALT_M,
    CHUTE_OPEN,
    COAST_Q_MAX_PA,
    COAST_RATE,
    LOFT_ALT_M,
    PAD_RATE,
    THICK_AIR_ALT_M,
    WARP_PULSE_SLACK_S,
    airborne_cannot_pay,
    apply_coast,
    apply_sit_warp,
    chute_arm_sit,
    chute_deploy_sit,
    high_q_sit,
    crash_ui_leave,
    leftover_abort_kv,
    leftover_abort_why,
    leftover_call,
    leftover_ksc_call,
    rails_zero,
    space_low_sit,
    set_factor,
    set_rate,
    thick_air_cross_sit,
    thick_air_sit,
    timeout_hit,
    unpause_clock,
    want_coast,
)


def _sc(rails: int = 0, phys: int = 0):
    return type(
        "SC",
        (),
        {"rails_warp_factor": rails, "physics_warp_factor": phys},
    )()


def _sess(sc):
    return type("S", (), {"space_center": sc})()


def test_coast_rate_is_4x():
    assert COAST_RATE == 4
    assert PAD_RATE == 3


def test_coast_rate_env_pins_test_hop(monkeypatch):
    from physics_warp import coast_rate

    monkeypatch.delenv("KSPSTUFF_PHYS_WARP", raising=False)
    assert coast_rate() == 4
    monkeypatch.setenv("KSPSTUFF_PHYS_WARP", "1")
    assert coast_rate() == 1
    monkeypatch.setenv("KSPSTUFF_PHYS_WARP", "4")
    assert coast_rate() == 4
    monkeypatch.setenv("KSPSTUFF_PHYS_WARP", "9")
    assert coast_rate() == 4
    monkeypatch.setenv("KSPSTUFF_PHYS_WARP", "nope")
    assert coast_rate() == 4


def test_set_rate_3x_is_factor_2_rails_0():
    sc = _sc(rails=4, phys=0)
    n = set_rate(_sess(sc), 3)
    assert n == 2
    assert sc.physics_warp_factor == 2
    assert sc.rails_warp_factor == 0


def test_unpause_clock_does_not_kill_4x():
    sc = _sc(phys=3, rails=2)
    krpc = type("K", (), {"paused": True})()
    sess = type(
        "S",
        (),
        {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
    )()
    sc.paused = True
    unpause_clock(sess)
    assert krpc.paused is False
    assert sc.paused is False
    assert sc.physics_warp_factor == 3
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


def test_apply_coast_default_4x():
    sc = _sc()
    last: list[str] = [""]
    logs: list[str] = []
    n = apply_coast(_sess(sc), coast=True, on_log=logs.append, last=last)
    assert n == 3
    assert sc.physics_warp_factor == 3
    assert sc.rails_warp_factor == 0
    assert last[0] == "4x"
    assert any("hop coast physics 4x rails=0" in x for x in logs)


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


def _snap(**kw):
    return type("Snap", (), kw)()


def test_want_coast_after_burnout_q_safe():
    snap = _snap(v_vert=40.0, alt=41_884.0, q=400.0)
    assert want_coast(snap, left_pad=True, down=False, burning=False)


def test_want_coast_1x_burn_pad_down_deploy():
    snap = _snap(v_vert=40.0, alt=12_000.0, q=400.0)
    assert not want_coast(snap, left_pad=False, down=False, burning=False)
    assert not want_coast(snap, left_pad=True, down=True, burning=False)
    assert not want_coast(snap, left_pad=True, down=False, burning=True)
    pad = _snap(v_vert=14.0, alt=101.0, q=15.0)
    assert not want_coast(pad, left_pad=True, down=False, burning=False)
    deploy = _snap(v_vert=-80.0, alt=1_500.0, q=1_200.0)
    assert chute_deploy_sit(deploy)
    assert not want_coast(deploy, left_pad=True, down=False, burning=False)
    silk = _snap(v_vert=-12.0, alt=800.0, chute="deployed", q=22.0)
    assert not want_coast(silk, left_pad=True, down=False, burning=False)
    semi = _snap(v_vert=-20.0, alt=1_200.0, chute="semi_deployed", q=400.0)
    assert not want_coast(semi, left_pad=True, down=False, burning=False)


def test_want_coast_high_q_is_1x():
    """10-31-47Z 4× at q≈29.5 kPa sheared. 17-26-04Z 4× at q≈4.7 kPa sheared.

    1× until q ≤1 kPa. 5 kPa was not actually low.
    """
    burnout = _snap(v_vert=256.0, alt=5_388.0, q=29_516.0, chute="armed")
    assert high_q_sit(burnout)
    assert not want_coast(burnout, left_pad=True, down=False, burning=False)
    wait = _snap(v_vert=148.0, alt=904.0, q=4_728.0, chute="stowed")
    assert high_q_sit(wait)
    assert not want_coast(wait, left_pad=True, down=False, burning=False)
    loft = _snap(v_vert=369.0, alt=41_884.0, q=400.0, chute="armed")
    assert want_coast(loft, left_pad=True, down=False, burning=False)
    missing_q = _snap(v_vert=40.0, alt=41_884.0)
    assert high_q_sit(missing_q)
    assert not want_coast(missing_q, left_pad=True, down=False, burning=False)


def test_chute_deploy_sit_ignores_skip():
    assert CHUTE_DEPLOY_ALT_M == 2_000.0
    assert LOFT_ALT_M == 250.0
    assert COAST_Q_MAX_PA == 1_000.0
    assert THICK_AIR_ALT_M == 18_000.0
    down = _snap(v_vert=-40.0, alt=1_500.0)
    assert chute_deploy_sit(down)
    assert not chute_deploy_sit(_snap(v_vert=40.0, alt=1_500.0))
    assert not chute_deploy_sit(_snap(v_vert=-40.0, alt=12_000.0))
    assert not chute_deploy_sit(_snap(v_vert=-40.0, alt=0.0))
    semi = _snap(v_vert=-20.0, alt=1_200.0, chute="semi_deployed")
    assert chute_deploy_sit(semi)


def test_chute_arm_sit_descent_not_only_2km():
    """11-11-37Z lithobrake 2.9 km q=5.7 kPa still stowed. Arm on vz<0 above 2 km."""
    crash = _snap(
        v_vert=-80.0, alt=2_918.0, q=5_748.0, pitch=-14.0, chute="stowed"
    )
    assert chute_arm_sit(crash)
    assert not chute_deploy_sit(crash)
    assert high_q_sit(crash)
    assert not want_coast(crash, left_pad=True, down=False, burning=False)

    loft_down = _snap(v_vert=-40.0, alt=12_000.0, q=400.0, chute="stowed")
    assert chute_arm_sit(loft_down)
    assert not chute_deploy_sit(loft_down)
    assert not want_coast(loft_down, left_pad=True, down=False, burning=False)

    climb = _snap(v_vert=40.0, alt=12_000.0, q=400.0, chute="stowed")
    assert not chute_arm_sit(climb)
    pad = _snap(v_vert=-1.0, alt=101.0, q=15.0)
    assert not chute_arm_sit(pad)
    light = _snap(v_vert=14.0, alt=88.0, q=43.0, chute="stowed")
    assert not chute_arm_sit(light)

    pitch_down = _snap(alt=12_000.0, pitch=-20.0, q=400.0)
    assert chute_arm_sit(pitch_down)
    assert not want_coast(pitch_down, left_pad=True, down=False, burning=False)
    assert not chute_arm_sit(_snap(alt=12_000.0, pitch=65.0, q=400.0))

    deploy = _snap(v_vert=-80.0, alt=1_500.0, q=1_200.0)
    assert chute_arm_sit(deploy)
    assert chute_deploy_sit(deploy)

    vac = _snap(v_vert=-40.0, alt=200_000.0, q=0.0, chute="stowed")
    assert not thick_air_sit(vac)
    assert not chute_arm_sit(vac)
    assert not chute_arm_sit(_snap(alt=200_000.0, pitch=-20.0, q=0.0))


def test_airborne_cannot_pay_is_sit_flag():
    kw = dict(
        lofted=True,
        down=False,
        started=[],
        science_attempted=True,
        waiting_hd=False,
    )
    assert airborne_cannot_pay(**kw)
    assert not airborne_cannot_pay(**{**kw, "down": True})
    assert not airborne_cannot_pay(**{**kw, "started": ["temperatureScan"]})
    assert not airborne_cannot_pay(**{**kw, "waiting_hd": True})
    assert not airborne_cannot_pay(**{**kw, "lofted": False})
    assert not airborne_cannot_pay(**{**kw, "science_attempted": False})


def test_apply_sit_warp_skip_loft_keeps_4x():
    """47 km loft after cannot-pay: unpause is not Hangar 1×."""
    sc = _sc(phys=3, rails=2)
    krpc = type("K", (), {"paused": True})()
    sess = type(
        "S",
        (),
        {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
    )()
    sc.paused = True
    snap = _snap(v_vert=368.0, alt=41_884.0, q=400.0, chute="armed")
    last = ["4x"]
    n = apply_sit_warp(
        sess,
        snap,
        left_pad=True,
        down=False,
        burning=False,
        last=last,
    )
    assert krpc.paused is False
    assert sc.paused is False
    assert n == 3
    assert sc.physics_warp_factor == 3
    assert sc.rails_warp_factor == 0
    assert last[0] == "4x"


def test_want_coast_thick_air_18km_lid_is_1x():
    """06-57-16Z 4× at ~3 km after hop_apo=18000. 18 km lid is still thick."""
    wreck = _snap(v_vert=40.0, alt=3_265.9, q=2_670.0, chute="stowed")
    assert thick_air_sit(wreck)
    assert high_q_sit(wreck)
    assert not want_coast(wreck, left_pad=True, down=False, burning=False)
    lid = _snap(v_vert=40.0, alt=18_000.0, q=400.0)
    assert thick_air_sit(lid)
    assert not want_coast(lid, left_pad=True, down=False, burning=False)
    just = _snap(v_vert=40.0, alt=18_000.1, q=400.0)
    assert not thick_air_sit(just)
    assert want_coast(just, left_pad=True, down=False, burning=False)
    twelve = _snap(v_vert=40.0, alt=12_000.0, q=400.0)
    assert thick_air_sit(twelve)
    assert not want_coast(twelve, left_pad=True, down=False, burning=False)
    mun = _snap(v_vert=40.0, alt=5_000.0, q=0.0, in_atmo=False)
    assert not thick_air_sit(mun)
    assert want_coast(mun, left_pad=True, down=False, burning=False)
    unknown_alt = _snap(v_vert=40.0, q=400.0)
    assert thick_air_sit(unknown_alt)
    assert not want_coast(unknown_alt, left_pad=True, down=False, burning=False)


def test_apply_sit_warp_thick_air_is_1x_clock_runs():
    sc = _sc(phys=3, rails=1)
    krpc = type("K", (), {"paused": True})()
    sess = type(
        "S",
        (),
        {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
    )()
    sc.paused = True
    snap = _snap(v_vert=40.0, alt=3_265.9, q=2_670.0, chute="stowed")
    last = ["4x"]
    n = apply_sit_warp(
        sess, snap, left_pad=True, down=False, burning=False, last=last
    )
    assert n == 0
    assert sc.physics_warp_factor == 0
    assert sc.rails_warp_factor == 0
    assert krpc.paused is False
    assert last[0] == "1x"


def test_want_coast_1x_on_chute_arm_sit_before_silk():
    """15-10-47Z: 4× coast, arm, deploy, then 1×, shear 28→18. 1× on arm sit."""
    arm = _snap(v_vert=-40.0, alt=12_000.0, q=400.0, chute="stowed")
    assert chute_arm_sit(arm)
    assert not want_coast(arm, left_pad=True, down=False, burning=False)
    armed = _snap(v_vert=-40.0, alt=12_000.0, q=400.0, chute="armed")
    assert chute_arm_sit(armed)
    assert not want_coast(armed, left_pad=True, down=False, burning=False)
    silk = _snap(v_vert=-12.0, alt=800.0, chute="deployed", q=22.0)
    assert not want_coast(silk, left_pad=True, down=False, burning=False)
    climb_armed = _snap(v_vert=369.0, alt=41_884.0, q=400.0, chute="armed")
    assert not chute_arm_sit(climb_armed)
    assert want_coast(climb_armed, left_pad=True, down=False, burning=False)


def test_want_coast_quiet_descent_above_thick_air():
    """T-442: 4× died at apo ~200 km because Arm was any vz<0. Not silk."""
    vac = _snap(v_vert=-40.0, alt=200_000.0, q=0.0, chute="stowed")
    assert not thick_air_sit(vac)
    assert not thick_air_cross_sit(vac)
    assert not chute_arm_sit(vac)
    assert want_coast(vac, left_pad=True, down=False, burning=False)
    armed = _snap(v_vert=-40.0, alt=200_000.0, q=0.0, chute="armed")
    assert not chute_arm_sit(armed)
    assert want_coast(armed, left_pad=True, down=False, burning=False)
    just = _snap(v_vert=-40.0, alt=18_000.1, q=400.0, chute="stowed")
    assert not thick_air_sit(just)
    assert not chute_arm_sit(just)
    assert thick_air_cross_sit(just)
    assert not want_coast(just, left_pad=True, down=False, burning=False)
    lid_down = _snap(v_vert=-40.0, alt=18_000.0, q=400.0, chute="stowed")
    assert thick_air_sit(lid_down)
    assert chute_arm_sit(lid_down)
    assert not want_coast(lid_down, left_pad=True, down=False, burning=False)


def test_want_coast_thick_air_cross_does_not_skip_18km_lid():
    """09-01Z 4× 55 km q=937 → 6 km q=17510 in 7.7 s wall. Pulse slower than 4×."""
    assert WARP_PULSE_SLACK_S == 12.0
    skip = _snap(
        v_vert=-1791.625,
        alt=55_125.382,
        q=936.979,
        chute="none",
        pitch=65.516,
    )
    assert not thick_air_sit(skip)
    assert not high_q_sit(skip)
    assert not chute_arm_sit(skip)
    assert thick_air_cross_sit(skip)
    assert not want_coast(skip, left_pad=True, down=False, burning=False)
    assert not thick_air_cross_sit(skip, rate=1)
    mid = _snap(v_vert=-1423.712, alt=118_429.263, q=0.032, chute="none")
    assert not thick_air_sit(mid)
    assert not thick_air_cross_sit(mid)
    assert want_coast(mid, left_pad=True, down=False, burning=False)
    mun = _snap(v_vert=-1800.0, alt=55_000.0, q=0.0, in_atmo=False)
    assert not thick_air_cross_sit(mun)
    assert want_coast(mun, left_pad=True, down=False, burning=False)
    unknown_vz = _snap(alt=55_000.0, q=400.0, pitch=-20.0)
    assert thick_air_cross_sit(unknown_vz)
    assert not want_coast(unknown_vz, left_pad=True, down=False, burning=False)
    climb = _snap(v_vert=40.0, alt=55_000.0, q=400.0)
    assert not thick_air_cross_sit(climb)
    assert want_coast(climb, left_pad=True, down=False, burning=False)


def test_apply_sit_warp_thick_air_cross_is_1x():
    sc = _sc(phys=3, rails=1)
    krpc = type("K", (), {"paused": True})()
    sess = type(
        "S",
        (),
        {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
    )()
    sc.paused = True
    snap = _snap(
        v_vert=-1791.625, alt=55_125.382, q=936.979, chute="none"
    )
    last = ["4x"]
    n = apply_sit_warp(
        sess,
        snap,
        left_pad=True,
        down=False,
        burning=False,
        last=last,
        uplink_rate=4,
    )
    assert n == 0
    assert sc.physics_warp_factor == 0
    assert sc.rails_warp_factor == 0
    assert krpc.paused is False
    assert last[0] == "1x"


def test_apply_sit_warp_arm_sit_is_1x():
    sc = _sc(phys=3, rails=1)
    krpc = type("K", (), {"paused": True})()
    sess = type(
        "S",
        (),
        {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
    )()
    sc.paused = True
    snap = _snap(v_vert=-40.0, alt=12_000.0, q=400.0, chute="stowed")
    last = ["4x"]
    n = apply_sit_warp(
        sess, snap, left_pad=True, down=False, burning=False, last=last
    )
    assert n == 0
    assert sc.physics_warp_factor == 0
    assert sc.rails_warp_factor == 0
    assert krpc.paused is False
    assert last[0] == "1x"


def test_apply_sit_warp_quiet_descent_200km_is_4x():
    sc = _sc(phys=3, rails=1)
    krpc = type("K", (), {"paused": True})()
    sess = type(
        "S",
        (),
        {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
    )()
    sc.paused = True
    snap = _snap(v_vert=-40.0, alt=200_000.0, q=0.0, chute="stowed")
    last = ["4x"]
    n = apply_sit_warp(
        sess,
        snap,
        left_pad=True,
        down=False,
        burning=False,
        last=last,
        uplink_rate=4,
    )
    assert n == 3
    assert sc.physics_warp_factor == 3
    assert sc.rails_warp_factor == 0
    assert krpc.paused is False
    assert last[0] == "4x"


def test_apply_sit_warp_high_q_is_1x_clock_runs():
    sc = _sc(phys=3, rails=1)
    krpc = type("K", (), {"paused": True})()
    sess = type(
        "S",
        (),
        {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
    )()
    sc.paused = True
    snap = _snap(v_vert=256.0, alt=5_388.0, q=29_516.0, chute="armed")
    last = ["4x"]
    n = apply_sit_warp(
        sess, snap, left_pad=True, down=False, burning=False, last=last
    )
    assert n == 0
    assert sc.physics_warp_factor == 0
    assert sc.rails_warp_factor == 0
    assert krpc.paused is False
    assert last[0] == "1x"


def test_apply_sit_warp_wait_q_is_1x_not_4x():
    """FlyingHigh wait at ~1 km q≈4.7 kPa: unpause is not 4×."""
    sc = _sc(phys=3, rails=1)
    krpc = type("K", (), {"paused": True})()
    sess = type(
        "S",
        (),
        {"space_center": sc, "conn": type("C", (), {"krpc": krpc})()},
    )()
    sc.paused = True
    snap = _snap(v_vert=148.0, alt=904.0, q=4_728.0, chute="stowed")
    last = ["4x"]
    n = apply_sit_warp(
        sess, snap, left_pad=True, down=False, burning=False, last=last
    )
    assert n == 0
    assert sc.physics_warp_factor == 0
    assert sc.rails_warp_factor == 0
    assert krpc.paused is False
    assert last[0] == "1x"


def test_timeout_is_met_not_wall():
    """T-328: MET 8 / wall 612 is not timeout. T-330: MET 129 still flying."""
    assert not timeout_hit(met=8.3, met0=0.0, budget=600.0, down=False)
    assert not timeout_hit(met=129.4, met0=0.0, budget=600.0, down=False)
    assert timeout_hit(met=600.0, met0=0.0, budget=600.0, down=False)
    assert not timeout_hit(met=600.0, met0=0.0, budget=600.0, down=True)
    assert not timeout_hit(met=float("nan"), met0=0.0, budget=600.0, down=False)
    assert leftover_call(recoverable=True) == "recover"
    assert leftover_call(recoverable=False) == "ksc leftover"
    from emergencies import resolve

    assert resolve(leftover_call(recoverable=True)) == "recover"
    assert resolve(leftover_call(recoverable=False)) == "ksc_leftover"
    assert leftover_ksc_call(True) == "python main.py recover-probe --recover"
    assert leftover_ksc_call(False) == "python main.py recover-probe --space-center"
    assert crash_ui_leave() == "ksc leftover"
    assert crash_ui_leave(total_wreck=True) == "ksc leftover"
    kv = leftover_abort_kv(sit="splashed", recoverable=True)
    assert kv[0] == "ksc: leftover"
    assert kv[1] == "sit: splashed"
    assert kv[2] == "recoverable: yes"
    assert kv[3] == "call: python main.py recover-probe --recover"
    why = leftover_abort_why(sit="flying", recoverable=False, why="timeout")
    assert why.startswith("ksc leftover sit=flying recoverable=no")
    assert "timeout" in why
    assert "recover-probe --space-center" in why
    assert "deployed" in CHUTE_OPEN
    assert "semi_deployed" in CHUTE_OPEN


def test_space_low_sit_not_flying_lid():
    """16-23-52Z flying at 50 km is not InSpaceLow; sub_orbital is."""
    assert not space_low_sit("flying")
    assert not space_low_sit("landed")
    assert not space_low_sit("splashed")
    assert not space_low_sit("")
    assert space_low_sit("sub_orbital")
    assert space_low_sit("orbiting")
    assert space_low_sit("escaping")
    assert space_low_sit("InSpaceLow")
    assert not space_low_sit("InSpaceHigh")


def test_source_sit_blocks_not_stamp_helpers():
    warp = Path("physics_warp.py").read_text(encoding="utf-8")
    assert "def _loft_after_skip" not in warp
    assert "def _coast_after_skip" not in warp
    assert "def airborne_cannot_pay" in warp
    assert "def apply_sit_warp" in warp
    assert "def chute_arm_sit" in warp
    assert "def chute_deploy_sit" in warp
    assert "def timeout_hit" in warp
    assert "def leftover_ksc_call" in warp
    assert "def leftover_abort_kv" in warp
    assert "def crash_ui_leave" in warp
    assert "def space_low_sit" in warp
    assert "Skip-save Tracking is not Close" in warp
    assert "def thick_air_sit" in warp
    assert "def thick_air_cross_sit" in warp
    assert "Never revert" in warp
    assert "WarpTo(" not in warp
    hop = Path("hop.py").read_text(encoding="utf-8")
    assert "leftover_abort_kv" in hop
    assert "chute_deploy_sit" in hop
    assert "want_coast" in hop
    assert "crash_ui_leave" in hop
    assert "not skip-save tracking" in hop
    assert "def leftover_ksc_call" not in hop
    factory = Path("hop_factory.py").read_text(encoding="utf-8")
    assert "def _loft_after_skip" not in factory
    assert "def _coast_after_skip" not in factory
    assert "apply_sit_warp" in factory
    assert "airborne_cannot_pay" in factory
    assert "chute_arm_sit" in factory
    assert "chute_deploy_sit" in factory
    assert "timeout_hit" in factory
    assert "leftover_call" in factory
    assert "space_low_sit as _space_low_sit" in factory
    assert "def _space_low_sit" not in factory
    assert "def _lid_alt_reached" in factory
    assert "def _lid_burn_sit" in factory
    assert "def _high_dwell_sit" in factory
    assert "def _leftover_sit" in factory
    assert "def _lid_vertical_sit" in factory
    assert "def _hold_lid" in factory
    assert "def _inland_high_sit" in factory
    assert "def _chute_arm_now" in factory
    assert "def _chute_deploy_now" in factory
    warp_at = factory.find("apply_sit_warp(")
    arm_at = factory.find("H.arm_chutes")
    assert warp_at != -1 and arm_at != -1
    assert warp_at < arm_at
    warp_chunk = factory[warp_at : warp_at + 280]
    assert "burning=burning_now" in warp_chunk
    assert "_high_dwell_sit" not in warp_chunk
