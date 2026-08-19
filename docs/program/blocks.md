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
| hop | `python main.py hop` (pad) / `phase hop` | hop_apo (default 15 km) | Kerbin sounding; peri_min ignored; landed or recover | Mun, LKO |

Pad `python main.py hop` Hangars a sounding stack (VAB `capable: yes`),
crew report + goo on the pad, Flea-height ascent (`circularize=False`),
FlyingLow reports, chute, recover if `vessel.recoverable` else freeze.
`phase hop` is that sequence on an **already launched** vessel. No
vessel → not this phase. EVA is Gene briefing only (no hatch API).
Do not transmit goo.

Pad `python main.py mun` still exists as a compose of ascent + these.
Do not Hangar over leftover crew. Use `phase` on the active vessel.

Helm (`phase`) takes `uplink.md`. Gene names only this catalog. Missing
name → `ksp-stack`, not a heredoc.
