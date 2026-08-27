"""VAB helpers: clone, tanks, chute MODULE, girders, wheel, HS."""

from __future__ import annotations

import unittest
from pathlib import Path

from catalog import Catalog, scan_config_cache, scan_gamedata
from craft import (
    Craft,
    CraftError,
    CraftPart,
    DECOUPLER_NAME,
    HS_COLLIDER_OVERSHOOT,
    TERRIER_NAME,
    axial_tanks,
    autostrut_stack,
    chute_is_nylon_good,
    clone_craft,
    cmd_craft,
    copy_chute,
    dump_attach_fuel,
    find_chutes,
    find_core,
    find_engine,
    girder_ring,
    heatshield_clearance_half,
    heatshield_modules,
    heatshield_place_half,
    insert_heatshield,
    insert_inline,
    insert_two_stage,
    insert_wheel,
    liquid_cylinder,
    pad_pbc,
    proc_volume,
    procedural_cylinder,
    replace_tanks,
    set_nylon_chute,
    stage_engine_first,
    strip_girders,
)

ROOT = Path(__file__).resolve().parents[1]
CRAFTS = ROOT / "crafts"
T7 = CRAFTS / "kspstuff-hop-valiant-t7-pbc.craft"
T7_WHEEL = CRAFTS / "kspstuff-hop-valiant-t7-wheel-pbc.craft"
T7_CHUTE = CRAFTS / "kspstuff-hop-valiant-t7-chute-pbc.craft"
T7_CONE = CRAFTS / "kspstuff-hop-valiant-t7-chute-cone-pbc.craft"
T7_HS_CONE = CRAFTS / "kspstuff-hop-valiant-t7-wheel-proc-hs-cone-pbc.craft"
T7_PROC_HS = CRAFTS / "kspstuff-hop-valiant-t7-wheel-proc-hs-pbc.craft"
STIFF = CRAFTS / "kspstuff-hop-valiant-proc-stiff-pbc.craft"
LOFT = CRAFTS / "kspstuff-hop-valiant-proc-loft-pbc.craft"


def _mod(part, name: str):
    for m in part.modules:
        if m.get("name") == name:
            return m
    return None


class TestRoundtrip(unittest.TestCase):
    def test_preserves_heaviest_resource_sqor(self):
        src = Craft.load(STIFF)
        girders = [p for p in src.parts if p.name == "trussPiece1x"]
        self.assertGreaterEqual(len(girders), 3)
        self.assertEqual(girders[0].autostrut_mode, "Heaviest")
        self.assertEqual(girders[0].rigid_attachment, "True")
        tanks = axial_tanks(src)
        self.assertTrue(any(r.get("name") == "Kerosene" for r in tanks[0].resources))
        chute = find_chutes(src)[0]
        self.assertEqual(chute.sqor, 0)
        back = Craft.loads(src.dumps())
        g2 = [p for p in back.parts if p.name == "trussPiece1x"]
        self.assertEqual(g2[0].autostrut_mode, "Heaviest")
        self.assertEqual(g2[0].rigid_attachment, "True")
        t2 = axial_tanks(back)
        self.assertTrue(any(r.get("name") == "Kerosene" for r in t2[0].resources))
        self.assertEqual(find_chutes(back)[0].sqor, 0)
        fuel = _mod(t2[0], "ModuleFuelTanks")
        self.assertIsNotNone(fuel)
        self.assertEqual(fuel.get("type"), "Default")
        self.assertNotEqual(fuel.get("type"), "SolidFuel")


class TestCloneAndTanks(unittest.TestCase):
    def test_clone_renames_ship(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "kspstuff-hop-valiant-t7-clone-pbc.craft"
            wrote = clone_craft(T7, "kspstuff-hop-valiant-t7-clone-pbc", out)
            craft = Craft.load(wrote)
            self.assertEqual(craft.name, "kspstuff-hop-valiant-t7-clone-pbc")
            self.assertEqual(len(axial_tanks(craft)), 7)
            self.assertEqual(len(craft.parts), len(Craft.load(T7).parts))

    def test_swap_t100_to_proc_keeps_count_and_radials(self):
        craft = Craft.load(T7_WHEEL)
        n_parts = len(craft.parts)
        n_tanks = len(axial_tanks(craft))
        replace_tanks(craft, kind="proc", diameter=1.25, length=0.625)
        tanks = axial_tanks(craft)
        self.assertEqual(len(tanks), n_tanks)
        self.assertTrue(all(t.name == "proceduralTankRealFuels" for t in tanks))
        fuel = _mod(tanks[0], "ModuleFuelTanks")
        self.assertEqual(fuel.get("type"), "Default")
        self.assertNotEqual(fuel.get("type"), "SolidFuel")
        self.assertTrue(any(r.get("name") == "Kerosene" for r in tanks[0].resources))
        self.assertTrue(any(r.get("name") == "LqdOxygen" for r in tanks[0].resources))
        self.assertEqual(len(craft.parts), n_parts)
        wheel = [p for p in craft.parts if p.name == "sasModule"][0]
        self.assertEqual(wheel.att_n.get("bottom"), tanks[0].token)
        self.assertEqual(tanks[0].att_n.get("top"), wheel.token)
        engine = find_engine(craft)
        self.assertEqual(tanks[-1].att_n.get("bottom"), engine.token)
        self.assertEqual(engine.att_n.get("top"), tanks[-1].token)
        radials = [p for p in craft.parts if p.attm == 1]
        self.assertGreater(len(radials), 3)
        alive = {p.token for p in craft.parts}
        for p in radials:
            _, _, rest = p.srf_n.partition(",")
            self.assertIn(rest, alive)

    def test_count_7_to_3_keeps_engine(self):
        craft = Craft.load(T7)
        replace_tanks(craft, count=3, kind="t100")
        tanks = axial_tanks(craft)
        self.assertEqual(len(tanks), 3)
        engine = find_engine(craft)
        self.assertEqual(tanks[-1].att_n.get("bottom"), engine.token)
        self.assertEqual(engine.att_n.get("top"), tanks[-1].token)
        self.assertTrue(all(t.name == "fuelTankSmallFlat" for t in tanks))


class TestChute(unittest.TestCase):
    def test_setter_writes_nylon_5_35_not_empty(self):
        craft = Craft.load(T7_CHUTE)
        chute = find_chutes(craft)[0]
        chute.modules = []
        set_nylon_chute(craft, "mk16")
        chute = find_chutes(craft)[0]
        self.assertTrue(chute_is_nylon_good(chute))
        para = _mod(chute, "RealChuteModule").of("PARACHUTE")[0]
        self.assertEqual(para.get("material"), "Nylon")
        self.assertEqual(para.get("preDeployedDiameter"), "5")
        self.assertEqual(para.get("deployedDiameter"), "35")
        self.assertEqual(para.get("minIsPressure"), "false")
        self.assertEqual(para.get("minDeployment"), "2500")
        self.assertEqual(para.get("deploymentAlt"), "700")
        self.assertEqual(_mod(chute, "RealChuteModule").get("mustGoDown"), "True")
        engine = find_engine(craft)
        self.assertEqual(engine.istg, 0)
        self.assertEqual(engine.sqor, 0)
        self.assertEqual(chute.istg, 1)
        self.assertEqual(chute.sqor, 0)
        self.assertIsNotNone(_mod(chute, "ProceduralChute"))

    def test_cone_50m(self):
        craft = Craft.load(T7_CONE)
        find_chutes(craft)[0].modules = []
        set_nylon_chute(craft, "cone")
        chute = find_chutes(craft)[0]
        self.assertEqual(chute.name, "RC_cone")
        para = _mod(chute, "RealChuteModule").of("PARACHUTE")[0]
        self.assertEqual(para.get("deployedDiameter"), "50")
        self.assertEqual(para.get("preDeployedDiameter"), "2.5")
        self.assertEqual(para.get("minIsPressure"), "false")
        engine = find_engine(craft)
        self.assertEqual(engine.istg, 0)
        self.assertEqual(engine.sqor, 0)
        self.assertEqual(chute.istg, 1)
        self.assertEqual(chute.sqor, 0)

    def test_stage_engine_first_queues_valiant(self):
        craft = Craft.load(T7_CHUTE)
        engine = find_engine(craft)
        chute = find_chutes(craft)[0]
        chute.istg = 0
        chute.sqor = 0
        engine.istg = 1
        engine.sqor = -1
        stage_engine_first(craft)
        self.assertEqual(engine.istg, 0)
        self.assertEqual(engine.sqor, 0)
        self.assertEqual(chute.istg, 1)
        self.assertEqual(chute.sqor, 0)

    def test_copy_from_donor_refuses_inherited_tiny(self):
        donor = Craft.load(T7_CHUTE)
        target = Craft.load(T7_CHUTE)
        chute = find_chutes(target)[0]
        chute.modules = []
        copy_chute(target, donor)
        self.assertTrue(chute_is_nylon_good(find_chutes(target)[0]))
        bad = Craft.load(T7_CHUTE)
        para = _mod(find_chutes(bad)[0], "RealChuteModule").of("PARACHUTE")[0]
        para.set("deployedDiameter", "0.8")
        para.set("minIsPressure", "true")
        para.set("minPressure", "0.04")
        empty = Craft.load(T7_CHUTE)
        find_chutes(empty)[0].modules = []
        with self.assertRaises(ValueError):
            copy_chute(empty, bad)


class TestGirdersWheelHs(unittest.TestCase):
    def test_girder_ring_3_heaviest(self):
        craft = Craft.load(T7_WHEEL)
        tanks = axial_tanks(craft)
        mid = tanks[len(tanks) // 2]
        girders = girder_ring(craft, 3, on="mid")
        self.assertEqual(len(girders), 3)
        for g in girders:
            self.assertEqual(g.name, "trussPiece1x")
            self.assertEqual(g.autostrut_mode, "Heaviest")
            self.assertEqual(g.rigid_attachment, "True")
            self.assertEqual(g.attm, 1)
            self.assertEqual(g.srf_n, f"srfAttach,{mid.token}")
        xs = sorted(round(g.att_pos0[0], 3) for g in girders)
        zs = sorted(abs(round(g.att_pos0[2], 3)) for g in girders)
        self.assertAlmostEqual(xs[2], 0.7, places=2)
        self.assertAlmostEqual(xs[0], -0.35, places=2)
        self.assertAlmostEqual(max(zs), 0.606, places=2)

    def test_girder_n0_strips_truss(self):
        craft = Craft.load(STIFF)
        before = [p for p in craft.parts if p.name == "trussPiece1x"]
        self.assertGreaterEqual(len(before), 3)
        gone = girder_ring(craft, 0)
        self.assertEqual(len(gone), len(before))
        self.assertFalse([p for p in craft.parts if p.name == "trussPiece1x"])
        for tank in axial_tanks(craft):
            self.assertFalse(any("trussPiece" in t for t in tank.links))
        self.assertEqual(strip_girders(craft), [])

    def test_insert_wheel_and_presmat(self):
        craft = Craft.load(T7)
        core = find_core(craft)
        first = axial_tanks(craft)[0]
        self.assertEqual(core.att_n.get("bottom"), first.token)
        insert_wheel(craft)
        wheel = [p for p in craft.parts if p.name == "sasModule"][0]
        first = axial_tanks(craft)[0]
        self.assertEqual(core.att_n.get("bottom"), wheel.token)
        self.assertEqual(wheel.att_n.get("top"), core.token)
        self.assertEqual(wheel.att_n.get("bottom"), first.token)
        self.assertEqual(first.att_n.get("top"), wheel.token)
        self.assertLess(wheel.pos[1], core.pos[1])
        self.assertLess(first.pos[1], wheel.pos[1])
        pres = [p for p in craft.parts if p.name == "sensorBarometer"]
        self.assertEqual(len(pres), 1)
        self.assertEqual(pres[0].srf_n, f"srfAttach,{core.token}")

    def test_wheel_count_three_heaviest(self):
        craft = Craft.load(T7)
        insert_wheel(craft, count=3)
        wheels = [p for p in craft.parts if p.name == "sasModule"]
        self.assertEqual(len(wheels), 3)
        core = find_core(craft)
        first = axial_tanks(craft)[0]
        self.assertEqual(core.att_n.get("bottom"), wheels[0].token)
        self.assertEqual(wheels[-1].att_n.get("bottom"), first.token)
        self.assertEqual(first.att_n.get("top"), wheels[-1].token)
        for w in wheels[1:]:
            self.assertEqual(w.autostrut_mode, "Heaviest")
            self.assertEqual(w.rigid_attachment, "True")

    def test_autostrut_stack_without_hs_or_chute(self):
        craft = Craft.load(T7)
        self.assertFalse(find_chutes(craft))
        self.assertFalse(any(p.name == "proceduralHeatshield" for p in craft.parts))
        autostrut_stack(craft)
        engine = find_engine(craft)
        self.assertEqual(engine.istg, 0)
        self.assertEqual(engine.sqor, 0)
        for p in craft.parts:
            if p.attm != 0:
                continue
            self.assertEqual(p.autostrut_mode, "Heaviest")
            self.assertEqual(p.rigid_attachment, "True")

    def test_cone_insert_on_okto_top(self):
        craft = Craft.load(LOFT)
        chute = find_chutes(craft)[0]
        tok = chute.token
        craft.parts = [p for p in craft.parts if p.token != tok]
        for p in craft.parts:
            p.links = [t for t in p.links if t != tok]
            p.att_n = {k: v for k, v in p.att_n.items() if v != tok}
        core = find_core(craft)
        self.assertEqual(core.name, "probeCoreOcto_v2")
        inserted = set_nylon_chute(craft, "cone")
        self.assertEqual(inserted.name, "RC_cone")
        self.assertEqual(inserted.att_n.get("bottom"), core.token)
        self.assertEqual(core.att_n.get("top"), inserted.token)
        engine = find_engine(craft)
        self.assertEqual(engine.istg, 0)
        self.assertEqual(engine.sqor, 0)
        self.assertEqual(inserted.istg, 1)
        self.assertEqual(inserted.sqor, 0)
        para = _mod(inserted, "RealChuteModule").of("PARACHUTE")[0]
        self.assertEqual(para.get("deployedDiameter"), "50")
        self.assertEqual(para.get("material"), "Nylon")

    def test_cone_insert_refuses_stayputnik(self):
        craft = Craft.load(T7)
        with self.assertRaises(CraftError) as ctx:
            set_nylon_chute(craft, "cone")
        self.assertIn("no top", str(ctx.exception).lower())
        self.assertIn("OKTO", str(ctx.exception))

    def test_two_stage_refuses_locked_terrier(self):
        craft = Craft.load(T7_WHEEL)
        n = len(craft.parts)
        with self.assertRaises(CraftError) as ctx:
            insert_two_stage(craft, unlocked=set())
        self.assertIn("LOCKED", str(ctx.exception))
        self.assertIn(TERRIER_NAME, str(ctx.exception))
        self.assertEqual(len(craft.parts), n)
        self.assertFalse(any(p.name == TERRIER_NAME for p in craft.parts))

    def test_two_stage_unlocked_fed_staging(self):
        craft = Craft.load(LOFT)
        insert_two_stage(craft, upper=1, unlocked={"advRocketry"})
        valiant = find_engine(craft)
        terrier = next(p for p in craft.parts if p.name == TERRIER_NAME)
        dec = next(p for p in craft.parts if p.name == DECOUPLER_NAME)
        chute = find_chutes(craft)[0]
        last = axial_tanks(craft)[-1]
        self.assertEqual(valiant.name, "restock-engine-125-valiant")
        self.assertEqual(last.att_n.get("bottom"), valiant.token)
        self.assertEqual(valiant.att_n.get("top"), last.token)
        self.assertEqual(valiant.istg, 0)
        self.assertEqual(valiant.sqor, 0)
        self.assertEqual(dec.istg, 1)
        self.assertEqual(dec.sqor, 0)
        self.assertEqual(terrier.istg, 2)
        self.assertEqual(terrier.sqor, 0)
        self.assertEqual(chute.istg, 3)
        self.assertEqual(chute.sqor, 0)
        self.assertGreater(terrier.pos[1], dec.pos[1])
        self.assertGreater(dec.pos[1], last.pos[1])
        text = dump_attach_fuel(craft, catalog=Catalog.stock())
        self.assertIn("FED  last tank reaches engine", text)
        self.assertNotIn("BLOCKED", text)

    def test_heatshield_modules_disc_is_vab_dish(self):
        mods, res = heatshield_modules(top=1.25, bottom=0.0, length=0.2, ablator=80)
        cone = next(m for m in mods if m.get("name") == "ProceduralShapeBezierCone")
        self.assertEqual(cone.get("topDiameter"), "1.25")
        self.assertEqual(cone.get("bottomDiameter"), "0")
        self.assertEqual(res[0].get("name"), "Ablator")
        self.assertEqual(res[0].get("amount"), "80")
        adapter, _ = heatshield_modules(top=1.427, bottom=1.25, length=0.2)
        cone = next(m for m in adapter if m.get("name") == "ProceduralShapeBezierCone")
        self.assertEqual(cone.get("topDiameter"), "1.427")
        self.assertEqual(cone.get("bottomDiameter"), "1.25")

    def test_insert_hs_refuses_false_cross_feed_leaves_fed_engine(self):
        craft = Craft.load(T7_WHEEL)
        last = axial_tanks(craft)[-1]
        engine = find_engine(craft)
        last_tok = last.token
        engine_tok = engine.token
        n_parts = len(craft.parts)
        with self.assertRaises(CraftError) as ctx:
            insert_heatshield(craft, kind="disc")
        self.assertIn("fuelCrossFeed=False", str(ctx.exception))
        self.assertIn("starve", str(ctx.exception).lower())
        last = axial_tanks(craft)[-1]
        engine = find_engine(craft)
        self.assertEqual(last.token, last_tok)
        self.assertEqual(engine.token, engine_tok)
        self.assertEqual(last.att_n.get("bottom"), engine.token)
        self.assertEqual(engine.att_n.get("top"), last.token)
        self.assertEqual(len(craft.parts), n_parts)
        self.assertFalse(any(p.name == "proceduralHeatshield" for p in craft.parts))

    def test_c477_fuel_dump_blocked_through_inline_hs(self):
        craft = Craft.load(T7_PROC_HS)
        last = axial_tanks(craft)[-1]
        engine = find_engine(craft)
        hs = next(p for p in craft.parts if p.name == "proceduralHeatshield")
        self.assertEqual(last.att_n.get("bottom"), hs.token)
        self.assertEqual(hs.att_n.get("top"), last.token)
        self.assertEqual(hs.att_n.get("bottom"), engine.token)
        self.assertEqual(engine.att_n.get("top"), hs.token)
        text = dump_attach_fuel(craft, catalog=Catalog.stock())
        self.assertIn(f"{last.token} -> {hs.token} -> {engine.token}", text)
        self.assertIn("fuelCrossFeed=False", text)
        self.assertIn("res=Ablator", text)
        self.assertIn("Kerosene", text)
        self.assertIn("BLOCKED  proceduralHeatshield fuelCrossFeed=False", text)
        self.assertIn("engine starved", text)

    def test_c477_payload_hs_is_clearance_not_node_math(self):
        """T-503: C-477 rebuilt T-500 half 0.5 (sas-hs 0.591 / hs-tank 0.8125)."""
        craft = Craft.load(T7_HS_CONE)
        sas = next(p for p in craft.parts if p.name == "sasModule")
        hs = next(p for p in craft.parts if p.name == "proceduralHeatshield")
        first = axial_tanks(craft)[0]
        last = axial_tanks(craft)[-1]
        engine = find_engine(craft)
        cone = next(
            m for m in hs.modules if m.get("name") == "ProceduralShapeBezierCone"
        )
        self.assertEqual(sas.att_n.get("bottom"), hs.token)
        self.assertEqual(hs.att_n.get("top"), sas.token)
        self.assertEqual(hs.att_n.get("bottom"), first.token)
        self.assertEqual(last.att_n.get("bottom"), engine.token)
        self.assertEqual(engine.istg, 0)
        self.assertEqual(engine.sqor, 0)
        self.assertEqual(cone.get("bottomDiameter"), "0")
        half = heatshield_place_half(0.2, catalog=Catalog.stock())
        self.assertAlmostEqual(half, 0.5, places=4)
        self.assertAlmostEqual(sas.pos[1] - hs.pos[1], 0.09111 + half, places=4)
        self.assertAlmostEqual(hs.pos[1] - first.pos[1], half + 0.3125, places=4)
        self.assertGreater(sas.pos[1] - hs.pos[1], 0.191)
        self.assertGreater(hs.pos[1] - first.pos[1], 0.4125)
        text = dump_attach_fuel(craft, catalog=Catalog.stock())
        self.assertIn("FED  last tank reaches engine", text)
        self.assertNotIn("BLOCKED", text)

    def test_insert_hs_payload_leaves_collider_clearance(self):
        cat = Catalog.stock()
        craft = Craft.load(T7_WHEEL)
        sas = next(p for p in craft.parts if p.name == "sasModule")
        first = axial_tanks(craft)[0]
        last = axial_tanks(craft)[-1]
        engine = find_engine(craft)
        hs = insert_heatshield(craft, kind="disc", payload=True, catalog=cat)
        cone = next(m for m in hs.modules if m.get("name") == "ProceduralShapeBezierCone")
        self.assertEqual(cone.get("bottomDiameter"), "0")
        min_half = heatshield_clearance_half(0.2)
        half = heatshield_place_half(0.2, catalog=cat)
        self.assertAlmostEqual(min_half, 0.1 + HS_COLLIDER_OVERSHOOT, places=9)
        self.assertGreaterEqual(half, min_half)
        self.assertAlmostEqual(half, 0.5, places=4)
        self.assertAlmostEqual(sas.pos[1] - hs.pos[1], 0.09111 + half, places=4)
        self.assertGreater(sas.pos[1] - hs.pos[1], 0.191)
        tank_half = 0.3125
        self.assertAlmostEqual(hs.pos[1] - first.pos[1], half + tank_half, places=4)
        self.assertGreater(hs.pos[1] - first.pos[1], 0.4125)
        self.assertEqual(sas.att_n.get("bottom"), hs.token)
        self.assertEqual(hs.att_n.get("bottom"), first.token)
        self.assertEqual(last.att_n.get("bottom"), engine.token)
        self.assertEqual(engine.att_n.get("top"), last.token)
        self.assertEqual(engine.istg, 0)
        self.assertEqual(engine.sqor, 0)
        text = dump_attach_fuel(craft, catalog=cat)
        self.assertIn("FED  last tank reaches engine", text)
        self.assertNotIn("BLOCKED", text)

    def test_insert_inline_hs_bumps_node_half_to_clearance(self):
        cat = Catalog.stock()
        craft = Craft.load(T7_WHEEL)
        sas = next(p for p in craft.parts if p.name == "sasModule")
        first = axial_tanks(craft)[0]
        mods, res = heatshield_modules(top=1.25, bottom=0.0, length=0.2)
        hs = CraftPart(name="proceduralHeatshield", istg=-1, dstg=0)
        hs.modules = mods
        hs.resources = res
        insert_inline(craft, sas, first, hs, catalog=cat, new_half=0.1)
        half = heatshield_place_half(0.2, catalog=cat)
        self.assertAlmostEqual(sas.pos[1] - hs.pos[1], 0.09111 + half, places=4)
        self.assertGreater(hs.pos[1] - first.pos[1], 0.4125)
        self.assertGreaterEqual(half, heatshield_clearance_half(0.2))


class TestLiquidNotSolidFuel(unittest.TestCase):
    def test_pad_pbc_stays_solidfuel(self):
        text = pad_pbc().dumps()
        self.assertIn("SolidFuel", text)
        mods, _res = liquid_cylinder(1.25, 0.625)
        fuel = next(m for m in mods if m.get("name") == "ModuleFuelTanks")
        self.assertEqual(fuel.get("type"), "Default")
        names = [c.get("name") for c in fuel.of("TANK")]
        self.assertEqual(names, ["Kerosene", "LqdOxygen"])
        srb = procedural_cylinder(0.625, 1.4)
        self.assertEqual(
            next(m for m in srb if m.get("name") == "ModuleFuelTanks").get("type"),
            "SolidFuel",
        )

    def test_liquid_redstone_1500(self):
        self.assertEqual(proc_volume(1.25, 1.222), 1500)
        mods, _res = liquid_cylinder(1.25, 1.222, texture="RedstoneStripes")
        shape = next(m for m in mods if m.get("name") == "ProceduralPart")
        self.assertEqual(shape.get("textureSet"), "RedstoneStripes")
        fuel = next(m for m in mods if m.get("name") == "ModuleFuelTanks")
        self.assertEqual(fuel.get("volume"), "1500")
        self.assertEqual(fuel.get("type"), "Default")


class TestCli(unittest.TestCase):
    def test_clone_then_tanks_cli(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kspstuff-hop-valiant-t3-pbc.craft"
            rc = cmd_craft(
                [
                    "clone",
                    str(T7),
                    "--name",
                    "kspstuff-hop-valiant-t3-pbc",
                    "--out",
                    str(dest),
                ]
            )
            self.assertEqual(rc, 0)
            rc = cmd_craft(["tanks", str(dest), "--count", "3", "--kind", "proc"])
            self.assertEqual(rc, 0)
            craft = Craft.load(dest)
            self.assertEqual(craft.name, "kspstuff-hop-valiant-t3-pbc")
            tanks = axial_tanks(craft)
            self.assertEqual(len(tanks), 3)
            self.assertEqual(tanks[0].name, "proceduralTankRealFuels")
            self.assertEqual(_mod(tanks[0], "ModuleFuelTanks").get("type"), "Default")

    def test_liquid_texture_and_girders_strip_cli(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kspstuff-hop-valiant-proc-redstone-cli.craft"
            rc = cmd_craft(
                [
                    "clone",
                    str(STIFF),
                    "--name",
                    dest.stem,
                    "--out",
                    str(dest),
                ]
            )
            self.assertEqual(rc, 0)
            rc = cmd_craft(
                [
                    "liquid",
                    str(dest),
                    "--count",
                    "4",
                    "--diameter",
                    "1.25",
                    "--length",
                    "1.222",
                    "--texture",
                    "RedstoneStripes",
                ]
            )
            self.assertEqual(rc, 0)
            rc = cmd_craft(["girders", str(dest), "-n", "0"])
            self.assertEqual(rc, 0)
            craft = Craft.load(dest)
            self.assertFalse([p for p in craft.parts if p.name == "trussPiece1x"])
            tanks = axial_tanks(craft)
            self.assertEqual(len(tanks), 4)
            shape = _mod(tanks[0], "ProceduralPart")
            self.assertEqual(shape.get("textureSet"), "RedstoneStripes")
            fuel = _mod(tanks[0], "ModuleFuelTanks")
            self.assertEqual(fuel.get("volume"), "1500")

    def test_fuel_cli_c477_blocked(self):
        import io
        from contextlib import redirect_stdout

        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cmd_craft(["fuel", str(T7_PROC_HS)])
        text = buf.getvalue()
        self.assertEqual(rc, 2)
        self.assertIn("BLOCKED  proceduralHeatshield fuelCrossFeed=False", text)
        self.assertIn("res=Ablator", text)
        self.assertIn("attN ", text)

    def test_heatshield_payload_cli_fed_clearance(self):
        import io
        import tempfile
        from contextlib import redirect_stdout

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "kspstuff-hop-valiant-t7-wheel-hs-payload-pbc.craft"
            rc = cmd_craft(
                ["clone", str(T7_WHEEL), "--name", dest.stem, "--out", str(dest)]
            )
            self.assertEqual(rc, 0)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_craft(["heatshield", str(dest), "--kind", "disc", "--payload"])
            self.assertEqual(rc, 0)
            craft = Craft.load(dest)
            hs = next(p for p in craft.parts if p.name == "proceduralHeatshield")
            sas = next(p for p in craft.parts if p.name == "sasModule")
            last = axial_tanks(craft)[-1]
            engine = find_engine(craft)
            min_half = heatshield_clearance_half(0.2)
            self.assertGreaterEqual(
                sas.pos[1] - hs.pos[1], 0.09111 + min_half - 1e-6
            )
            self.assertGreater(sas.pos[1] - hs.pos[1], 0.191)
            self.assertEqual(last.att_n.get("bottom"), engine.token)
            self.assertEqual(engine.sqor, 0)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = cmd_craft(["fuel", str(dest)])
            self.assertEqual(rc, 0)
            self.assertIn("FED", buf.getvalue())


class TestFuelCrossFeedCfg(unittest.TestCase):
    def test_cache_parses_fuel_cross_feed_false(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / "ModuleManager.ConfigCache"
            cache.write_text(
                "url = ProceduralParts/Parts/Structural/Heatshield\n"
                "PART\n{\n"
                "name = proceduralHeatshield\n"
                "fuelCrossFeed = False\n"
                "}\n",
                encoding="utf-8",
            )
            cat = scan_config_cache(cache)
            part = cat.get("proceduralHeatshield")
            self.assertIsNotNone(part)
            self.assertIs(part.fuel_cross_feed, False)
            self.assertIn("Heatshield", part.cfg_path)

    def test_gamedata_cfg_parses_fuel_cross_feed_false(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cfg = (
                root
                / "GameData"
                / "ProceduralParts"
                / "Parts"
                / "Structural"
                / "Heatshield.cfg"
            )
            cfg.parent.mkdir(parents=True)
            cfg.write_text(
                "PART\n{\n"
                "name = proceduralHeatshield\n"
                "fuelCrossFeed = False\n"
                "}\n",
                encoding="utf-8",
            )
            cat = scan_gamedata(root)
            part = cat.get("proceduralHeatshield")
            self.assertIs(part.fuel_cross_feed, False)
            self.assertEqual(part.cfg_path, str(cfg))
            text = dump_attach_fuel(Craft.load(T7_PROC_HS), catalog=cat)
            self.assertIn("BLOCKED", text)
            self.assertIn("fuelCrossFeed=False", text)
            self.assertIn("Heatshield.cfg", text)

    def test_stock_hs_is_false_without_gamedata(self):
        hs = Catalog.stock().get("proceduralHeatshield")
        self.assertIs(hs.fuel_cross_feed, False)
        self.assertAlmostEqual(hs.nodes["top"][1], 0.5, places=4)
        self.assertAlmostEqual(hs.nodes["bottom"][1], -0.5, places=4)
        tank = Catalog.stock().get("proceduralTankRealFuels")
        self.assertIsNone(tank.fuel_cross_feed)
