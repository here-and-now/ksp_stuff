# kspstuff

Agent-driven kRPC checkout for Kerbal Space Program. Sibling `.py` files +
`python main.py`. Not a pip package. No PyQt.

```bash
source .venv/bin/activate
python main.py world
python main.py tech
python main.py parts --unlocked
python main.py status
python main.py missions
```

KSP is **`~/Games/KSP-rss`**, save **`letsgrok`**. Override with `KSPSTUFF_KSP`
and `KSPSTUFF_SAVE`. kRPC 0.6.0 on `127.0.0.1:50000` / `:50001`. One `Session`
per process. Steam stock Kerbin is not this program.

Helm / Flight / VAB / Linus: `AGENTS.md`, `docs/program/CHARTER.md`.
Lessons: `docs/lessons.md`. kRPC traps: `docs/agent-notes.md`.

Do not Hangar over leftover crew. Do not fly `hop` / `mun` until VAB
`capable: yes` on a PBC start craft. Do not `pip install` this tree.
Do not `python -m kspstuff`.

```
main.py       CLI: world / tech / parts / status / phase / seat / vab / science
world.py      disk tree + parts + save R&D (no kRPC)
catalog.py    MM ConfigCache / unpatched GameData
phases.py     one segment per process
science.py    stock Experiment.run (Kerbalism live probe later)
watch.py      FlightWatch (to be replaced)
missions.py   dossiers, seat, warp scan of other crew
```

`--profile auto` picks RSS if the save has Earth, else stock Kerbin.
No tests need the game: `python -m unittest discover -s tests -q`.
