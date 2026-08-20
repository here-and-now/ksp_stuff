# Linus board — science program

Query, then write. Do not copy Squad Start from memory.

```bash
python main.py world
python main.py tech
python main.py parts --unlocked --search geiger
python main.py parts --stack
```

F-013: bind `geigerCounter` only on `kerbalism-geigercounter`, never
Stayputnik PAW. File experiments credit while recording. Do not
transmit. PBC unmanned. Mk1 locked (`simpleCommandModules`, 90).

---

## Banked (do not re-fly)

Live `persistent.sfs`: R&D `sci = 2.3272078` + uncredited 0.056.
Unlocked: **`start`, `engineering101`, `basicRocketry`**. 22-56-44Z
Hammer hop OFFPLAN apo 18.8 km (still FlyingLow). 2HOT started;
Kerbalism credited while recording. **No recover** — recovery leftover
unchanged. KSC empty. Do not recover Ast. XRL-564.

| subject | sci / cap | scv | notes |
|---|---|---|---|
| `mysteryGoo@EarthSrfLanded` | 1.80 / 1.80 | 0 | F-005. |
| `temperatureScan@EarthSrfLandedShores` | 0.90 / 0.90 | 0 | Shores. |
| `kerbalism_TELEMETRY@EarthFlyingLowShores` | 1.40 / 1.40 | 0 | **Capped.** |
| `geigerCounter@EarthSrfLandedShores` | 1.20 / 1.20 | 0 | **Capped.** Do not re-pad. |
| `temperatureScan@EarthFlyingLowShores` | **2.055 / 2.10** | **0.021** | leftover **0.045**. **3 s.** Crumbs. |
| `kerbalism_TELEMETRY@EarthSrfLandedShores` | 0.027 / 0.60 | 0.955 | leftover **0.57**. 29 s. |
| `recovery@EarthFlew` | 5.00 / 6.00 | 0.167 | leftover **1.00**. |

86 s leftover thermo card **spent / stale**. Do not re-bind. Jump
1.13→2.33 is FlyingLow thermo file, not recover.

Earth RSS: landed 0.3, flyingLow 0.7, flyingHigh 0.9. FlyingLow < 50 km.
Geiger cap 4 → FlyingLow **global** 2.80, FlyingHigh **global** 3.60.

Need **12.67** for `survivability` (15). **17.67** for `generalRocketry`
(20).

---

## Tree now

| node | cost | state |
|---|---|---|
| start | 0 | **owned** |
| engineering101 | 5 | **owned** — Geiger Counter |
| basicRocketry | 5 | **owned** — Hammer/Swivel/tanks. No science part. |
| survivability | 15 | locked. chute |
| generalRocketry | 20 | locked. MITE SETUP |
| stability | 18 | locked. barometer |

`kerbalism-geigercounter` **UNLOCKED**. seismic `landing` LOCKED.

---

## Hardware

This Hangar: `kspstuff-geiger-pbc` (Gus signed). Stayputnik +
Engineer7500 + Geiger Counter (do **not** start). Bound leftover landed
TELEMETRY: `docs/missions/jebediah/science.md`. Do not Hangar Hammer
for this pad. Do not Toggle Stayputnik PAW geigerCounter. Do not
Toggle goo/thermo (F-005).

---

## Still available

### 1. Landed TELEMETRY Shores leftover — **bound**

On `kspstuff-geiger-pbc`. Stayputnik PAW. Live
`kerbalism_TELEMETRY@EarthSrfLandedShores` scv 0.955, sci 0.027/0.60.

| field | value |
|---|---|
| experiment_id | `kerbalism_TELEMETRY` |
| part | **`probeCoreSphere_v2`** |
| instrument | hosted PAW, no Science part, unlocked start |
| situation | SrfLanded@Shores |
| duration_s | **29** |
| ec_rate | **0.052** |
| file MB | 0.72 vs tape 1.0 |
| est. sci | **0.57** |
| recover_banks | yes |

Do not bind `geigerCounter`. Do not bind goo/thermo. Cape pad sit.

### 2. Other remaining (not this card)

| experiment_id | situation | instrument | duration_s | ec_rate | est. left | notes |
|---|---|---|---|---|---|---|
| `kerbalism_TELEMETRY` | SrfLanded@Shores | hosted PAW | **29** | 0.052 | **0.57** | **this card** |
| `geigerCounter` | FlyingLow **global** | Geiger Counter, e101, unlocked | **497** | 0.005 | **2.80** | fat file. **497 s hang.** part on stack, not PAW |
| `geigerCounter` | FlyingHigh **global** | same | **497** | 0.005 | **3.60** | 50 km lid |
| `geigerCounter` | Surface other biomes | same | 497 | 0.005 | **1.20**/biome | Shores done |
| `recovery@EarthFlew` | survive+recover | — | — | — | **1.00** | living hop + recover (OFFPLAN did not) |
| `temperatureScan` | FlyingLow@Shores | 2HOT | **3** | 0.002 | **0.045** | **crumbs — skip** |
| `temperatureScan` | FlyingHigh | 2HOT, start, unlocked | 138 | 0.002 | **2.70** | if apo ≥ 50 km. Lars lid 50 km |
| `mysteryGoo` | SrfSplashed | Goo | 641 | 0.18 | **2.40** | hop-to-water refused |

Tape: geiger 0.5 MB + leftover thermo crumbs 0.01 MB << 1.0. EC: geiger
497×0.005=2.5 + cmd ~14 vs 310. Hang is the wall, not tape.

Do not re-pad Cape Surface geiger. Do not hop leftover FlyingLow
TELEMETRY. Do not bind Stayputnik PAW as the Geiger. Do not bind
seismic / barometer / MITE (LOCKED).

### Horizon, not a bind

Ast. XRL-564 — InSpace TELEMETRY / LITE / geiger-with-part someday.
Do not recover the rock. Chute is still 15.

One line of future: landed TELEMETRY 29 s is this pad. FlyingLow
geiger 2.80 still wants the Geiger part and 497 s. Survivability
12.67 away.
