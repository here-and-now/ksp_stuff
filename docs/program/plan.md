# Seated jebediah. Canonical: docs/missions/jebediah/plan.md
mun_pe: 25000
suicide_start: 25000
parking_apo: 250000
parking_peri: 75000
suicide_throttle: 1
landing_pe: 18000
phase: hop
next: hop
expect_body: Earth
expect_peri_min: -500000
expect_apo_max: 50000
craft: kspstuff-hop-flea-pbc
hop_apo: 18000
go: yes
recommended: python main.py hop
emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
need_builder: none
need_science: none
need_stack: none
# Sit: living hop. Start FlyingLow geiger leftover 2.10 on kerbalism-geigercounter.
# Catalog 497 s is not a hang expect. Recover HD (recovery@EarthFlew leftover 0.17).
# Hangar hop-flea-pbc (KSC empty; hop refuses pad/geiger names). Do not pad.
# hop_apo 18 km is a cut wish. OffPlan lid 50 km.
# FAR apo 7.5 km held (10-42-32Z living 199 m; 10-47-59Z / 11-09-13Z lithobrake 75 m).
# Lars 11-09-13Z: recover() while still Flight at ≤250 m; post-dismiss pre_launch is not the bank.
