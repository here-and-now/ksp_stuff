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
expect_apo_max: 140000
craft: kspstuff-hop-valiant-pbc
hop_apo: 80000
go: yes
campaign: none
recommended: python main.py hop
emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
need_builder: none
need_science: none
need_stack: none
# Sit: leftover PRELAUNCH kspstuff-hop-flea-pbc vs seated Valiant.
# hop recovers unmatched without lighting, then Hangars valiant-pbc.
# Do not fly the Flea. Do not Hangar from this desk.
# Gus capable yes. Linus FlyingHigh shorts 138/0.002 + 30/0.052.
# hop_apo 80 km cut. OffPlan 140 km Space. File FlyingHigh ≥50 km.
# Shorts ~4.50 if finished — not 15. Skip FlyingLow crumbs. Do not pad.
# Never rails. Never revert. Crash UI: recover if yes else Space Center.
