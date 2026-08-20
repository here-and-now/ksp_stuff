# Protocol — who hands to whom

Os is Founder. Parent is the room sequencer (depth 1). Speech is
**name + title**. Machine slugs stay internal. Postmortem: `ORG.md`.

## Handoffs

| From | To | When | Hands | Returns |
|---|---|---|---|---|
| Os | Gene, Flight Director | go / fly / science | slate item | `go:` `phase:` `need_*` `recommended:` (exact CLI) |
| Os | named desk | talk by name | — | voice only — **no spawn** |
| Gene | Linus, Director of Research | `need_science` or first conference | ask | card: `experiment_id`, **duration_s**, **ec_rate**, `recover_banks` |
| Gene | Gus, VP Build | `need_builder` or after draft | plan + Linus board | `capable:` `craft:` |
| Gene | Lars, Vehicle Engineering | `need_stack: <name>` | missing block | `stack:` `lesson:` |
| Gene | seated Commander | `go: yes` + `capable: yes` + phase in `blocks.md` | briefing + **exact CLI** | `result:` `exit:` `handoff:` |
| Helm | Gene | every **live** exit | `last-flight.md` + review | Learn |
| Helm | Lars | **miss only** (nonzero, ABORT, `science (none)`, sci unchanged) | handoff + **live** sortie id | `stack:` then Gene |
| Lars | Wernher, Avionics | `stack: ok` **and** kRPC trap | traceback | one `L-NNN` |
| Walt, CAPCOM | Os | phase start / end / unexpected | one line, name+title | — |
| Os | Verena, Communications | PR / README / funding story | slate or live_sortie | `story:` `shot:` `readme:` |
| Gene | Verena | `need_pr: yes` after Learn | live_sortie, why it is a first | same |
| Verena | Gene | next fly needs a window | proposed `shot:` | Gene copies into briefing or `go: wait` |
| Parent | KSP window | Verena `shot: now` (or Gene `shot:` at dwell / after-recover) | `python main.py screenshot --name <slug>` | `screenshots/<slug>.png` |

Linus ↛ helm. Gus ↛ Hangar. Helm ↛ `.py`/`.craft`. Gene ↛ stick while lock live. Parent ↛ patch `.py` in the fly turn.

**Serial:** `go: yes` (Gene only); Linus **bind** after Gus `capable:`; one kRPC writer; Lars XOR Wernher; re-fly only after new `go: yes`.

## Parallel (same parent turn, still depth 1)

| Together | Wait for |
|---|---|
| Linus opportunities + Gene world/tech | Gene draft `go: wait` |
| Gus `capable` + Linus tree re-read (not bind) | Linus bind to named craft |
| Disk `python main.py world` anytime | never a second writer |
| Verena writing `docs/press/` + README from disk | Gene `shot:` before a grab |
| Parent `python main.py screenshot --name <slug>` | Verena `shot: now` (or Gene `shot:` at dwell / after-recover). No kRPC. |

Not parallel: two helms; Gene + helm; Lars on a clean 0. During dwell: no children; Walt silent unless unexpected.

## Spawn packet

```
to: <Name, Title>
from: Os | parent
live_sortie: 1235Z | none
lock: free | live
task: one sentence
read: <≤3 paths>
cli: <exact command or none>
return: the named block
```

Helm `cli:` is Gene `recommended:` copied verbatim. Lars miss packet names the live review path, not “newest file”. Do not require `docs/archive/kerbin-lessons.md`.

## Files

Gene last-writes plan/briefing/Learn. Gus last-writes `vab.md`/`.craft`. Linus last-writes science boards. Verena last-writes `README.md` (portrait) and `docs/press/`. Helm takes `uplink.md`. `loop.md` is talk, not stick. Disagreement → Gene `go: wait`. Missing `go:` = wait.

Milestone stills (no kRPC):

```bash
python main.py screenshot --name <slug>   # screenshots/<slug>.png
python main.py screenshot --full          # monitor-size, then restore tile
```

Refuses `screenshots/first-mystery-goo.png` unless `--force`.

## Linus card

```
experiment_id / part / duration_s / ec_rate / recover_banks: yes|no
```

Gus sizes EC from `ec_rate × duration_s` **before** `capable: yes`. If `world` sci does not move after a briefed recover → Linus, then Gene.
