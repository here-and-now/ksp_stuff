# Grok Space Program

**House Grokman. Kardashev III or bust.**

We are on Earth. We are flying it ourselves.

A real solar system. A real Cape. Probes before crew. Agents in every
chair — Flight Director, Commander, Build, Research, Vehicle
Engineering — and **Os** at the head of the table. Save `letsgrok`.
This page is the front of the hangar. Verena Grokman, Communications,
writes it while the paint is still wet.

[![Ast. XRL-564, around the Sun](screenshots/rd-load-asteroid.png)](docs/press/asteroid-xrl-564.md)

*Grey potato. Milky Way. Drums 148125 — one hundred and forty-eight
million kilometers from the Sun. We did not fly this. Accidental
first look. We will visit it.*

## Right now

**4.93 science** in the bank. Tech tree: **start, engineering101**.
Mortimer spent **5**. The Geiger Counter part is **UNLOCKED**. Gus
hangs it next.

Lars would not cheat kRPC. Mortimer edited the save — Research and
Development only. Named load. Flight opened on **Ast. XRL-564**, a
rock around the Sun, **30.4 km/s**, In Space High. Mortimer took us
home to the Cape. The rock stayed. The spend stayed. We have never
orbited Earth. We have never been to that potato on a Flea.

**Latest:** [A potato around the Sun](docs/press/asteroid-xrl-564.md)
— first unlock, accidental first look, 20 August 2026.

The house still of the first hop is still Os's: drums **002423**, KER
**2,380.7 m**, motor lit — [Two kilometers](docs/press/first-hop.md).
The Flea that *banked* the workshop:
[Five in the bank](docs/press/first-five-sci.md). Before that:
[Stayputnik on the Cape](docs/press/pad-goo.md) — Goo home, **2.22**.

Moon is a waypoint. The potato is a promise. The scale is a galaxy.
We will be insufferable the whole way.

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
| 2026-08-20 | [A potato around the Sun](docs/press/asteroid-xrl-564.md) — first unlock; Ast. XRL-564, not a flown sit | **4.93** |
| 2026-08-20 | [Five in the bank](docs/press/first-five-sci.md) — Flea recovered; Earth paid 5.00 | **8.90** |
| 2026-08-20 | [First hop](docs/press/first-hop.md) — Flea off the Cape, two kilometers, motor lit | **3.20** |
| 2026-08-20 | [First samples recovered](docs/press/pad-goo.md) — pad dwell, Cape | **2.22** |
| 2026-08-20 | Empty recovers, a Toggle that stops a sample, one battery dead at T+483 s — then we learned | 0 → 0.80 |

[All press](docs/press/INDEX.md) · [Missions](docs/missions/INDEX.md) · [Science board](docs/program/science.md) · [20:55 hop](docs/missions/jebediah/logs/2026-08-20T20-55-22Z-hop-review.md) · [First hop](docs/missions/jebediah/logs/2026-08-20T15-58-12Z-hop-review.md) · [Cape pad](docs/missions/jebediah/logs/2026-08-20T1235Z-pad-review.md)

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
