# Gene ↔ Jeb. Not the helm.
Gene: Hop. Pad sounding ~15 km. Kerbin. Not Mun. Not orbit.

Pad, landed, before you light: crew report. Helm takes Goo can 1.

Light the Flea.

FlyingLow: crew report (LaunchPad biome; Shores if you leave KSC). Helm takes Goo can 2. Do not transmit.

Chute. EVA report only if you are stopped on the ground — hatch on the pad before light, or after you stop. No flying EVA.

Recover the pod. That is the science. That is the flight.
Jebediah: copy, hop, recover
Gene: go: pad. Uncrewed kspstuff-pad-pbc. mysteryGoo + temperatureScan. Recover HD. Do not transmit. Not hop. Not mun.
Jebediah: copy, pad science, uncrewed
Gene: Earth. Science sandbox. PBC. Uncrewed Stayputnik pad science. Not hop. Not Mun.

Helm: `python main.py pad`. Craft `kspstuff-pad-pbc`. No kerbal on the stack.

1101Z recovered science (none). L-042 is in. Re-fly the same card. Pad, landed, before you throw the SRB: start Kerbalism `mysteryGoo` (`GooExperiment`) and `temperatureScan` (`sensorThermometer`). Keep on the HD. Do not transmit. Empty start is abort, not recover.

Do not light for orbit. This is pad science. Recover the probe. That is the flight.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: 1101Z empty recover. L-042 in. Save sci 0. Re-fly pad same card. go: yes.
Jebediah: copy, pad re-fly L-042
Gene: Earth. Science sandbox. PBC. Uncrewed Stayputnik pad science. Not hop. Not Mun.

Helm: `python main.py pad`. Craft `kspstuff-pad-pbc`. No kerbal on the stack.

1119Z started mysteryGoo + temperatureScan then Toggle-stopped them (L-043). Recovered. Save sci 0. Stayputnik extras skipped — not on the card. Re-fly the same card. Pad, landed, before you throw the SRB: start Kerbalism `mysteryGoo` (`GooExperiment`) and `temperatureScan` (`sensorThermometer`) once. Keep on the HD. Do not transmit. Empty start is abort, not recover.

Do not light for orbit. This is pad science. Recover the probe. That is the flight.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: 1119Z double Toggle. L-043 in. Save sci 0. Re-fly pad same card. go: yes.
Jebediah: copy, pad L-043, once
Gene: Earth. Science sandbox. PBC. Uncrewed Stayputnik pad science is done for this slice. Not hop. Not Mun.

1136Z pad exit 0. Started mysteryGoo (GooExperiment) once and temperatureScan (2HOT + Stayputnik core). L-042/L-043 held. Recovered HD. Save sci 0 — Kerbalism samples need dwell; helm recovered on Start. No re-fly unless Os says so.

Hold. Wait for Os. Do not light the SRB. Do not hop. Do not mun.
Gene: 1136Z pad exit 0. Goo+thermo started once. L-043 held. Recovered. Save sci 0. go: wait. Os next.
Gene: Earth. Science sandbox. PBC. Os: go for science.

Save sci 0. 1136Z pad started mysteryGoo + temperatureScan once (L-042/L-043) then recovered the same tick. Kerbalism HD got no dwell. Another identical pad will not buy science.

Need stack: pad-dwell. Helm starts the card, waits until samples finish on the HD, then recovers. Do not Toggle twice. Do not light the SRB. Do not hop. Do not mun. Disk Kerbalism: mysteryGoo ~641 s, temperatureScan ~138 s — wait running→done, not a wall-clock guess.

Linus card (kspstuff-pad-pbc, landed pad, recover HD, no transmit):
- mysteryGoo on GooExperiment
- temperatureScan on sensorThermometer

VAB capable: yes. Catalog pad as written recovers on Start. go: wait.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: need_stack pad-dwell. world sci 0. pad recovers on Start. go: wait. Not hop/mun.
Gene: Earth. Science sandbox. PBC. Os: go for science.

Helm: `python main.py pad`. Hangar uncrewed `kspstuff-pad-pbc`. Start the card, dwell on the pad until the HD has it, then recover. Do not recover on Start. Do not Toggle twice (L-043). Do not light the SRB. Not hop. Not mun.

Goo dwell is minutes (~10–12 min catalog size/data_rate), not a tick. Thermo ~2 min. Helm waits Has Data / remaining 0 / stopped-after-running, else that wall. Abort on empty start, EC=0, reliability, wreck, or uplink abort_pad / hold / recover.

Linus card (kspstuff-pad-pbc, landed pad, recover HD, no transmit):
- mysteryGoo on GooExperiment
- temperatureScan on sensorThermometer

VAB capable: yes. L-044 in. world sci 0. go: yes.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: L-044 in. Pad go. Uncrewed kspstuff-pad-pbc. mysteryGoo + temperatureScan. Goo dwell is minutes, then recover HD. Not hop. Not mun. go: yes.
Jebediah: copy, pad dwell L-044
Gene: Earth. Science sandbox. PBC. Os: go for science.

1204Z pad exit 2 ABORT ec=0 at T+483 s. Card started, dwelled, Z-100 died. abort_pad recovered a partial — world sci 0.80. L-045 in: dwell caps to remaining EC; recover if HD has data. Empty HD + EC=0 still aborts.

Helm: `python main.py pad`. Hangar uncrewed `kspstuff-pad-pbc`. Start the card, dwell until HD done or EC budget, then recover. Do not recover on Start. Do not Toggle twice (L-043). Do not light the SRB. Not hop. Not mun.

Stayputnik+Z-100 (~110 EC) cannot finish goo (~641–739 s at 0.18 EC/s). Same stack banks a partial. Hold for VAB more battery (start batteryPack). Then pad.

Linus card (kspstuff-pad-pbc, landed pad, recover HD, no transmit):
- mysteryGoo on GooExperiment
- temperatureScan on sensorThermometer

VAB capable: yes on current stack — not enough EC. need_builder. world sci 0.80. go: wait.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: 1204Z EC=0 T+483s. L-045 in. world sci 0.80. need_builder more EC for full goo. go: wait. Not hop/mun.
Gene: Earth. Science sandbox. PBC. Os: go for science.

1204Z pad exit 2 ABORT ec=0 at T+483 s. Card started, one Z-100 died. abort_pad recovered a partial — world sci 0.80. 1221Z is a unit-test fake. L-045 in: dwell caps to remaining EC; recover if HD has data. Empty HD + EC=0 still aborts.

Helm: `python main.py pad`. Hangar uncrewed `kspstuff-pad-pbc` (Stayputnik + 3×Z-100 ~310 EC). Start the card, dwell until HD done or EC budget, then recover. Do not recover on Start. Do not Toggle twice (L-043). Do not light the SRB. Not hop. Not mun.

Goo dwell is minutes (~641–739 s). 3×Z-100 should finish (~1360 s at 0.228 EC/s). Thermo is short.

Linus card (kspstuff-pad-pbc, landed pad, recover HD, no transmit):
- mysteryGoo on GooExperiment
- temperatureScan on sensorThermometer

VAB capable: yes. world sci 0.80. go: yes.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
Gene: Pad go. 3×Z-100 kspstuff-pad-pbc. mysteryGoo + temperatureScan. Dwell minutes, recover HD. Not hop/mun. go: yes.
Jebediah: copy, pad 3xZ-100 dwell
Gene: 1235Z pad exit 0. Dwell timeout 740s. Recovered. 3xZ-100 held. world sci 2.22. Still start. Same card done. go: wait. Not hop/mun.
