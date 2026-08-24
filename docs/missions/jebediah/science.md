# jebediah science dump (tickets)

science: tickets
flight: jebediah
craft: kspstuff-hop-valiant-proc-long-pbc
recover_banks: yes
notes: dump of bound tickets + fly `science_ids`. Retired splash hang is not live.
  fly: T-081 cli=python main.py hop
  science_ids: temperatureScan,kerbalism_TELEMETRY

## Flying

- experiment: kerbalism_TELEMETRY
  situation: FlyingHigh@Forest
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreOcto_v2
  duration_s: 25
  ec_rate: 0.052
  recover_banks: yes
  ticket: T-069
- experiment: temperatureScan
  situation: SrfLanded@Forest
  experiment_id: temperatureScan
  part: sensorThermometer
  duration_s: 83
  ec_rate: 0.002
  recover_banks: yes
  ticket: T-077
- experiment: kerbalism_TELEMETRY
  situation: SrfLanded@Forest
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreOcto_v2
  duration_s: 30
  ec_rate: 0.052
  recover_banks: yes
  ticket: T-287
- experiment: kerbalism_TELEMETRY
  situation: SrfSplashed@Forest
  experiment_id: kerbalism_TELEMETRY
  part: probeCoreOcto_v2
  duration_s: 6
  ec_rate: 0.052
  recover_banks: yes
  ticket: T-288
- experiment: temperatureScan
  situation: SrfSplashed@Forest
  experiment_id: temperatureScan
  part: sensorThermometer
  duration_s: 138
  ec_rate: 0.002
  recover_banks: yes
  ticket: T-313
