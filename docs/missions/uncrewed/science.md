# uncrewed science dump (tickets)

science: tickets
flight: uncrewed
craft: kspstuff-hop-valiant-proc-loft-pbc
recover_banks: yes
notes: dump of bound tickets + fly `science_ids`. Retired splash hang is not live.
  fly: T-081 cli=python main.py hop
  science_ids: kerbalism_LITE,kerbalism_TELEMETRY

## Flying

- experiment: kerbalism_LITE
  situation: InSpaceLow
  experiment_id: kerbalism_LITE
  part: probeCoreSphere_v2
  duration_s: 10
  ec_rate: 0.03
  recover_banks: yes
  ticket: S-514
- experiment: kerbalism_TELEMETRY
  situation: InSpaceLow
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreSphere_v2
  duration_s: 30
  ec_rate: 0.052
  recover_banks: yes
  ticket: S-515
