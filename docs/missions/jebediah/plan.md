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
go: yes
campaign: none
recommended: python main.py phase hop
emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
need_builder: none
need_science: none
need_stack: none
# Sit: 12-22-36Z hop abort. exit 2 not recoverable. sci 6.35 (+0).
# Crash UI detect-now: MET 65.4 alt 74.1 q=0 flying recoverable=no. No wait-landed.
# leftover PRELAUNCH hop-flea-pbc. Skip Hangar. Keep Flea. Hammer-far waits.
# FlyingLow geiger leftover 0.32 on kerbalism-geigercounter. Catalog 497 not hang.
# Skip thermo 0.045. Do not pad. Do not Hangar hop-flea / geiger-pbc / hammer-far.
# hop_apo 18 km is a cut wish. OffPlan lid 50 km. Never rails.
# Crash UI: log sit/recoverable/met/alt/q; recover() if yes; else Space Center/Close abort.
# Do not unpause-spam recover after Catastrophic when recoverable=no.
# Living recover: wait sit=landed then recover() BEFORE dismiss.
