# Protocol — who hands to whom

Os is Founder. **Hank Grokman, COO** is the room sequencer (depth 1).
Speech is **name + title**. Ticket bus: `docs/program/OPS.md`.
Machine slugs stay internal.

**Mortimer Grokman, CEO** owns the objective and org RSI. **Hank**
owns who is hired, the pad, and leftover/KSC hygiene
(`recover-probe` / `ksc`). **Gene Grokman, Launch / Flight
Director** stamps `go:` on a fly ticket and leftover **honesty**.
Mortimer never flies. Gene never routes tickets. Hank never stamps
`go:`. Commander hop does not recover leftover.

## Handoffs

| From | To | When | Hands | Returns |
|---|---|---|---|---|
| Os | Hank, COO | loop / ops / “keep flying” | — | `python main.py ops next` then those hires |
| Os | Mortimer, CEO | objective / CHARTER / RSI org | slate | `goal:` |
| Os | named desk | talk by name | — | voice only — **no spawn** |
| Hank | desks | `ops next` | ticket ids | ticket patches |
| Gene | fly ticket | `go` stamp | Gene only | `go: yes\|wait` on that ticket |
| Hank | Commander | `ops next` fly_ready | fly ticket + exact `cli` | `result:` `exit:` `handoff:` |
| Hank | leftover / KSC | lock free, leftover or crash UI | desk then `recover-probe` [`--recover`\|`--space-center`] or `ksc` | pad clean |
| Commander | Hank | hop abort leftover / crash UI | `ksc leftover` — do **not** recover or Close | Hank hygiene |
| Hank | Gus, Vehicle Engineering Lead | open vehicle tickets | ids (batch) | `capable:` on those tickets |
| Hank | Linus, Director of Research | open science tickets | ids (batch) | payload bind (blocked until vehicle `capable`) |
| Hank | Lars, Vehicle Systems Engineer | control tickets / miss | ticket + `live_run` | `lesson:` close |
| Hank | Wernher, Chief Systems Engineer | systems / kRPC world | ticket | systems close |
| Commander | ticket bus | miss (not leftover hygiene) | `tickets open --type control` | Hank `ops next` |
| Commander | ticket bus | campaign clean 0 | same fly ticket stays `go: yes` | Hank re-hires Commander — **no Gene** |
| Anyone | ticket bus | friction | `tickets open` | Hank routes |
| Hank | Mortimer | `type=ctt` / `org` / rsi×3 | ticket | RD spend / PROTOCOL mutation |
| Hank | Verena, Communications | `type=press` firsts | ticket | `story:` `shot:` |
| Walt, CAPCOM | Os | phase start / end / unexpected | one line, name+title | — |
| Gene or seated Commander | KSP window | stuck | `screenshot --name stuck-<stem>` then read PNG | scene |

Linus ↛ Commander. Gus ↛ Hangar. Commander ↛ `.py`/`.craft`. Commander ↛ leftover recover / Close crash UI. Gene ↛ stick while lock live. Parent ↛ patch `.py` in the fly turn.
Mortimer ↛ GameData. Mortimer ↛ flight/UT in the save. Mortimer **may**
edit `persistent.sfs` ResearchAndDevelopment (`sci`, `Tech` node) when
Linus/Lars/Gene brief a paid unlock.
Commander ↛ revert / quickload / return to VAB / rewind UT. Crash UI is
honest: **Hank** `recover-probe` / `ksc` the leftover, then Hangar the
next stack on a **clean** pad. Os will not click it. Screenshot when
stuck; do not wait for a founder click.
Clean-pad Hangar of the seated craft for the sortie may stay inside
hop (`install_and_launch`) — that is **launch**, not leftover hygiene.
Splash HD recover of **this** hop after a briefed dwell stays mission.

**Ground talk (between exits, lock free):** Gene, Linus, Gus, Lars,
Wernher, Mortimer, Verena may address each other by name. Still not
the stick. Still not mid-phase. Still different files in one turn. They
do not spawn each other.

## World model

`docs/program/world-model.md` — Gene chairs **flight** layers: facts
(disk / `desk.md`), meaning (Learn), horizon (Linus), story (Verena).
**Practice** (pitfalls, house changes, QOL) is **Mortimer**. Patterns
that are still true as *ops* stay Practice; flight clocks stay Gene.
Spawn prompts do not inject niche notebooks. Open questions is a
**table** Gene chairs — dispatch does not live there.

Wonder is inner. Moments, not a desk. Rare field exploration
(`tickets open --type ops --tag explore`), some Learns, firsts. Not
every packet. Kardashev creed in the model; joke in the TUI.

## Questions

Ground desks do **not** return `ask:` / `explore:` / `improve:` /
`feedback:` / `recommended:` / `card:` / `need_*` as the bus. Open
tickets (`payload.to` = addressee on `ask`):

```
python main.py tickets open --type ops --tag ask --title "…" --desk <addressee>
python main.py tickets open --type ops --tag explore --priority P3 --title "…"
python main.py tickets open --type ops --tag feedback --title "…"
python main.py tickets open --type rsi --title "…"
python main.py tickets open --type ctt --title "…"
python main.py tickets open --type press --title "…"
```

`ask` P1 if it blocks `go`. Parent opens that `ops` ticket — it does
**not** file leftover `ask:` onto the world-model table as the bus.
`need_os` is **not a ticket** (CHARTER creed / roster — Os). Leftover
`need_*` in a return is a Hank shim (`tickets from-need`). Desks open
with `--type` as above. Do not emit those leftover keys.

**Tree + hardware (F-013):** experiment_id is not a part. Every bind /
capable / `go:` / Lars science-miss packet must say **tree node** and
whether the **Science-category instrument** is unlocked and on the
craft. Stayputnik PAW is a host, not a Geiger Counter. Desk `f013` is
that line — do not send `tech` / `parts --search` if desk is this sit.
If the instrument is LOCKED: Linus does not bind it as hardware; Gus
`capable: no`; Gene `go: wait`; Lars does not patch a sit for a part we
do not have. Parent copies that line into Lars’s packet so he is not
sequencing a ghost instrument.

**Serial:** `go: yes` (Gene only — first of the sit, or after a stop); Linus **bind** after Gus `capable:`; one kRPC writer; Lars XOR Wernher.

**Uncrewed campaign (I-016):** Gene stamps `payload.campaign=uncrewed`
on the fly ticket with the first `go: yes` of a cheap probe sit
(`pad`/`hop`, leftover science). He renders seated `plan.md`. Parent,
lock free, after clean exit **0** + abort none: `python main.py desk`
then `protocol fly`. `fly: yes` and `campaign: uncrewed` on **that
print** → spawn the Commander with that `cli:` (`payload.cli`). **Do
not hire Gene between hops.** Pad does not idle. Stop the string (no
re-fly; Gene **batch Learn**, or Lars on miss): nonzero / ABORT /
`science (none)` / sci unchanged after a briefed recover; `hangar:`
leftover unclear (`recover` / `blocked`); empty card; f013 fail;
`go: wait`; Os wait; new craft or new card; crewed; **remaining
subjects cannot finish on this hang/craft** (do not string lithobrake
Flea hops to a 15-sci node). `campaign: none` is Learn each hop.
`python main.py protocol fly` still owns the gate — missing `go: yes`
on the fly ticket (plan fallback) is wait.

## Parallel (same parent turn, still depth 1)

| Together | Wait for |
|---|---|
| Linus opportunities + Gene world/tech | Gene draft `go: wait` |
| Gus `capable` + Linus tree re-read (not bind) | Linus bind to named craft |
| Parent **re-desk** after Gus `capable: yes` (I-014) | Linus bind / Gene merge on stale capable/f013 |
| Disk `python main.py world` anytime | never a second writer |
| Verena writing `docs/press/` + README from disk | Gene `shot:` before a grab |
| Parent `python main.py screenshot --name <slug>` | Verena `shot: now` (or Gene `shot:` at dwell / after-recover). No kRPC. |
| Gene / Commander `python main.py screenshot --name stuck-<stem>` | logs first; one still; read the PNG. No kRPC. |
| Retro comments on open F- items (gym archive) | Gene chairs ops; Mortimer if org/goal |
| Ground `ops --tag ask` tickets | addressee’s next spawn (lock free) |
| Gene merge of world-model after Learn | never mid-phase |

Not parallel: two Commanders; Gene + flight; Lars on a clean 0. Uncrewed campaign hops are **serial** re-flies after lock free, not two writers. During dwell: no children; Walt silent unless unexpected. No retro while lock live.

## Spawn packet

```
to: <Name, Title>
from: Os | parent
live_run: 2026-08-20T12-35-42Z-pad | none
lock: free | live
task: one sentence
read: <desk.md + ≤2 role paths>
cli: <exact command or none>
return: ## Return (this job)
```

Packet `read:` is **`docs/program/desk.md`** (parent just wrote it) plus
at most two role paths. Tickets how-to is always skim:
`docs/program/tickets/BRIEF.md`. `tickets inbox --desk <you>`.
Jsonl / PNG only on `--deep`. Landing class is a skim line on the fly
ticket after `tickets attach-run`. Commander `cli:` is fly
`payload.cli` **copied verbatim** (F-004) from
`python main.py protocol fly` — not Gene `recommended:`, not seated
`plan.md`. Lars miss packet names the **live** review path **and** the
seated **jsonl** (body-frame tape), not “newest file”. Parent copies
**f013** from desk. Do not send `docs/archive/kerbin-lessons.md`.
Children do not re-run `world`/`tech`/`parts` if desk is this sit.

**Envelope (jsonl, not last-flight prose):** Learn / miss / bind that
claims a heading or a biome cites `kind=state` rows: `heading`,
`horiz`, pitch/`tgt_pitch` from the live jsonl (or review rollup of
that tape). `docs/last-flight.md` is abort/exit only — it can look like
skill while heading never 090. Gene batch Learn names those numbers.
Linus does not bind Water/east if the tape never held heading. Lars
does not patch a miss from last-flight alone. Commander result cites
heading vs briefed 090, not “flew east.”

`hangar:` on desk **is** the Hangar decision (`none` |
`phase <name> sit=<SIT>` | `recover <name> sit=<SIT>` | `blocked`).
Disk cannot see crash UI (`scene: unknown (disk)`). Gene does not vibe
it. Gene `go: wait` if hangar is `recover` / `blocked` — do not `go:
yes` over a dirty hangar. Hank cleans leftover first. Missing `f013`
on bind / capable / `go:` / Lars miss → wait.
Parent flies only if `python main.py protocol fly` prints `fly: yes`.
Uncrewed campaign continue uses that same print — `campaign:` and `go`
come from the fly ticket (plan is fallback). Do not vibe a hop because
the last exit was 0.

Gene merge is the only `go:`. Gene **max two hires per sit** (draft iff
the sit is unnamed, then merge). Uncrewed campaign: that merge is the
**first** `go:` (`campaign: uncrewed`); hops between are not Gene;
**batch Learn** at stop is the second. Crewed / `campaign: none` /
firsts: Learn each hop. Do not hire Gene as a merge bus after every
specialist. Do not hire Gene after every clean 0 on an uncrewed string.

A **run** is one Commander command. Filename Earth UTC with seconds
(`2026-08-20T12-35-42Z-pad`). Review also has Kerbal UT + MET. Verena
dates stories from those lines. Logs: `docs/missions/<id>/logs/`.

## Return (this job)

Open tickets. Do not emit `need_*`, `ask:`, `explore:`, `improve:`,
`feedback:`, Linus `card:`, or Gene `recommended:` (`cli:` is the
fence). Body text may say `tickets open --type ops --tag
ask|explore|feedback` (paid node `--type ctt`; press `--type press`).
Leftover `need_*` is a Hank `from-need` shim only — not in the Gene
body, not a hire token.

**Gene** (stamps + identity; routing is ticket ids):

```
fly: T-NNN
flight: <id>
seat: <kerbal>
phase: <name>
craft: <file or inflight>
tickets: T-NNN [go=yes|wait] | none
go: yes|wait
cli: python main.py <phase> | none
campaign: uncrewed|none
f013: <instrument tech unlocked on_craft>
shot: none|dwell|after-recover
slate: docs/program/slate.md
```

Stamp: `tickets stamp T-NNN --field go --value yes|wait --who gene` and
patch `payload.cli` / `payload.campaign` / `payload.phase`. Then render
seated `plan.md`. Do not `from-need` from this body.

**Linus**

```
science: tickets|none
tickets: T-NNN | none
f013: <instrument tech unlocked on_craft>
```

Bind = patch science payload (`experiment_id` / `part` / `duration_s` /
`ec_rate` / `recover_banks`). Rewrite `docs/program/science.md` as dump
only. Idle on open science tickets, not `need_science`.

**Gus** — `capable:` `craft:` `f013:` `tickets:` `blocker:` (if no).

**Lars** — `tickets:` `stack:` `lesson:` `f013:` `blocks:`.

**Wernher** — `tickets:` `ready_to_fly:` `files:` `blocker:`.

**Verena** — `tickets:` `story:` `shot:` `readme:`.

**Mortimer** — `goal:` `org:` `tickets:` `unlocked:` `need_os: none|charter|roster` (creed only). Drop `need_builder` / `need_qol` / `need_gene` / `recommended`.

**Hank** — `ops:` `hire:` `packet:` `pad:` `why:` `rsi:`. Leftover/KSC: he **runs** `recover-probe` / `ksc` (lock free). Leftover `need_*` in a child return → `tickets from-need` (shim). Desks must not emit those keys.

**Pilot** — `result:` `exit:` `handoff:` `abort:` `last:`. Drop `envelope:` / `improve:` / `feedback:` / `need_*`. Miss → `tickets open --type control`. Hop abort `ksc leftover` → Hank, not Commander recover. `note-tech` is optional tape, not the bus.

## Files

Gene last-writes **briefing prose + seated plan.md render** (`go` /
`cli` / `campaign` / `phase` from the fly ticket; `hop_apo` /
`expect_*` / `emergencies` stay on the plan) and chairs **flight**
layers of `world-model.md`. Mortimer last-writes **Practice**,
PROTOCOL, and job cards on an org hire. Gus last-writes `vab.md`/`.craft`.
Linus last-writes science **dump**. Bind source is science-ticket
payload. Verena last-writes `README.md` (portrait) and `docs/press/`
(story layer). The Commander takes `uplink.md`. `loop.md` is talk, not
stick. Disagreement → Gene `go: wait`. Missing `go:` = wait.

Milestone stills (no kRPC). Press: Verena `shot:` → parent grab. **Stuck:** Gene (between exits) or the seated Commander may grab **one** still when last-flight, the review, and the jsonl cannot explain the scene (empty events, crash UI, leftover vs KSC). Read the PNG. Not a heartbeat. Not press.

Flight cadence (capture only — do not read): `screenshots/runs/<stamp>-<command>/` about every 60 s of a live `pad`/`hop`, plus sit/stage/light/science/recover/wreck. Library for Verena or a stuck debug. Never clobber press heroes.

```bash
python main.py screenshot --name <slug>         # screenshots/<slug>.png
python main.py screenshot --name stuck-<stem>   # Gene / Commander, stuck only
python main.py screenshot --full                # monitor-size, then restore tile
```

Refuses `screenshots/first-mystery-goo.png` unless `--force`. `--full` only if the still is unreadable.

## Linus bind

Science-ticket payload (dump may still print the same kv):

```
experiment_id / part / duration_s / ec_rate / recover_banks: yes|no
```

Gus sizes EC from `ec_rate × duration_s` **before** `capable: yes`. If `world` sci does not move after a briefed recover → Linus, then Gene.

## Feedback

Gym record remains `docs/program/feedback.md` (`F-NNN`) as archive.
`docs/program/improve/` is archive. Flight bugs stay in
`docs/lessons.md` as **run — title** headings (the filename stem, not letter-codes).

Leftover `improve:` / `feedback:` → parent `tickets open --type ops --tag feedback`
(or `type=rsi` if repeating house friction). Do not file live `I-NNN.md`.
Leftover `ask:` → `--type ops --tag ask` (not the world-model table).
Mortimer `need_os: none|charter|roster` is creed only.
