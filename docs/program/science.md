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

**Bound** `docs/missions/jebediah/science.md` on Gus-signed
**`kspstuff-hop-valiant-east-one-pbc`**: FlyingLow@Water thermo **138 /
0.002 / 2.10** + TELEMETRY **30 / 0.052 / 1.40**. Same shorts. Not
spent Shores FlyingHigh. Not t7. leftover **east-bare / east-pbc** is
Gene hangar. Working goal **15**. Bank **10.96** → need **~4.04**. Do
not re-pad Cape. Do not re-fly spent FlyingHigh Shores.

---

## Banked (do not re-fly)

Live `sci = 10.9586` (desk). Unlocked: **`start`, `engineering101`,
`basicRocketry`**. leftover **east-bare / east-pbc** — Gene hangar,
not this bind. Desk leftover vessels n=0. Do not recover Ast. XRL-564.

Save leftovers (cap − sci). Missing id = unstarted:

| subject | sci/cap | left | honest |
|---|---|---|---|
| `geigerCounter@EarthSrfLandedShores` | 1.20/1.20 | 0 | **capped** — not Cape again |
| `mysteryGoo@EarthSrfLanded` | 1.80/1.80 | 0 | **capped** Earth-global (F-005) |
| `kerbalism_TELEMETRY@EarthSrfLandedShores` | 0.60/0.60 | 0 | **capped** |
| `kerbalism_TELEMETRY@EarthFlyingLowShores` | 1.40/1.40 | 0 | **capped** |
| `temperatureScan@EarthSrfLandedShores` | 0.90/0.90 | 0 | **capped** |
| `temperatureScan@EarthFlyingLowShores` | ~2.10/2.10 | ~0 | **capped** |
| `temperatureScan@EarthFlyingHigh` | 2.70/2.70 | 0 | **capped global** — no other-biome FlyingHigh thermo |
| `kerbalism_TELEMETRY@EarthFlyingHighShores` | 1.80/1.80 | 0 | **capped Shores** — Water still unstarted, not this hang |
| `recovery@EarthFlew` | 5.995/6.00 | ~0 | **gone** |
| `geigerCounter@EarthFlyingLow` | 2.484/2.80 | **0.316** | crumbs — not a node |

Need **~4.04** for `survivability` (15). Leftover **0.32** does not
pay it. Bound pair **3.50** if finished over Water — **0.54 short**.
Splash TELEMETRY **0.80** is remaining-subject close, not a second
dashed id. Scan marks `*@Biomes` **capped** when Shores leftover is
0 — **Water ids missing = unstarted**, not spent.

Caps from Kerbalism value × situation (surface 0.3, splash 0.4,
FlyingLow 0.7, FlyingHigh 0.9): geiger 4, thermo 3, TELEMETRY 2,
goo 6.

---

## Instruments on the capable craft (this bind)

Gus `capable: yes` **`kspstuff-hop-valiant-east-one-pbc`**. Stayputnik
**stack-only**; 2HOT + Z-100 + 16-S + Engineer7500 **srf on upper
FL-T100**; 2× FL-T100 + Valiant Boattail. **No fins, no goo, no
geiger part.** Same motor as 13-08-57Z apo **12.3 km**. Tape **1.0**.
Does **not** loft FlyingHigh.

| experiment_id | instrument | tech | unlocked | on_craft |
|---|---|---|---|---|
| `geigerCounter` | `kerbalism-geigercounter` | e101 | **yes** | **no** — not this stack |
| `temperatureScan` | `sensorThermometer` (2HOT) | start | **yes** | **yes** — bound FlyingLow@Water |
| `mysteryGoo` | `GooExperiment` | start | **yes** | **no** — not this stack |
| `kerbalism_TELEMETRY` | Stayputnik PAW | start | **yes** | hosted — bound FlyingLow@Water |

Stayputnik PAW is **not** the Geiger. `seismicScan` landing LOCKED.
LITE InSpace (e101, ~10 s) — orbit / Space ~140 km, not this hop.
MITE `generalRocketry` LOCKED. SITE `advRocketry` LOCKED. Crew
eva/sample: Mk1 locked. Scan `evaReport` REACH is PBC-false.

### Spent — do not re-fly

FlyingHigh **global** thermo **2.70** + FlyingHigh@Shores TELEMETRY
**1.80**. Banked 13-49 / 13-58. Same pad card is not more science.

### This hop — Water FlyingLow shorts

| experiment_id | situation | duration_s | ec_rate | est. |
|---|---|---|---|---|
| `temperatureScan` | FlyingLow@Water | **138** | 0.002 | **2.10** — **bound** |
| `kerbalism_TELEMETRY` | FlyingLow@Water | **30** | 0.052 | **1.40** — **bound** |
| `kerbalism_TELEMETRY` | SrfSplashed@Water | **30** | 0.052 | **0.80** — skip dashed (same id) |
| `kerbalism_TELEMETRY` | FlyingHigh@Water | **30** | 0.052 | **1.80** — skip (no loft) |
| `temperatureScan` | Surface@Water | **138** | 0.002 | **0.90** — skip dashed (same id) |

recover_banks **yes**. Do not transmit. Do not co-run geiger.

### Hang wall — do not bind as hop success

| experiment_id | situation | duration_s | ec_rate | est. |
|---|---|---|---|---|
| `mysteryGoo` | FlyingLow **global** | **641** | 0.18 | **4.20** — would close; will not finish |
| `mysteryGoo` | SrfSplashed **global** | **641** | 0.18 | **2.40** sample |
| `geigerCounter` | FlyingHigh **global** | **497** | 0.005 | **3.60** |
| `geigerCounter` | Surface@Water | **497** | 0.005 | **1.20** |

---

## Out of reach / locked

InSpace LITE/TELEMETRY/geiger/thermo/goo — orbit (Space ~140 km).
LITE **unlocked** e101; envelope is the lock. MITE/SITE tree LOCKED.
`seismicScan` `sensorAccelerometer` **landing** LOCKED. Barometer
`stability` 18 LOCKED. ROCScience **advExploration** LOCKED. Crew
reports: Mk1 locked.

---

## Horizon, not a bind

Ast. XRL-564 — InSpace someday. Do not recover the rock. Chute is
still 15.

One line of future: **~4.04** needs Water-finished FlyingLow thermo
**2.10** in the file plus TELEMETRY; pair **3.50** still **0.54**
short. Not leftover geiger 0.32, not spent Shores FlyingHigh, not
497 s.
