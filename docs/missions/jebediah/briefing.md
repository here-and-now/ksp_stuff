# Briefing — Gene → jebediah

Earth. PBC. East Water sit. go: **yes**. campaign: **uncrewed**. T-013.
T-007 **done**. T-015 hop_apo latch **held** (22-57). T-023 leftover-LF
suicide **vz latch in**, **untested**. T-016 heading **301** is hardware
— do **not** wait a wheel. T-008 hop-splash **parked**. Do **not**
hop-splash. Os: same brake, latched.

sci **13.26** (22-57 **Δ0**). Tree start + e101 + basicRocketry. Need
**~1.74** for survivability 15. Linus: splash goo **2.40** closes 15.
Pair **3.20** overshoots. hangar **none**. leftover **n=0** disk. Pad
empty. Next CLI recover-then-Hangars east-t3 if a 22-57 wreck is still
live. Do **not** Hangar from Gene. Do **not** revert / VAB / rewind UT.

Gus `capable: yes` **`kspstuff-hop-valiant-east-t3-pbc`**. Stayputnik
stack-only, Engineer7500 + 16-S + 2HOT + Goo, **20×Z-100** (~2050 EC),
**3×FL-T100** + LV-T15 **Boattail**, **3× basicFin on lowest T100**.
Tape **1.0**. No chute. No RW (stability LOCKED). FAR on. TWR ~1.1 at
throttle **0.4**. Not t7-splash. Not 2×T100 east-fin/bare/one. Not Flea.
Do not pad. Do not transmit. Never rails. Never WarpTo.

f013: `mysteryGoo` instrument **Mystery Goo Containment Unit**
(`GooExperiment`), tech **start**, unlocked **yes**, on_craft **yes**,
host none. `kerbalism_TELEMETRY` instrument **Stayputnik PAW** (no
Science part), part `probeCoreSphere_v2`, tech **start**, unlocked
**yes**, on_craft **yes**, host `probeCoreSphere_v2`. Never
Stayputnik-as-Geiger. Geiger part not on hang.

Linus (bound **Splash** on east-t3 — FlyingLow@Water **unbound** until
jsonl heading **090**):
- `kerbalism_TELEMETRY` SrfSplashed, part `probeCoreSphere_v2`,
  **duration_s 30 / ec_rate 0.052**. est **0.80**. Sequential **first**.
  Do **not** start TELEMETRY airborne (19-43 T+1 was the miss).
- `mysteryGoo` SrfSplashed, part `GooExperiment`, **duration_s 641 /
  ec_rate 0.18**. est **2.40**. After TELEMETRY. **This is 15.**
- Skip leftover FlyingLow geiger **0.32**. Skip FlyingHigh Forest
  TELEMETRY leftover **1.51**. Skip spent Cape / Shores High. Do not
  transmit. Do not co-run geiger.

Helm: **`python main.py hop-to-water`**. Light **vertical**. After
`left_pad`, slew pitch **25°** from up, heading **090**, throttle
**0.4**. Hold AP through burnout. **Latch** hop_apo — stay cut. Do
**not** recut 0.4 when apo falls (22-57 MET **79.2** thr **0** fuel
**109.5** held). Leftover LF is **suicide** near Water: **arm on TTI**
(≤20 s, alt ≤8 km), **hold throttle 1 until vz ≥ −20 or fuel=0**. TTI
rising is **not** a recut. After hop_apo, point **zenith** while leftover
LF remains. **No** flying Toggle. Wait **splashed**. Then TELEMETRY 30 s,
then goo 641 s, recover HD. Dwell **may run at EC=0**. Landed after
left_pad is Shores — abort not splashed. 22-57 jsonl: heading **never
090** (pad **299**, burn **300**, splash **300/314**; 080–100 fly-throughs
not a hold) horiz **8.1** vs briefed **090**. Suicide MET **179.7** thr
**1**; TTI recut MET **183** vz **+19** after vz **−72**; relight lofted
leftover; splash **119 m/s** Shores. T-016 hardware. This hop tests the
**vz latch**.

hop_apo **18 km** (FlyingLow clamp). OffPlan **50 km**. Do not copy t7
**80 km** — that OffPlans a short loft. 2×T100 apo **12.3 km** vertical;
east tapes apo **3.66–12.1 km**. 3×T100 is this hang, not t7 88 km.

Crash UI: frozen MET + flying + recoverable=no. One log line.
`recover()` only if recoverable. Else Tracking / Close until KSC
(`can_revert` false). Do **not** unpause-spam.

Ast. XRL-564 is horizon. Do not recover the rock.

emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
