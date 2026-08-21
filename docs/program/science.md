# Linus board — science program

Query, then write. Do not copy Squad Start from memory.

```bash
python main.py science-scan
python main.py world
python main.py parts --unlocked --search geiger
```

kRPC 0.6 has `get_Science` only. Disk is the scan. F-013: bind
`geigerCounter` only on `kerbalism-geigercounter`, never Stayputnik
PAW. File experiments credit while recording. Do not transmit. PBC
unmanned. Mk1 locked (`simpleCommandModules`, 90). Chute locked
(`survivability`, 15).

**Bound** `kspstuff-hop-valiant-pbc` → `docs/missions/jebediah/science.md`.
Working goal **15**. Bank **6.35** → need **~8.65**. leftover PRELAUNCH
`kspstuff-hop-flea-pbc` is Gene hangar, not this stack. Do not re-pad
Cape. Do not bind 497 s / 641 s as complete.

---

## Banked (do not re-fly)

Live `sci = 6.3526` (desk). Unlocked: **`start`, `engineering101`,
`basicRocketry`**. KSC leftover PRELAUNCH hop-flea. Do not recover
Ast. XRL-564.

Save subjects (cap − sci). Missing id = unstarted:

| subject | sci/cap | left | honest |
|---|---|---|---|
| `geigerCounter@EarthSrfLandedShores` | 1.20/1.20 | 0 | **capped** — not Cape again |
| `mysteryGoo@EarthSrfLanded` | 1.80/1.80 | 0 | **capped** Earth-global (F-005) |
| `kerbalism_TELEMETRY@EarthSrfLandedShores` | 0.60/0.60 | 0 | **capped** |
| `kerbalism_TELEMETRY@EarthFlyingLowShores` | 1.40/1.40 | 0 | **capped** |
| `temperatureScan@EarthSrfLandedShores` | 0.90/0.90 | 0 | **capped** |
| `recovery@EarthFlew` | 5.995/6.00 | ~0 | **gone** |
| `temperatureScan@EarthFlyingLowShores` | 2.055/2.10 | **0.045** | crumbs — skip |
| `geigerCounter@EarthFlyingLow` | 2.484/2.80 | **0.316** | crumbs — not a node |

Need **~8.65** for `survivability` (15). Leftover **0.36** does not
pay it. Same lithobrake Flea will not.

Caps from Kerbalism value × situation (surface 0.3, splash 0.4,
FlyingLow 0.7, FlyingHigh 0.9): geiger 4, thermo 3, TELEMETRY 2,
goo 6.

---

## Instruments on the capable craft

Gus `capable: yes` **`kspstuff-hop-valiant-pbc`**. hop_apo **18 km**
is a real cut. Does **not** finish 497 s / 641 s. FlyingHigh only if
Gene lofts **≥50 km** (hop.py OffPlan lid 50 km).

| experiment_id | instrument | tech | unlocked | on_craft |
|---|---|---|---|---|
| `geigerCounter` | `kerbalism-geigercounter` | e101 | **yes** | **yes** — not bound (497 s / tape) |
| `temperatureScan` | `sensorThermometer` (2HOT) | start | **yes** | **yes** — **bound** FlyingHigh |
| `mysteryGoo` | `GooExperiment` | start | **yes** | yes — skip 641 s |
| `kerbalism_TELEMETRY` | Stayputnik PAW | start | **yes** | hosted — **bound** FlyingHigh |

Stayputnik PAW is **not** the Geiger. `seismicScan` landing LOCKED.
LITE InSpace (e101, 10 s) — orbit. MITE `generalRocketry` LOCKED.
SITE `advRocketry` LOCKED. Crew eva/sample: Mk1 locked.

### Bound this sit — FlyingHigh shorts ~4.50 if finished (0.55+ short of 8.65)

| experiment_id | situation | duration_s | ec_rate | est. |
|---|---|---|---|---|
| `temperatureScan` | FlyingHigh **global** | **138** | 0.002 | **2.70** |
| `kerbalism_TELEMETRY` | FlyingHigh@Shores | **30** | 0.052 | **1.80** |

Skip FlyingHigh geiger **3.60** / 497 s (will not finish; tape vs
TELEMETRY). 8.10 catalog trio is not this hang. Do not co-run geiger
+ TELEMETRY on 1.0 MB tape. recover_banks **yes**. Do not transmit.

### Bundle A — Water (nearest other biome) ~9.1 if finished — not this card

Cape is Shores. East is Water. Valiant **has gimbal** — Gene if he
pitches east. hop.py does not.

| experiment_id | situation | duration_s | ec_rate | est. |
|---|---|---|---|---|
| `mysteryGoo` | SrfSplashed **global** | **641** | 0.18 | **2.40** sample — hang on water |
| `kerbalism_TELEMETRY` | SrfSplashed@Water | **30** | 0.052 | **0.80** |
| `temperatureScan` | Surface@Water | **138** | 0.002 | **1.20** |
| `geigerCounter` | Surface@Water | **497** | 0.005 | **1.20** |
| `temperatureScan` | FlyingLow@Water | **138** | 0.002 | **2.10** |
| `kerbalism_TELEMETRY` | FlyingLow@Water | **30** | 0.052 | **1.40** |

### Bundle C — FlyingLow goo 4.20 does not close 8.65 alone

`mysteryGoo` FlyingLow **global** 641 s / 0.18 / **4.20**. Do not brief
airborne goo as success.

---

## Out of reach / locked

InSpace LITE/MITE/SITE/TELEMETRY/geiger Space@VirtualBiomes — orbit.
`seismicScan` `sensorAccelerometer` **landing** LOCKED. Barometer
`stability` 18 LOCKED. ROCScience **advExploration** LOCKED.

---

## Horizon, not a bind

Ast. XRL-564 — InSpace someday. Do not recover the rock. Chute is
still 15.

One line of future: 8.65 is Water-finished (~9.1) or FlyingHigh-plus
one extra (~8.1 + 0.6). This card is the shorts (~4.50) **if** lofted.
Not another Flea lithobrake. Not leftover geiger 0.32.
