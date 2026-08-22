# Seated jebediah. Canonical: docs/missions/jebediah/plan.md
mun_pe: 25000
suicide_start: 25000
parking_apo: 250000
parking_peri: 75000
suicide_throttle: 1
landing_pe: 18000
phase: hop-to-water
next: hop-to-water
expect_body: Earth
expect_peri_min: -500000
expect_apo_max: 50000
craft: kspstuff-hop-valiant-east-t3-pbc
hop_apo: 18000
go: yes
campaign: uncrewed
recommended: python main.py hop-to-water
emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
need_builder: none
need_science: none
need_stack: none
# T-013 go yes. Merge suicide-latch-until-vz. 22-57 Learn: latch held
# MET 79.2 thr 0 fuel 109.5; suicide MET 179.7 TTI recut lofted leftover;
# splash 119 m/s Shores heading never 090 horiz 8.1. sci 13.26 Δ0.
# T-023 vz latch in. T-016 hardware. Os: same brake, latched. T-014
# capable east-t3. T-008 parked. leftover n=0 hangar none. CLI
# recover-then-Hangar. hop_apo 18 km. Light vertical. After left_pad
# slew 0.4 heading 090 pitch 25 from up. Hold AP through burnout.
# Latch hop_apo. Suicide: arm TTI, hold until vz ≥ −20 or fuel=0.
# No flying Toggle. Wait splash. TELEMETRY then goo.
