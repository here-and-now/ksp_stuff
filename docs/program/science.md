# Linus board — science dump

Dump of **science tickets**, not dispatch. Bind is ticket payload.
Catalog (`unbound`) is the shelf. This-hop work is **bound**.

Craft `kspstuff-hop-valiant-t7-wheel-pbc`. Tree `start,engineering101,basicRocketry,survivability,stability`. Bank **2.2905**. Next CTT
`generalRocketry` 20 → need ~**17.71**. F-013: instrument part, never
Stayputnik PAW as Geiger.

## Policy — TX vs recover (Cape 64 bps)

House **never transmit / recover HD only** is outdated. Live MM `kind`
(`science-scan`): **sample** = recover the can (no radio). **file** =
credits while recording onto HD; bank via recover HD **or** TX.
Wall-time = `size_MB × 1000 / 0.008` s at live Cape path **64 bps**
(Kerbalism 0.008 kB/s, T-427). Size it. Do not guess goo-sized.

| eid | kind | size_MB | t_s | tx @ 64 bps | this-hop bank |
|---|---|---|---|---|---|
| `kerbalism_TELEMETRY` | file | 0.75 | 30 | **26 h** | recover HD |
| `temperatureScan` | file | 0.45 | 138 | **16 h** | recover HD |
| `barometerScan` | file | 1.17 | 305 | **41 h** | recover HD |
| `geigerCounter` | file | 0.50 | 497 | **17 h** | recover HD (not bound) |
| `mysteryGoo` | sample | 429 | 641 | **621 d** | recover can (not bound) |

**tx:** none of the bound leftover. Hang is minutes; radio is hours.
**recover:** `kerbalism_TELEMETRY` `temperatureScan` `barometerScan`.
Goo is a can — never a 64 bps dump.

Splash-Water bind stays (T-028 / T-422 / T-423). Toggle at splash;
recover HD. Bank stuck **2.29** after recover() is airborne cannot-pay
then recover with **empty HD** — splash leftover never Toggled — not
proof recover() is dead.

Forest High TELEMETRY leftover **1.512** (T-069) shelf until a Forest
loft — same 0.75 MB file, still recover at 64 bps. Not this-hop bind.

TX becomes hop-scale when RateToHome covers size in the hang
(TELEMETRY 0.75 MB in ~5 min needs ~20 kbps — not TL2).

```bash
python main.py science-scan
python main.py comms
python main.py tickets list --type science
```

---

## Bound (this hop)

| ticket | experiment_id | situation | biome | part | duration_s | ec_rate | est | recover_banks |
|---|---|---|---|---|---|---|---|---|
| **T-028** | `kerbalism_TELEMETRY` | SrfSplashed@Water | Water | `probeCoreSphere_v2` | 30 | 0.052 | 0.8 | yes |
| **T-422** | `temperatureScan` | SrfSplashed@Water | Water | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-423** | `barometerScan` | SrfSplashed@Water | Water | `sensorBarometer` | 305 | 0.05 | 0.9 | yes |

## Catalog (unbound shelf — not `ops next` / not hop bind)

| ticket | experiment_id | situation | biome | part | duration_s | ec_rate | est | recover_banks |
|---|---|---|---|---|---|---|---|---|
| **T-025** | `temperatureScan` | FlyingLow@Water | Water | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-026** | `kerbalism_TELEMETRY` | FlyingLow@Water | Water | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-027** | `` | FlyingHigh@Water | Water | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-069** | `kerbalism_TELEMETRY` | FlyingHigh@Forest | Forest | `probeCoreSphere_v2` | 25 | 0.052 | 1.512 | yes |
| **T-070** | `temperatureScan` | FlyingLow@Grasslands | Grasslands | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-071** | `kerbalism_TELEMETRY` | FlyingLow@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-072** | `temperatureScan` | FlyingLow@Tropics | Tropics | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-073** | `temperatureScan` | FlyingLow@Savanna | Savanna | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-074** | `kerbalism_TELEMETRY` | FlyingLow@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-075** | `kerbalism_TELEMETRY` | FlyingLow@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-076** | `` | FlyingHigh@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-078** | `temperatureScan` | SrfLanded@Grasslands | Grasslands | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-079** | `kerbalism_TELEMETRY` | SrfLanded@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-090** | `temperatureScan` | SrfLanded@Tropics | Tropics | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-091** | `temperatureScan` | SrfLanded@Savanna | Savanna | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-092** | `kerbalism_TELEMETRY` | SrfLanded@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-093** | `kerbalism_TELEMETRY` | SrfLanded@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-117** | `temperatureScan` | FlyingLow@Tundra | Tundra | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-118** | `kerbalism_TELEMETRY` | FlyingLow@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-119** | `temperatureScan` | FlyingLow@Mountains | Mountains | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-120** | `kerbalism_TELEMETRY` | FlyingLow@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-121** | `temperatureScan` | FlyingLow@Desert | Desert | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-122** | `kerbalism_TELEMETRY` | FlyingLow@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-123** | `temperatureScan` | FlyingLow@Ice Caps | Ice Caps | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-124** | `kerbalism_TELEMETRY` | FlyingLow@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-125** | `temperatureScan` | FlyingLow@Taiga | Taiga | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-126** | `kerbalism_TELEMETRY` | FlyingLow@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-289** | `temperatureScan` | SrfLanded@Tundra | Tundra | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-290** | `kerbalism_TELEMETRY` | SrfLanded@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-292** | `temperatureScan` | SrfLanded@Mountains | Mountains | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-293** | `kerbalism_TELEMETRY` | SrfLanded@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-295** | `temperatureScan` | SrfLanded@Desert | Desert | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-296** | `kerbalism_TELEMETRY` | SrfLanded@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-298** | `temperatureScan` | SrfLanded@Ice Caps | Ice Caps | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-299** | `kerbalism_TELEMETRY` | SrfLanded@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-301** | `temperatureScan` | SrfLanded@Taiga | Taiga | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-302** | `kerbalism_TELEMETRY` | SrfLanded@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-313** | `temperatureScan` | SrfSplashed@Forest | Forest | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-351** | `temperatureScan` | SrfSplashed@Grasslands | Grasslands | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-352** | `kerbalism_TELEMETRY` | SrfSplashed@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-368** | `mysteryGoo` | FlyingHigh | global | `GooExperiment` | 641 | 0.18 | 5.4 | yes |
| **T-404** | `barometerScan` | FlyingHigh |  | `sensorBarometer` | 305 | 0.05 | 2.7 | yes |
| **T-080** | `geigerCounter` | SrfLanded@Forest | Forest | `kerbalism-geigercounter` | 497 | 0.005 | 1.2 | yes |
| **T-094** | `` | FlyingHigh@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-095** | `` | FlyingHigh@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-291** | `` | FlyingHigh@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-294** | `` | FlyingHigh@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-297** | `` | FlyingHigh@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-300** | `` | FlyingHigh@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-303** | `` | FlyingHigh@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-316** | `geigerCounter` | FlyingLow |  | `kerbalism-geigercounter` | 56 | 0.005 | 0.316 | yes |

Desk leftover vessels n=1. Query desk leftover-science.
`kerbalism_TELEMETRY@EarthFlyingHighForest` sci=0.288/1.800 left=1.512 (T-069 shelf).
