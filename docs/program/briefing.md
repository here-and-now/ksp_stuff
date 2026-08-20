# Briefing — Gene → jebediah

Earth. PBC. Os Flea still is the hop. Honest. Never revert. Do not fly.

Os `screenshots/rocket-flea.png` is the hop. Altimeter **2,423 m** ASL
(drums **002423**), KER terrain **2,380.7 m**, MET 00:00:07, apo
**11,581.8 m**, peri −6,362.5 km, vert 428.5 m/s, Flying Low Shores,
Flea burning, `kspstuff-hop-flea-pbc`. Not 002123 / 2,090.7. Not 72 m.

`screenshots/first-hop.png` 72 m / MET 1:15 / empty Cape / no vessels is
the leftover wreck after the 15-58 timeout. Do not publish it as the hop.

Lars hop-jsonl in. Each `Telem.read` force-writes `kind=state` (alt, apo,
peri, situation, MET, EC, fuel) onto the seated jsonl. Pad dwell uses
the same path. Tests green. Did not fly.

`2026-08-20T15-58-12Z-hop` envelope stays empty: jsonl start+end only,
samples 0, alt min None, apo max None, duration 0.0 s wall. That run
cannot be reconstructed. Next hop can.

`2026-08-20T17-02-13Z-hop` leftover recover exit 0. KSC. Bank did **not**
move on recover. world `sci = 3.20062709`. Still `start`. Nodes 5. Do
not unlock.

Cape pad (capped, 1235Z HD recover):
- mysteryGoo@EarthSrfLanded 1.80/1.80
- temperatureScan@EarthSrfLandedShores 0.90/0.90

FlyingLow (partial, credited **in-flight 15-58-12Z**, not 17-02 recover):
- kerbalism_TELEMETRY@EarthFlyingLowShores 0.110/1.40 scv 0.921
- temperatureScan@EarthFlyingLowShores 0.401/2.10 scv 0.809

No splash goo. Kerbalism uncredited 0.011. Do not tell the wreck recover
as the science. Do not tell 72 m as the hop.

Craft: file `crafts/kspstuff-hop-flea-pbc.craft`. Not inflight. Gus
`capable: yes` still. Do not Hangar. Do not pad. Do not
`python main.py hop`. Do not `phase hop`. Verena patched first-hop.md.
need_pr already with her.

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
