# Gene's plan. `python main.py phase` runs `phase:`.
mun_pe: 25000
suicide_start: 25000
parking_apo: 250000
parking_peri: 75000
suicide_throttle: 1
landing_pe: 18000
phase: hop
next: none
expect_body: Earth
expect_peri_min: -500000
expect_apo_max: 400000
craft: kspstuff-hop-valiant-proc-long-pbc
hop_apo: 50000
go: yes
cli: python main.py hop
campaign: uncrewed
science_ids: barometerScan,geigerCounter,mysteryGoo
emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
