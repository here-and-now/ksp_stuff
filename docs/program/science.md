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

Gene living hop. Gus `capable: yes`. craft **`kspstuff-hop-flea-pbc`**.
Bound: FlyingLow `geigerCounter` on the Geiger **part**. Keep
`python main.py hop`. Do not re-pad spent Cape cards.

---

## Banked (do not re-fly)

Live `sci = 2.9559` (desk; I-012). Unlocked: **`start`,
`engineering101`, `basicRocketry`**. KSC empty. Do not recover
Ast. XRL-564.

Desk leftovers (cap − sci). Missing id = unstarted:

| subject | left | scan |
|---|---|---|
| Cape Surface geiger Shores | 0 | **capped** |
| Landed TELEMETRY Shores | 0 | **capped** |
| FlyingLow TELEMETRY Shores | 0 | **capped** |
| Landed thermo Shores | 0 | **capped** |
| Landed goo (Earth-global) | 0 | **capped** (F-005) |
| `temperatureScan@EarthFlyingLowShores` | **0.045** | REACH crumbs — skip |
| `recovery@EarthFlew` (save, not Situation) | **1.000** | living recover |

Need **12.04** for `survivability` (15).

---

## REACH (living hop) — bound

Honest hang: Flea ~75 s at 13.5 km. Hammer 18.8 km in **15 s** then
OFFPLAN. Vacuum ballistic at 50 km lid ≈ **202 s**. 497 s vertical is
~300 km = space, not FlyingLow. FAR+RealHeat **unflown** — stock hang
numbers are suspect; lid still 50 km.

Card: `docs/missions/jebediah/science.md` on **`kspstuff-hop-flea-pbc`**.

| experiment_id | situation | instrument | duration_s | ec_rate | est. | honest |
|---|---|---|---|---|---|---|
| `recovery@EarthFlew` | living recover | n/a (HD recover) | — | — | **1.00** | **this sit’s REACH payoff.** Not a Science part. Not a Toggle |
| `geigerCounter` | FlyingLow **global** | `kerbalism-geigercounter` e101 **UNLOCKED** **on_craft yes** | **497** | 0.005 | **2.80** if complete | **BOUND.** Start while aloft. Tape 0.5 / EC 2.5 not the wall. Do **not** expect 497 s. File whatever records. Host is the Geiger part, not Stayputnik PAW |
| `temperatureScan` | FlyingLow@Shores | 2HOT, start, unlocked | **3** | 0.002 | **0.045** | crumbs — skip |
| `mysteryGoo` | FlyingLow **global** | **GooExperiment**, start, unlocked | **641** | 0.18 | **4.20** | hang-limited. Do not bind. Scan maps goo to `Large_Crewed_Lab` LOCKED — wrong host; can is on hop stacks |
| `telemetryReport` | Surface@Shores | stock PAW | instant | — | ~0.60 | skip — Kerbalism TELEMETRY is the id (capped) |
| `evaReport` | Surface@Shores | hosted PAW | — | — | ~3.00 | **crew.** PBC. Mk1 locked |
| `evaScience` | Surface@Shores | hosted PAW | — | — | ~3.00 | **crew.** PBC |
| `surfaceSample` | SrfLanded@Shores | hosted PAW | — | — | ~6.60 | **crew.** PBC |

f013 this sit: instrument **`kerbalism-geigercounter`**, tech
**engineering101**, unlocked **yes**, on_craft **yes** (Gus
`kspstuff-hop-flea-pbc`). Stayputnik PAW is not the Geiger.

---

## Capped (do not re-pad / re-hop)

Surface@Shores geiger. SrfLanded TELEMETRY. FlyingLow TELEMETRY Shores.
Surface thermo Shores. Landed goo.

Other-biome Surface geiger ~1.20: scan REACH pad Shores only — **no
launch site**. Not Cape. Not this hop.

---

## Out of reach

FlyingHigh (50 km lid / OffPlan): geiger ~3.60, thermo ~2.70,
TELEMETRY ~1.80, goo ~5.40.

InSpace LITE/MITE/SITE/TELEMETRY/geiger Space@VirtualBiomes. Splash
TELEMETRY ~0.80 / goo ~2.40 — splash refused (no Water leftover).

---

## Locked (not REACH)

| id | why |
|---|---|
| `seismicScan` | `sensorAccelerometer` **landing** LOCKED |
| `ROCScience` | `RobotArmScanner_S1` **advExploration** LOCKED |
| barometer | `stability` 18 LOCKED |

Scan lists every `mysteryGoo` row as lab LOCKED. Ignore that map for
the containment can. Chute parts exist in catalog; tree is
**survivability 15**.

---

## Horizon, not a bind

Ast. XRL-564 — InSpace someday. Do not recover the rock. Chute is
still 15.

One line of future: recovery leftover **1.00** plus partial FlyingLow
geiger on the **part** is the living hop. 2.80 waits on hang physics,
not a node.
