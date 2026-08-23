# Linus board — science dump

Dump of **science tickets**, not dispatch. Bind is ticket payload.
Catalog (`unbound`) is the shelf. This-hop work is **bound**.

Craft `kspstuff-hop-valiant-proc-stiff-pbc`. Tree `start,engineering101,basicRocketry,survivability`. Bank **8.7721**. Next CTT
`stability` 18 → need ~**9.23**. Do not transmit. F-013:
instrument part, never Stayputnik PAW as Geiger.

```bash
python main.py science-scan
python main.py tickets list --type science
```

---

## Bound (this hop)

| ticket | experiment_id | situation | biome | part | duration_s | ec_rate | est | recover_banks |
|---|---|---|---|---|---|---|---|---|
| **T-077** | `temperatureScan` | SrfLanded@Forest | Forest | `sensorThermometer` | 83 | 0.002 | 0.54 | yes |
| **T-287** | `kerbalism_TELEMETRY` | SrfLanded@Forest | Forest | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-288** | `kerbalism_TELEMETRY` | SrfSplashed@Forest | Forest | `probeCoreOcto_v2` | 6 | 0.052 | 0.16 | yes |

## Catalog (unbound shelf — not `ops next` / not hop bind)

| ticket | experiment_id | situation | biome | part | duration_s | ec_rate | est | recover_banks |
|---|---|---|---|---|---|---|---|---|
| **T-069** | `` | FlyingHigh@Forest | Forest | `probeCoreOcto_v2` | 25 | 0.052 | 1.512 | yes |
| **T-025** | `` | FlyingLow@Water | Water | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-026** | `` | FlyingLow@Water | Water | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-027** | `` | FlyingHigh@Water | Water | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-028** | `` | SrfSplashed@Water | Water | `probeCoreOcto_v2` | 30 | 0.052 | 0.8 | yes |
| **T-070** | `` | FlyingLow@Grasslands | Grasslands | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-071** | `` | FlyingLow@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-072** | `` | FlyingLow@Tropics | Tropics | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-073** | `` | FlyingLow@Savanna | Savanna | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-074** | `` | FlyingLow@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-075** | `` | FlyingLow@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-076** | `` | FlyingHigh@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-078** | `` | SrfLanded@Grasslands | Grasslands | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-079** | `` | SrfLanded@Grasslands | Grasslands | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-090** | `` | SrfLanded@Tropics | Tropics | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-091** | `` | SrfLanded@Savanna | Savanna | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-092** | `` | SrfLanded@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-093** | `` | SrfLanded@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-117** | `` | FlyingLow@Tundra | Tundra | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-118** | `` | FlyingLow@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-119** | `` | FlyingLow@Mountains | Mountains | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-120** | `` | FlyingLow@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-121** | `` | FlyingLow@Desert | Desert | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-122** | `` | FlyingLow@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-123** | `` | FlyingLow@Ice Caps | Ice Caps | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-124** | `` | FlyingLow@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-125** | `` | FlyingLow@Taiga | Taiga | `sensorThermometer` | 138 | 0.002 | 2.1 | yes |
| **T-126** | `` | FlyingLow@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 1.4 | yes |
| **T-289** | `` | SrfLanded@Tundra | Tundra | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-290** | `` | SrfLanded@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-292** | `` | SrfLanded@Mountains | Mountains | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-293** | `` | SrfLanded@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-295** | `` | SrfLanded@Desert | Desert | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-296** | `` | SrfLanded@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-298** | `` | SrfLanded@Ice Caps | Ice Caps | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-299** | `` | SrfLanded@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-301** | `` | SrfLanded@Taiga | Taiga | `sensorThermometer` | 138 | 0.002 | 0.9 | yes |
| **T-302** | `` | SrfLanded@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 0.6 | yes |
| **T-080** | `` | SrfLanded@Forest | Forest | `kerbalism-geigercounter` | 497 | 0.005 | 1.2 | yes |
| **T-094** | `` | FlyingHigh@Tropics | Tropics | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-095** | `` | FlyingHigh@Savanna | Savanna | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-291** | `` | FlyingHigh@Tundra | Tundra | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-294** | `` | FlyingHigh@Mountains | Mountains | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-297** | `` | FlyingHigh@Desert | Desert | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-300** | `` | FlyingHigh@Ice Caps | Ice Caps | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |
| **T-303** | `` | FlyingHigh@Taiga | Taiga | `probeCoreOcto_v2` | 30 | 0.052 | 1.8 | yes |

Desk leftover vessels n=1. Query desk leftover-science.
