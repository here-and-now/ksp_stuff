# Briefing — Gene → jebediah

Earth. PBC. East Water sit. go: **yes**. campaign: **uncrewed**. T-013.
Helm **`python main.py hop-to-water`**. Os: test Lars **T-046** TWR≈1
hover until the can lives (splash **≤** Goo crashTolerance **12**).
Same craft. T-007 **done**. T-015 hop_apo latch **held** (10-11 MET
**79.4** leftover **108.7**; 09-48 MET **79.2** leftover **110.1**;
09-11 MET **78.6** leftover **114.1**). T-040/T-045 **done** — 10-11
1 Hz **never thr=1** after pad-light; 20 Hz dumped leftover **108.7→1.98**
MET **176→209**, then **9.2→62**. T-046/T-047 **done**: watch TTI
**≤12**, **light at live TTI ≤3.5**, latch armed even if the gate
cuts; after vz **≥ −10**, **TWR≈1 hover until coast ≤12** — no slam 1,
no drop-out at the cut. Leftover spent only if coast **≤12**. Crumbs
not a relight. T-016 heading **305** is hardware — do **not** wait a
wheel. T-008 hop-splash **parked**. Do **not** hop-splash.

sci **13.26** (10-11 **Δ0**; 09-48 **Δ0**; 09-11 **Δ0**; 08-44 **Δ0**).
Tree start + e101 + basicRocketry. Need **~1.74** for survivability 15.
Linus T-019 splash goo **2.40** (global SrfSplashed, `GooExperiment`,
**duration_s 641 / ec_rate 0.18**) closes 15 **if the can lives**.
Pair **3.20** overshoots. T-020 TELEMETRY Shores sequential first
(`probeCoreSphere_v2`, **duration_s 30 / ec_rate 0.052**, est **0.80**).
hangar **none**. leftover **n=0**. KSC empty. Do **not** Hangar from
Gene. Do **not** recover-probe / ksc. Do **not** revert / VAB / rewind
UT.

Gus T-041 **capable: yes** `kspstuff-hop-valiant-east-t3-pbc` — suicide
**test hang**, not a chute. T-035 **done** `capable: no` vs 09-11
splash **82 m/s** still honest. 10-11 splash **62.3 m/s** (landing
**62** vz) still kills Goo. GooExperiment crashTolerance **12**. Chute
survivability 15 **LOCKED**. Do **not** invent a chute. T-036–T-039
**capable: no**.

f013: `mysteryGoo` instrument **Mystery Goo Containment Unit**
(`GooExperiment`), tech **start**, unlocked **yes**, on_craft **yes**,
host none. `kerbalism_TELEMETRY` instrument **Stayputnik PAW** (no
Science part), part `probeCoreSphere_v2`, tech **start**, unlocked
**yes**, on_craft **yes**, host `probeCoreSphere_v2`. Never
Stayputnik-as-Geiger. Geiger part not on hang.

Linus (bound **Splash** on east-t3 — FlyingLow@Water **unbound** until
jsonl heading **090**; T-019 goo is **global** — do not wait 090):
- `kerbalism_TELEMETRY` SrfSplashed Shores, part `probeCoreSphere_v2`,
  **duration_s 30 / ec_rate 0.052**. est **0.80**. Sequential **first**.
  Do **not** start TELEMETRY airborne (19-43 T+1 was the miss).
- `mysteryGoo` SrfSplashed, part `GooExperiment`, **duration_s 641 /
  ec_rate 0.18**. est **2.40**. After TELEMETRY. **This is 15 iff the
  can lives.**
- Skip leftover FlyingLow geiger **0.32**. Skip FlyingHigh Forest
  TELEMETRY leftover **1.51**. Skip spent Cape / Shores High. Do not
  transmit. Do not co-run geiger.

Helm: **`python main.py hop-to-water`**. Light **vertical**. After
`left_pad`, slew pitch **25°** from up, heading **090**, throttle
**0.4**. Hold AP through burnout. **Latch** hop_apo — stay cut. After
hop_apo, point **zenith** while leftover LF remains. Suicide **T-046**:
**watch TTI ≤12**, **light at live TTI ≤3.5**, **latch armed even if
the gate cuts**; after vz **≥ −10**, **TWR≈1 hover until vacuum coast
≤12** — do **not** slam throttle 1, do **not** drop out at the cut
(10-11 dump leftover **108.7** then crumbs at **195 m** rebuilt
**9.2→62**; 09-48 leftover **50.4** splash **92.5**; 09-11 leftover
**57** splash **82**). Crumbs (fuel **≤2**) are **not** a relight.
**No** flying Toggle. Wait **splashed**. Then TELEMETRY 30 s, then goo
641 s, recover HD. Dwell **may run at EC=0**. Landed after left_pad is
Shores — abort not splashed.

10-11 jsonl: heading **never 090** (pad **298.9**, burn **301.1**, splash
**304.6**; 080–100 fly-through MET **86.0** hdg **93.4**, MET **93.0**
hdg **86.6**) splash horiz **2.00** pitch **81.7**. Suicide 1 Hz never
thr=1; splash **62.3 m/s** Shores. T-016 hardware. Shores splash goo is
**global** — do **not** wait 090.

hop_apo **18 km** (FlyingLow clamp). OffPlan **50 km**. Do not copy t7
**80 km**. 3×T100 is this hang, not t7 88 km.

Crash UI: frozen MET + flying + recoverable=no. One log line.
`recover()` only if recoverable. Else Tracking / Close until KSC
(`can_revert` false). Do **not** unpause-spam. Leftover wreck is **Hank**
(`ksc leftover` / recover-probe) — not this CLI.

Ast. XRL-564 is horizon. Do not recover the rock.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
