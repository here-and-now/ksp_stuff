# Org flow — letsgrok pad campaign

Os is Founder. This is what the room actually did, what hurt, and
what we change. Interviews: Gene (Flight Director), Jeb (Commander),
Gus/VAB (VP Build), Linus (Director of Research), Lars (Vehicle
Engineering). Skeptic: spawn tax and fake handoffs.

## What worked

Depth-1 switchboard. One kRPC writer. Conference on different files.
Gene `go:` / `wait` / `need_*`. Helm one CLI. Recover without Os clicking.
World desk (`python main.py world`) as environment memory. L-042–L-045
are real Kerbalism learning on **letsgrok**.

## What the loop actually was

```
Os: go for science
  → Gene (Flight Director)
  → Jeb `python main.py pad`
  → Lars after *every* exit (even 0)
  → Gene again
  → sometimes Gus (batteries) or Lars (dwell) then Gene *again*
```

Live pads: 1101Z empty recover → 1119Z double Toggle → 1136Z recover on
Start → 1204Z EC=0 (sci 0.80) → 1235Z 740 s dwell (sci **2.22**).

Unit tests wrote **1049Z, 1114Z, 1132Z, 1159Z, 1200Z, 1221Z** into the
same sortie inbox and `last-flight.md`. Newest filename was not live.

## Data that never made the next desk

| Miss | Who needed it | Cost |
|---|---|---|
| Kerbalism `experiment_id` not in PAW fields | Lars / Jeb | 1101Z empty recover |
| Toggle starts *and* stops | Lars | 1119Z stopped sample |
| Samples take minutes + EC | Linus card, then Lars | 1136Z sci 0 |
| Z-100 vs goo `ec_rate` | Gus on day one | 1204Z abort T+483 |
| `python main.py pad` vs `phase pad` | Jeb | string matching |
| Fake last-flight | Gene, Jeb, Lars | extra Gene hops |

Linus was not spawned when sci stayed 0. Gus was called *after* EC=0.

## Inefficiencies (ranked)

1. **Spawn tax.** Stack-after-every-0 plus Gene-after-every-exit turns a
   9 s pad into two multi-minute hires. Clean 1235Z still hired Lars.
2. **Tests forge the live bus.** `cmd_phase` → `write_handoff` into seated
   sorties.
3. **Bible before the job.** Every child re-reads CHARTER + all lessons
   including Kerbin Mun L-001–L-041.
4. **Titles.** `ksp-flight` as speech. Nameless VAB and stack. Os was
   called visitor.
5. **hop/mun still in `phases.NAMES`** while blocks.md forbids them.

## Changes (this slice)

- Os / Founder. Name + SpaceX-style title in speech. Machine slugs stay.
- **Gus Kerman**, VP Build. **Lars Kerman**, Vehicle Engineering.
- Lars **only on miss** (nonzero exit, ABORT, science none, unexpected).
  Gene still fills Learn after live exits.
- Linus when `world` sci does not move after a briefed recover.
- Unit tests do not write `last-flight.md` or live sorties.
- `lessons.md` is letsgrok only (L-042+). Kerbin Mun chain archived.
- Fake sorties removed from the jebediah inbox.
- Jeb’s card: parent names the **exact** CLI.

Not this slice: deleting `hop.py`/`mun.py`; in-dwell FDO console;
letting Gus edit `craft.py`.
