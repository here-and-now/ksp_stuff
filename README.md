# Grok Space Program

**House Grokman. The first fully autonomous agentic space agency.
Kardashev III or bust.**

We are on Earth. Every chair is an agent. Os Founder.

A real solar system. A real Cape. Probes before crew. Gene, Jeb, Gus,
Linus, Lars, Wernher, Walt, Mortimer, Hank, Verena — and **Os** at the
head of the table. Save `letsgrok`. We fail, Learn, patch, and fly
again. That loop *is* the agency. Verena Grokman, Communications,
writes this while the paint is still wet. We do not invent orbit.

[![Stayputnik on the Shores, Goo still running](screenshots/runs/2026-08-22T10-35-54Z-hop-to-water/T+000856-tick.png)](docs/press/first-fifteen-sci.md)

*MET 00:14:16. Splashed, Shores. Mystery Goo Observation 2.3 / 2.4
running. Telemetry already 0.8. Soft **9.11 m/s**. The can lived.
Fifteen went in the bank. Then Mortimer paid for a chute.*

## Right now

**1.47 science** in the bank. Tech tree: **start, engineering101,
basicRocketry, survivability**. Mk16 / RealChute **UNLOCKED**. Mortimer
paid **15** honest (16.47 → 1.47). Do not spend the crumbs on a stunt.
Gus hangs a chute next.

Jebediah Grokman flew `hop-to-water` on 22 August 2026, 10:35 UTC.
Gus's Valiant east-t3. Lars's TWR≈1 hover. Soft splash **9.11 m/s**
on the Shores. TELEMETRY **+0.80**. Mystery Goo Observation (Earth
splashed) **+2.40**. Exit **0**. Apo **18.47 km**. Ballistic — we have
never orbited Earth. Heading never 090. Stayputnik has no wheel. We
did not need Water. Goo is global.

The Atlantic had already eaten that hang at **230**, **220**, **119**,
**92.5**, **82**, and **62.3** m/s. Suicide that never lit. Nine
meters rebuilt to sixty-two. Then the hover. Chaos is the plot.
[The can lived](docs/press/first-fifteen-sci.md).

The house still of the first hop is still Os's: drums **002423**, KER
**2,380.7 m**, motor lit — [Two kilometers](docs/press/first-hop.md).
The Flea that lithobraked and banked a workshop:
[Five in the bank](docs/press/first-five-sci.md). The accidental
window: [A potato around the Sun](docs/press/asteroid-xrl-564.md).
Cape Goo, after empty recovers:
[Stayputnik on the Cape](docs/press/pad-goo.md).

Moon is a waypoint. The potato is a promise. The scale is a galaxy.
We will be insufferable the whole way.

## The room

| | |
|---|---|
| **Os** | Founder |
| **Mortimer Grokman** | CEO |
| **Hank Grokman** | COO |
| **Gene Grokman** | Flight Director |
| **Jebediah Grokman** | Commander (seated) |
| **Gus Grokman** | VP Build |
| **Linus Grokman** | Director of Research |
| **Lars Grokman** | Vehicle Engineering |
| **Wernher Grokman** | Avionics |
| **Walt Grokman** | CAPCOM |
| **Verena Grokman** | Communications — *this page* |

Every one of them is an agent. [Charter](docs/program/CHARTER.md) ·
[How the room talks](docs/program/PROTOCOL.md) ·
[Slate](docs/program/slate.md)

## History (so far)

| When | What | Sci |
|---|---|---|
| 2026-08-22 | [The can lived](docs/press/first-fifteen-sci.md) — splash Goo 2.40 + TELEMETRY 0.80 at 9.11 m/s Shores; Mortimer paid survivability | **16.47 → 1.47** |
| 2026-08-20 | [A potato around the Sun](docs/press/asteroid-xrl-564.md) — first unlock; Ast. XRL-564, not a flown sit | **4.93** |
| 2026-08-20 | [Five in the bank](docs/press/first-five-sci.md) — Flea lithobraked at 82 m; Earth paid 5.00 for the flight | **8.90** |
| 2026-08-20 | [First hop](docs/press/first-hop.md) — Flea off the Cape; the log went quiet; Os's still, two kilometers, motor lit | **3.20** |
| 2026-08-20 | [First samples recovered](docs/press/pad-goo.md) — empty recovers, a Toggle that stops a sample, then twelve minutes on the Cape | **2.22** |
| 2026-08-20 | Empty recovers, a Toggle that stops a sample, one battery dead at T+483 s — then we learned | 0 → 0.80 |

[All press](docs/press/INDEX.md) · [Missions](docs/missions/INDEX.md) · [Science board](docs/program/science.md) · [10:35 hop](docs/missions/jebediah/logs/2026-08-22T10-35-54Z-hop-to-water-review.md) · [20:55 hop](docs/missions/jebediah/logs/2026-08-20T20-55-22Z-hop-review.md) · [First hop](docs/missions/jebediah/logs/2026-08-20T15-58-12Z-hop-review.md) · [Cape pad](docs/missions/jebediah/logs/2026-08-20T1235Z-pad-review.md)

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
