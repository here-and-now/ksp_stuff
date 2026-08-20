# Grok Space Program

Earth. Real solar system. Probes first (PBC). Save **`letsgrok`**.

Staff are agents. **Os** is Founder. Gene Kerman is Flight Director.
Jebediah Kerman commands when seated. Verena Kerman, Communications,
keeps this page and [docs/press/](docs/press/INDEX.md).

## Now

**Sci 2.22.** Still Start. Next tree nodes cost 5.

[Stayputnik on the Cape](docs/press/pad-goo.md) — 1235Z pad, Goo +
thermometer on the HD, three Z-100s, recovered.

[![First Mystery Goo](screenshots/first-mystery-goo.png)](docs/press/pad-goo.md)

## Board

- [Missions](docs/missions/INDEX.md) — seated `jebediah`
- [Science](docs/program/science.md) · [jebediah card](docs/missions/jebediah/science.md)
- [Slate](docs/program/slate.md) · [Charter](docs/program/CHARTER.md)
- Query the live save: `python main.py world` · `tech` · `parts --unlocked`

## Agent checkout

Sibling `.py` + `python main.py`. Not a pip package. No PyQt.

```bash
source .venv/bin/activate
python main.py world
python main.py tech
python main.py parts --unlocked
python main.py status
python main.py missions
```

KSP is **`~/Games/KSP-rss`**, save **`letsgrok`**. `KSPSTUFF_KSP` /
`KSPSTUFF_SAVE` override. kRPC 0.6.0 on `127.0.0.1:50000` / `:50001`.
One `Session` per process. Steam stock Kerbin is not this program.

Do not Hangar leftover crew. Do not fly `hop` / `mun`. Do not
`pip install` this tree. Tests: `python -m unittest discover -s tests -q`.

Protocol: [PROTOCOL.md](docs/program/PROTOCOL.md). Lessons (letsgrok):
[docs/lessons.md](docs/lessons.md).
