# Linus board — science program

Query, then write. Do not copy Squad Start from memory.

```bash
python main.py world
python main.py parts --unlocked --module Experiment
python main.py tech start
python main.py science
```

Kerbalism Default: `MODULE Experiment` + `HardDrive` (time + EC). File
experiments (`kerbalism_TELEMETRY`, `temperatureScan`, `geigerCounter`)
credit R&D **while recording** — not on `vessel.recover()`. Goo is a
sample; that slot still wants recover. Do not transmit (omni-only, no
RA planner). Game `PreferencesScience.transmitScience = True` anyway.
PBC unmanned. Mk1 is locked (`simpleCommandModules`, 90). No
`crewReport` on a probe.

After Gus `capable: yes`, bind **that** craft in seated `science.md`.
Each line: `experiment_id`, `part`, `duration_s`, `ec_rate`. Card
`recover_banks: yes|no`. Missing part → `need_builder`. Gus sizes
`ec_rate × duration_s` before signing. `duration_s` is size/data_rate
(recording). Pad wall is that ×1.15+2.

---

## Banked (do not re-fly)

Live `persistent.sfs` (`python main.py world`): R&D `sci = 3.20062709`
+ Kerbalism `uncreditedScience = 0.011`. Still `start`. No hop vessel
in FLIGHTSTATE (`activeVessel = -1`). Asteroids only.

Cape `2026-08-20T12-35-42Z-pad` recovered HD: landed goo + Shores
thermo, then `sci = 2.2239902` + uncredited `0.476` (2.70 in the lab).
Hop `2026-08-20T15-58-12Z-hop` started TELEMETRY + thermo airborne,
died EC=0, **never recovered**. Those FlyingLow subjects were already
in R&D. Leftover `2026-08-20T17-02-13Z-hop` exit 0 (paused wreck,
`go_space_center`) **did not move sci**. `recover_banks` did not dump a
hop HD. No splash goo. Cape uncredited buffer flushed (~0.011 left).

| subject | sci / cap | scv | notes |
|---|---|---|---|
| `mysteryGoo@EarthSrfLanded` | 1.80 / 1.80 | 0 | **Earth-global.** Cape. Another Cape goo is 0. |
| `temperatureScan@EarthSrfLandedShores` | 0.90 / 0.90 | 0 | Shores only. Other biomes still pay. |
| `kerbalism_TELEMETRY@EarthFlyingLowShores` | 0.110 / 1.40 | 0.921 | 15-58-12Z hop, **partial**. 1.29 left. |
| `temperatureScan@EarthFlyingLowShores` | 0.401 / 2.10 | 0.809 | 15-58-12Z hop, **partial**. 1.70 left. |

Cape 2.70 + hop 0.512 = 3.21 lab. F-005: same Cape pad card is done.
Hop flying card (`docs/missions/jebediah/science.md`) is **spent** —
do not re-bind it as new. Remaining scv is still payable on a *new*
run if Gene asks.

HD assumption that failed: TELEMETRY 0.75 + thermo 0.45 = 1.20 MB vs
1.0 MB tape did **not** zero one subject. Both filed **partials**
(Kerbalism credits as data is produced; they never finished both
files). ~0.06 MB TELEMETRY + ~0.086 MB thermo fits the tape. "Both
will not file" was a complete-file claim. Wrong.

Earth RSS multipliers (Kopernicus): landed 0.3, splashed 0.4, flyingLow 0.7,
flyingHigh 0.9. FlyingLow < 50 km; space 35786 km. Cape biome = Shores.

Need **1.80** more for a 5-sci node.

---

## Hardware at `start` (unlocked Experiment parts)

| part | experiment_id | duration_s | ec_rate | HD |
|---|---|---|---|---|
| `GooExperiment` | `mysteryGoo` | 641 | 0.18 | private sample slot |
| `sensorThermometer` | `temperatureScan` | 138 | 0.002 | uses command HD |
| `probeCoreSphere_v2` | `temperatureScan` | 138 | 0.002 | same subject as 2HOT |
| `probeCoreSphere_v2` | `geigerCounter` | 497 | 0.005 | 0.5 MB — fills Stayputnik HD |
| `probeCoreSphere_v2` | `kerbalism_TELEMETRY` | 30 | 0.052 | 0.75 MB — **does not fit** 0.5 MB HD |
| `probeCoreSphere_v2` | `kerbalism_LITE` | 10 | 0.03 | 0.25 MB; **InSpace only** |
| `probeCoreSphere_v2` | `kerbalism_MITE` | 755 | 0.085 | polar orbit (`incl 70–120`) |
| `probeCoreSphere_v2` | `kerbalism_SITE` | 3645 | 0.15 | InSpace; 12.4 MB; 547 EC |
| `probeCoreSphere_v2` | `seismicScan` | 317248 | 0.0076 | landed@biomes; 200 MB; 2411 EC |
| `restock-goocanister-625-1` | `mysteryGoo` | 641 | 0.18 | same id as canister — not extra sci |

PBC Stayputnik HD = **0.5 MB**. `Engineer7500` (Start, KER tape) = **+0.5 MB**.
No solar. No parachute (`parachuteSingle` = survivability, 15). No barometer
(`sensorBarometer` = stability, 18).

Expected cap ≈ patched `scienceCap` × Earth dataValue (Cape 1.80 / 0.90
and FlyingLow thermo cap 2.10 match).

Craft on the shelf: `kspstuff-hop-flea-pbc` (Gus `capable: yes`). Not
bound for a new card. Leftover is gone — next hop is a Hangar.

---

## Still available at this tech

### 1. Finish FlyingLow Shores (same subjects, remaining scv)

Not a new card. Not the spent hop bind. Remaining:

| experiment_id | part | left | duration_s left | ec_rate | est. sci left |
|---|---|---|---|---|---|
| `kerbalism_TELEMETRY` | Stayputnik | scv 0.921 | ~28 | 0.052 | **1.29** |
| `temperatureScan` | `sensorThermometer` | scv 0.809 | ~112 | 0.002 | **1.70** |

Thermo alone → program **4.90**, **0.10 short of a node**. TELEMETRY
alone → 4.49, short. **Both remaining → ~6.19, unlocks.** Do not start
goo airborne. Do not co-run geiger (1.25 MB). Bind only if Gene asks.

### 2. Cape pad, new IDs (no hop)

Not the Cape goo+thermo card. Landed TELEMETRY is a **different**
subject from FlyingLow.

- `geigerCounter` on `probeCoreSphere_v2` — landed Shores `@Biomes`.
  497 s, 0.005 EC/s, 0.5 MB. Est. **1.2** → program **4.40**, short.
- `kerbalism_TELEMETRY` landed Shores. 30 s, 0.052 EC/s, 0.75 MB.
  Est. **0.6**. Needs `Engineer7500`. Do not run with geiger.

Together ~1.8 → ~5.00, razor. Do not also start landed goo/thermo.

### 3. Splash / other biomes

| experiment_id | situation | duration_s | ec_rate | est. sci | notes |
|---|---|---|---|---|---|
| `mysteryGoo` | FlyingLow (global) | 641 | 0.18 | **4.2** | hop will not finish |
| `mysteryGoo` | SrfSplashed (global) | 641 | 0.18 | **2.4** | water; **unlocks** if the can lives |
| `temperatureScan` | Surface@Water (or other) | 138 | 0.002 | 0.9 / 1.2 splash | Shores landed is done |
| `geigerCounter` | FlyingLow (global) | 497 | 0.005 | 2.8 | long for a hop |

No chute at Start. Splash is a living wreck on Water, 641 s, ~115 EC.

### 4. Not this program yet

- `kerbalism_LITE` / `SITE` / `MITE` — orbit (MITE polar).
- `seismicScan` — 3.7 d, 2411 EC, 200 MB. Needs solar + drive.
- Mk1 / `crewReport` / EVA — locked.
- Do not unlock. Next 5-sci nodes (`basicRocketry`, `engineering101`)
  are engines/tanks/decoupler, not a chute. Dedicated
  `kerbalism-geigercounter` at engineering101 is redundant with Stayputnik.

One line of future: remaining FlyingLow thermo+TELEMETRY on a new hop
is the 5-sci node; chute is still survivability (15).
