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
go: wait
recommended: python main.py hop
emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
need_builder: none
need_science: none
need_stack: none
# Sit: 11-40-22Z hop clean. sci 4.79 → 5.33 (+0.54). KSC empty. hangar none.
# Recover sit=landed recoverable=yes then recovered sit=landed — before dismiss.
# FAR apo 7.7 km, lithobrake landed 76 m. Next: Hangar hop-flea-pbc. python main.py hop.
# FlyingLow geiger leftover 1.40. Recovery crumbs 0.028 skip. Do not pad.
# hop_apo 18 km is a cut wish. OffPlan lid 50 km. Never rails.
# Recover: wait sit=landed in Flight, then recover() when recoverable=yes BEFORE dismiss.
