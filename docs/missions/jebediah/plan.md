# Gene's plan. `python main.py phase` runs `phase:`.
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
# Sit: 11-40-22Z hop clean. exit 0. sci 4.79 → 5.33 (+0.54). KSC empty. hangar none.
# Recover sit=landed recoverable=yes then recovered sit=landed — before dismiss.
# FAR apo 7.7 km, lithobrake landed 76 m, MET 67, EC 279→275. Flea spent.
# Next: Hangar kspstuff-hop-flea-pbc. python main.py hop. Do not phase leftover.
# Start FlyingLow geiger leftover 1.40 on kerbalism-geigercounter. Catalog 497 not a hang.
# Skip recovery crumbs 0.028. Skip thermo 0.045. Do not pad. Do not Hangar geiger-pbc.
# hop_apo 18 km is a cut wish. OffPlan lid 50 km. Never rails.
# Recover: wait sit=landed in Flight, then recover() when recoverable=yes BEFORE dismiss.
