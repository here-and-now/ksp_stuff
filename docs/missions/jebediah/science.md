# jebediah science dump (tickets)

science: tickets
flight: jebediah
craft: kspstuff-hop-valiant-t7-pbc
recover_banks: yes
notes: dump of bound tickets + fly `science_ids`. Retired splash hang is not live.
  fly: T-081 cli=python main.py hop
  science_ids: kerbalism_TELEMETRY,mysteryGoo,geigerCounter

## Flying

- experiment: kerbalism_TELEMETRY
  situation: FlyingHigh@Forest
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreSphere_v2
  duration_s: 25
  ec_rate: 0.052
  recover_banks: yes
  ticket: T-069
- experiment: mysteryGoo
  situation: FlyingHigh
  experiment_id: mysteryGoo
  part: GooExperiment
  duration_s: 641
  ec_rate: 0.18
  recover_banks: yes
  ticket: T-368
- experiment: geigerCounter
  situation: FlyingHigh
  experiment_id: geigerCounter
  part: kerbalism-geigercounter
  duration_s: 497
  ec_rate: 0.005
  recover_banks: yes
  ticket: T-369
