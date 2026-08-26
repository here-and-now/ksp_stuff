# Missions

Tape id is `current.md` `flight:`. Uncrewed hops write `docs/missions/uncrewed/logs/`.
Commander dossier stays `jebediah` (historical logs: `docs/archive/2026-08-26-jebediah-logs/`). Seat with `python main.py seat <id>`.
Seated `plan.md` is envelope (`hop_apo` / `expect_*` / `emergencies`). `science.md` is a dump, not a board (bind is tickets). Tape is `logs/*.jsonl`.

| Id | Pilot | Status | Next |
|---|---|---|---|
| `uncrewed` ← seated | none | tape id | hop |
| `jebediah` | Jebediah Grokman | Commander dossier | logs |
