# Building blocks — Gene may only name these

Owned by the **stack engineer** (`ksp-stack`). If Gene needs a name
that is not here, parent spawns `ksp-stack` first. No heredocs.

| Phase | CLI | Plan keys | Expect | Not for |
|---|---|---|---|---|
| recover | `python main.py phase recover` | parking_peri | peri ≥ air+extra | already circular |
| circularize | `phase circularize` | parking_apo | expect_body, peri_min, apo_max | peri in air |
| tli | `phase tli` | mun_pe | next body Mun or high apo | not parked |
| soi | `phase soi` | — | body Mun | already in Mun SOI |
| capture | `phase capture` | mun_pe | bound, peri ≥ 12 km | Kerbin |
| land | `phase land` | suicide_start, suicide_throttle, landing_pe | touchdown or low Mun orbit | Kerbin atmo |

Pad `python main.py mun` still exists as a compose of ascent + these.
Do not Hangar over leftover crew. Use `--from-orbit` / `phase` on the
active vessel.
