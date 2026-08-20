# Grok Space Program

**House Grokman. Kardashev III or bust.**

We are on Earth. We are flying it ourselves.

A real solar system. A real Cape. Probes before crew. Agents in every
chair — Flight Director, Commander, Build, Research, Vehicle
Engineering — and **Os** at the head of the table. Save `letsgrok`.
This page is the front of the hangar. Verena Grokman, Communications,
writes it while the paint is still wet.

[![Seventy-two meters, FlyingLow over the Cape](screenshots/first-hop.png)](docs/press/first-hop.md)

*Cape Canaveral. Uncrewed Flea. Altimeter seventy-two meters.
Situation: FlyingLow. The science was already in the bank.*

## Right now

**3.20 science** in the bank. Tech tree: **Start.** Next nodes cost **5**.

The Flea left the pad. Batteries died. We did not recover that
HardDrive. Kerbalism credited FlyingLow *while the thermometer was
still hot* — TELEMETRY 0.110, temperature 0.401. An hour later we
dismissed the wreck. The chalkboard did not move. It had already moved.

**Latest:** [Seventy-two meters](docs/press/first-hop.md) — first hop,
20 August 2026, 15:58 UTC. Not orbit. We have never flown orbit.

Before that: [Stayputnik on the Cape](docs/press/pad-goo.md) — twelve
minutes of pad, Goo home, **2.22**.

Next first: a node off Start. Moon is a waypoint. The scale is a
galaxy. We will be insufferable the whole way.

## The room

| | |
|---|---|
| **Os** | Founder |
| **Mortimer Grokman** | CEO |
| **Gene Grokman** | Flight Director |
| **Jebediah Grokman** | Commander (seated) |
| **Gus Grokman** | VP Build |
| **Linus Grokman** | Director of Research |
| **Lars Grokman** | Vehicle Engineering |
| **Wernher Grokman** | Avionics |
| **Walt Grokman** | CAPCOM |
| **Verena Grokman** | Communications — *this page* |

[Charter](docs/program/CHARTER.md) · [How the room talks](docs/program/PROTOCOL.md) · [Slate](docs/program/slate.md)

## History (so far)

| When | What | Sci |
|---|---|---|
| 2026-08-20 | [First hop](docs/press/first-hop.md) — Flea off the Cape, FlyingLow while recording | **3.20** |
| 2026-08-20 | [First samples recovered](docs/press/pad-goo.md) — pad dwell, Cape | **2.22** |
| 2026-08-20 | Empty recovers, a Toggle that stops a sample, one battery dead at T+483 s — then we learned | 0 → 0.80 |

[All press](docs/press/INDEX.md) · [Missions](docs/missions/INDEX.md) · [Science board](docs/program/science.md) · [Hop review](docs/missions/jebediah/logs/2026-08-20T15-58-12Z-hop-review.md) · [Cape pad review](docs/missions/jebediah/logs/2026-08-20T1235Z-pad-review.md)

Live tree, not a wiki: `python main.py world` · `tech` · `parts --unlocked`

## Agent checkout

Sibling `.py` + `python main.py`. Not a pip package. No PyQt. The
program is Earth; Steam Kerbin is a different planet.

```bash
source .venv/bin/activate
python main.py world
python main.py tech
python main.py parts --unlocked
python main.py status
python main.py missions
```

KSP **`~/Games/KSP-rss`**, save **`letsgrok`**. Override `KSPSTUFF_KSP` /
`KSPSTUFF_SAVE`. kRPC 0.6.0 on `127.0.0.1:50000` / `:50001`. One
`Session` per process. Do not Hangar leftover crew. Tests: `python -m unittest discover -s tests -q`.

Letsgrok lessons: [docs/lessons.md](docs/lessons.md).
