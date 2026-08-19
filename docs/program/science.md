# Linus board — science program

mode: science_sandbox
science: 0.0
funds: none
tree: unknown/start (GameData, not a live RD probe)
body: Kerbin
not: Mun (no stack, no tree, no need)

## Now (0 sci)

Pad hop / sounding. Recover the pod. Do not transmit goo (xmit 0.3).

| experiment | part | where | new? | notes |
|---|---|---|---|---|
| crewReport | mk1pod_v2 | LaunchPad landed | yes | 5 / cap 5 |
| crewReport | mk1pod_v2 | FlyingLow (LaunchPad, else Shores) | yes | biome-specific while FlyingLow |
| evaReport | kerbal | LaunchPad landed | yes | 8; only if feet on pad |
| mysteryGoo | GooExperiment | LaunchPad landed | yes | 10 / cap 13; Start part |
| mysteryGoo | GooExperiment | Kerbin FlyingLow | yes | not biome-split |

Surface samples need experiment level 0.5 — skip. Thermometer is
engineering101 — do not hang it. EVA while flying: no.

That recover should buy **engineering101** (thermometer) and
**basicRocketry** (Hammer / T100). Then a second hop for temp scans.

## Later (not this flight)

- FlyingHigh (~18 km), space low/high crew + goo
- KSC / Runway / Shores landed if they walk or hop sideways
- Mun after the tree and a real transfer stack

Do not brief the crew. Gene copies the mission card into the briefing.
