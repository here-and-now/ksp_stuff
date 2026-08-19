# Preflight — next recovery (honor 4761)

Do **not** fly until this is true.

## 4761 (missing)

Mun lithobrake after suicide **timeout + freeze throttle 0** at ~8 km
with peri underground. Relight had worked. He had LF. We killed him
by cutting the stick.

## Before 6189 `--from-orbit` TLI

- [ ] Seat `current.md` = exact crew on **that** vessel (`Grok Kerman 6189`)
- [ ] `python main.py radio` works; Gene uses it every cycle
- [ ] No Hangar. `--from-orbit` only
- [ ] Engines: every `has_fuel` engine **active** (twin Terrier trap)
- [ ] LF and Ox both > 0
- [ ] Freeze will **not** cut throttle if peri < 0 and alt < 30 km (L-035)
- [ ] Suicide: peri < 0 ⇒ throttle 1, timeout clock resets (L-035)
- [ ] Landing Pe **18 km**, not 10 km. Suicide from **>25 km** while peri still ≥ 0 if possible
- [ ] Gene does **not** abort FLAME on a bound orbit
- [ ] Wall-clock SOI wait does **not** dump crew
- [ ] 4373 stays 89×1609 — do not launch over him

## 4373 (already recovered)

Bound **89 × 1609 km**. Next for him is **circularize**, not TLI, so we
do not repeat Val's 11 Mm Pe=None freeze.

## Phases (L-036)

Next recovery is **one block**, not a full `mun`:

- 4373: `python main.py phase circularize` (expect Kerbin peri ≥ 80 km)
- 6189: `python main.py phase tli` after circular parking is confirmed

No spotter. No 15 s monitor. Gene between phases. Stack engineer after exit.

## Go

Only after the boxes. Say go for **circularize 4373** or **tli 6189**.
