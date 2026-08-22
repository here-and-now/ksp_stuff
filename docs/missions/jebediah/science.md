# jebediah science dump (tickets T-020 then T-019)

science: tickets
flight: jebediah
craft: kspstuff-hop-valiant-east-t3-pbc
at: splash
body: Earth
recover_banks: yes
notes: Gus T-014 capable yes east-t3. Not t7-splash. Bank 13.2632
  need ~1.74. Splash goo 2.40 closes 15. Pair 3.20 overshoots.
  Sequential: T-020 splash TELEMETRY first (30 s, Shores), then
  T-019 goo 641 s global. Tape 0.75. Do not transmit. Do not co-run
  geiger (PAW not bind hardware). Do not Toggle TELEMETRY airborne.
  Skip leftover FlyingLow geiger 0.32 and Forest High TELEMETRY 1.51.
  Do not bind FlyingLow@Water or Water biome until hop-to-water jsonl
  heading 090. 23-15/22-57/22-03 never 090. 23-15 modules gone after
  220 m/s is Lars, not an unbind.

## Splash
- experiment: kerbalism_TELEMETRY
  situation: SrfSplashed
  biome: Shores
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreSphere_v2
  instrument: Stayputnik PAW (no Science-category part) — tech start — unlocked yes
  duration_s: 30
  ec_rate: 0.052
  recover_banks: yes
  est: 0.80
  seq: 0
  ticket: T-020
- experiment: mysteryGoo
  situation: SrfSplashed
  biome: global
  experiment_id: mysteryGoo
  part: GooExperiment
  instrument: Mystery Goo Containment Unit (GooExperiment) — tech start — unlocked yes
  duration_s: 641
  ec_rate: 0.18
  recover_banks: yes
  est: 2.40
  seq: 1
  ticket: T-019
