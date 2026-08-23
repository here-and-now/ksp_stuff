# jebediah science dump (tickets)

science: tickets
flight: jebediah
craft: kspstuff-hop-valiant-proc-stiff-pbc
recover_banks: yes
notes: dump of bound tickets + fly `science_ids`. Retired splash hang is not live.
  fly: T-081 cli=python main.py hop
  science_ids: temperatureScan,kerbalism_TELEMETRY,mysteryGoo

## Flying

- experiment: temperatureScan
  situation: FlyingLow@Grasslands
  experiment_id: temperatureScan
  part: sensorThermometer
  duration_s: 138
  ec_rate: 0.002
  recover_banks: yes
  ticket: T-070
- experiment: kerbalism_TELEMETRY
  situation: FlyingLow@Grasslands
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreOcto_v2
  duration_s: 30
  ec_rate: 0.052
  recover_banks: yes
  ticket: T-071
