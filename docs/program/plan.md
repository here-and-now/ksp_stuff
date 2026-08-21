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
# leftover PRELAUNCH hop-flea-pbc unmatched: recover without light, then
# Hangar valiant-pbc. hop_apo 80 km. OffPlan 140 km. campaign none.
