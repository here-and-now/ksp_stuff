# kspstuff

Agent-driven kRPC checkout for Kerbal Space Program. Sibling `.py` files +
`python main.py`. Not a pip package. No PyQt.

```bash
source .venv/bin/activate
python main.py status
python main.py phase circularize
python main.py missions
```

KSP + kRPC 0.6.0 on `127.0.0.1:50000` / `:50001`. One `Session` per process.
Helm / Flight / VAB / Linus: `AGENTS.md`, `docs/program/CHARTER.md`.
Lessons: `docs/lessons.md`. kRPC traps: `docs/agent-notes.md`.

Do not Hangar over leftover crew. Pad `mun` needs VAB `capable: yes`.
Do not `pip install` this tree. Do not `python -m kspstuff`.

```
main.py       CLI: status / phase / seat / vab / science / mun (pad compose)
phases.py     one segment per process
transfer.py   TLI / SOI / capture
land.py       deorbit / suicide
watch.py      FlightWatch gates
missions.py   dossiers, seat, warp scan of other crew
```

`--profile auto` picks RSS if the save has Earth, else stock Kerbin.
No tests need the game: `python -m unittest discover -s tests -q`.
