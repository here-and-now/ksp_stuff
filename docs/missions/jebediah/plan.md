# Gene's plan. `python main.py phase` runs `phase:`.
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
craft: kspstuff-hop-valiant-east-one-pbc
hop_apo: 18000
go: yes
campaign: uncrewed
recommended: python main.py hop-to-water
emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
need_builder: none
need_science: none
need_stack: none
# Water sit. Bank 10.96 +0. Need ~4.04. FlyingHigh Shores spent.
# 16-11-58Z: east-bare slammed AP 65 at TWR 5, sheared, dump MET 11.7,
# apo 5.3 km, Shores 71 m, never splash. leftover unmatched east-bare
# — recover without lighting, then Hangar east-one. Do not light
# east-bare or the finned hang. Light vertical; after left_pad slew
# 10°/s to 65 at throttle 0.4; hold AP through burnout. Wait splash.
# hop_apo 18 km. Flea refused. Never rails. Never revert.
