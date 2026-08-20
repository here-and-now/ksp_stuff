# Briefing — Gene → jebediah

Earth. PBC. Os: leftover recovered. Honest. Never revert.

`2026-08-20T17-02-13Z-hop` clean leftover recover. exit 0. Skip Hangar.
No light. ~10 s. keep HD → paused wreck → finish wreck → dismissed
Flight Results. MET frozen 1:15. Envelope empty (samples=1). Still:
KSC, 1 Jan 1951 17:30, sci 3.2, toolbar no vessels, no crash UI.

Bank did **not** move on recover. world `sci = 3.20062709`. Still
`start`. Nodes 5. Do not unlock.

Cape pad (capped, 1235Z HD recover):
- mysteryGoo@EarthSrfLanded 1.80/1.80
- temperatureScan@EarthSrfLandedShores 0.90/0.90

FlyingLow (partial, credited **in-flight 15-58-12Z**, not 17-02 recover):
- kerbalism_TELEMETRY@EarthFlyingLowShores 0.110/1.40 scv 0.921
- temperatureScan@EarthFlyingLowShores 0.401/2.10 scv 0.809

No splash goo. Kerbalism uncredited 0.011 (was 0.476 after pad).
`recover_banks` added nothing. TELEMETRY+thermo both filed partial
despite HD 1.0 vs 1.20. Do not tell the wreck recover as the science.

Craft: file `crafts/kspstuff-hop-flea-pbc.craft`. Not inflight. Gus
`capable: yes` still. Do not Hangar. Do not pad. Do not
`python main.py hop`. Do not `phase hop`. Verena writes the hop.

Linus card still bound (not this CLI). `recover_banks: yes`. Do not
transmit. Do not co-run geiger. Splash goo off.

Flying.
- kerbalism_TELEMETRY on probeCoreSphere_v2 — duration_s 30 / ec_rate 0.052
- temperatureScan on sensorThermometer — duration_s 138 / ec_rate 0.002

Splash (not a hop start).
- mysteryGoo on GooExperiment — duration_s 641 / ec_rate 0.18
Do not start goo airborne.

hop_apo: 15000. expect_apo_max: 18000.

go: wait.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
