# Protocol — who hands to whom

Os is Founder. **Hank Grokman, COO** is the room sequencer (depth 1).
Speech is **name + title**. Ticket bus: `docs/program/OPS.md`.
Machine slugs stay internal.

**Mortimer Grokman, CEO** owns the objective and org RSI. **Hank**
owns who is hired, the pad, leftover/KSC hygiene
(`recover()` + Close; never leftover-ksc load), and **after-flight tape** (`desk`,
`tickets attach-run`, `tickets landing`). **Gene Grokman, Launch /
Flight Director** stamps `go:` on a fly ticket and leftover
**honesty**. Mortimer never flies. Gene never routes tickets. Hank
never stamps `go:`. Commander hop does not recover leftover. CLI
exit **ends** the hop — Commander does not review.

## Handoffs

| From | To | When | Hands | Returns |
|---|---|---|---|---|
| Os | Hank, COO | loop / ops / “keep flying” | — | `python main.py ops next` then those hires |
| Os | Mortimer, CEO | objective / CHARTER / RSI org | slate | `goal:` |
| Os | named desk | talk by name | — | voice only — **no spawn** |
| Hank | desks | `ops next` | ticket ids | ticket patches |
| Gene | fly ticket | `go` stamp | Gene only | `go: yes\|wait` on that ticket |
| Hank | hop pid | `fly: yes` | exact `cli` (parent starts it when `commander: none`) | last-flight; lock on that pid |
| Hank | Commander | `commander: jebediah` (crewed / firsts / `campaign: none`) | fly ticket + exact `cli`; abort officer | `result:` `exit:` `handoff:` |
| Hank | leftover / KSC | lock free, leftover or crash UI | desk then `recover()` + Close (`recover-probe --recover` if recoverable). Never revert. Never leftover-ksc load | pad clean |
| Hank | tape | Commander CLI returned | `desk`, leftover, `attach-run`, `landing` | `ops next` — no Jeb debrief |
| Commander | Hank | hop abort leftover / crash UI | `ksc leftover` — do **not** recover or Close | Hank hygiene |
| Hank | Gus, Vehicle Engineering Lead | open vehicle tickets | ids (batch) | `capable:` on those tickets |
| Hank | Linus, Director of Research | open science tickets | ids (batch) | payload bind (blocked until vehicle `capable`) |
| Hank | Lars, Vehicle Systems Engineer | control tickets / miss | ticket + `live_run` | `lesson:` close |
| Hank | Wernher, Chief Systems Engineer | systems / kRPC world | ticket | systems close |
| Commander | ticket bus | miss **during hop** (still connected) | `tickets open --type control` | Hank after exit |
| Hank | ticket bus | miss after process exit | open control from last-flight abort | Lars if needed — **no Jeb debrief** |
| Commander / hop pid | Hank | campaign clean 0 CLI exit | last-flight only | Hank tape then uncrewed re-run `cli:` — **no Gene, no Jeb** |
| Anyone | ticket bus | friction | `tickets open` | Hank routes |
| Hank | Mortimer | `type=ctt` / `org` / rsi×3 | ticket | RD spend / PROTOCOL mutation |
| Hank | Verena, Communications | `type=press` firsts | ticket | `story:` `shot:` |
| Walt, CAPCOM | Os | phase start / end / unexpected | one line, name+title | — |
| Gene (between exits) or Commander (**during hop**) | KSP window | stuck | `screenshot --name stuck-<stem>` then read PNG | scene — not a postmortem |
| Commander | radio | unusual **during hop** | `note` / hold / abort | in-flight — not a review |
| Hank | `python main.py ship` | lock live, from time to time | envelope (no `status`, no jsonl) | uplink or hire if off-nominal |
| Hank | Gene | off-nominal, plan/`go` must change | `ship.md` + fly ticket | uplink / `go: wait` / tickets — **not stick** |

Linus ↛ Commander. Gus ↛ Hangar. Commander ↛ `.py`/`.craft`. Commander ↛ leftover recover / Close crash UI. Commander ↛ after-flight review / jsonl / attach-run / landing. Gene ↛ stick while lock live. Parent ↛ patch `.py` in the fly turn.
Mortimer ↛ GameData. Mortimer ↛ flight/UT in the save. Mortimer **may**
edit `persistent.sfs` ResearchAndDevelopment (`sci`, `Tech` node) when
Linus/Lars/Gene brief a paid unlock.
Commander ↛ revert / quickload / return to VAB / rewind UT. Crash UI is
honest: **Hank** recovers the ship (`recover()`) and **Close**s to KSC,
then Hangar the next stack on a **clean** pad. Os disabled reverting
flights. Never revert. Never leftover-ksc save/load. Os will not click
it. Screenshot when stuck; do not wait for a founder click.
Clean-pad Hangar of the seated craft for the sortie may stay inside
hop (`install_and_launch`) — that is **launch**, not leftover hygiene.
Splash HD recover of **this** hop after a briefed dwell stays mission.

**Ground talk (between exits, lock free):** Gene, Linus, Gus, Lars,
Wernher, Mortimer, Verena may address each other by name. Still not
the stick. Nominal hop: still not mid-phase hire of Gene. Off-nominal
`ship.md`: Hank may hire. Still different files in one turn. They
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
python main.py tickets open --type ops --tag feedback --title "…" --fingerprint <stem>
python main.py tickets open --type rsi --title "…"
python main.py tickets open --type ctt --title "…"
python main.py tickets open --type press --title "…"
```

`ask` P1 if it blocks `go`. Parent opens that `ops` ticket — it does
**not** file leftover `ask:` onto the world-model table as the bus.
`need_os` is **not a ticket** (CHARTER creed / roster — Os). Leftover
`need_*` in a return is a Hank shim (`tickets from-need`). Desks open
with `--type` as above. Do not emit those leftover keys.
**Fingerprint** is a short stem (`heading-never-090`), never an abort
novel. Third hit opens `type=rsi` (software → Wernher, else Mortimer).
Do not tell another desk in Return prose — open `ops --tag ask`
(`payload.to` / `--desk` = addressee). **Landing envelope wins** over
fly `payload.learn`.

**Tree + hardware (F-013):** experiment_id is not a part. Every bind /
capable / `go:` / Lars science-miss packet must say **tree node** and
whether the **Science-category instrument** is unlocked and on the
craft. Stayputnik PAW is a host, not a Geiger Counter. Desk `f013` is
that line — do not send `tech` / `parts --search` if desk is this sit.
If the instrument is LOCKED: Linus does not bind it as hardware; Gus
`capable: no`; Gene `go: wait`; Lars does not patch a sit for a part we
do not have. Parent copies that line into Lars’s packet so he is not
sequencing a ghost instrument.

**Serial:** `go: yes` (Gene only); Linus **bind** after Gus `capable:`;
one kRPC writer; Lars XOR Wernher on a **miss**. Open `type=systems` →
Wernher (desk/ops/ticket kernel, hangar scene, telem, kRPC trap) without
waiting for a miss. Lars owns vehicle control (`hop_factory.py` factory inland,
`physics_warp.py` coast/pad warp, `pad.py` / `splash.py` /
`blocks.md`; `hop.py` is parked water/splash + helpers).

**Pad occupancy (Os 2026-08-23):** Tape is the product. An **idle pad
is a sin**. A **living recover that cannot pay is also a waste**.
Inventory stays full: Linus many `science_opportunity`; Gus many
signed `.craft` alts (not one hang designed after a wreck). Gene
**picks from that shelf** a bind this hang can bank and stamps `go:`
on a fly ticket. **This-hop bind** is last-envelope biome/sit
(Forest tape is Forest; Grasslands waits Grasslands; SrfLanded vs
splash match the hang; FlyingHigh waits ≥50 km). Do not gather a
subject this stack cannot reach. Warp the coast (physics 2–4×;
uplink `phys-warp` / `no_warp`; never rails / WarpTo). Ground fills
the shelf **during** flight (lock live, other files). Wernher **logs
more kRPC** and explores unused 0.6 surfaces **without waiting for a
miss** (`type=systems` standing). All data is good data if stored.
A 10–15 min Gene conference, an RSI letter, “consider the 154 m/s”,
or conference-then-+0 hops does **not** empty the pad — and does
**not** re-fly the same +0 bind. After sci unchanged: rebind from
the envelope or the next signed hang that can bank. Stop the batch
**only** leftover / crash UI, f013 fail, live control `.py` must be
patched, or Os wait. `go: wait` **only** those.

**Thin tape is first-class:** a 9-column space program is not a log
shrug. Every desk that stumbles on it opens `--type systems` (or
`--type ops --tag feedback`). Cite it on capable / bind / `go:` the
way `f013` is cited. Do **not** idle the pad for it — Wernher patches
during lock live. Query **Tape**, never raw jsonl.

**Science side-by-side:** Linus binds every honest instrument that can
share a hop (thermo + TELEMETRY + goo if not capped / F-013 / tape).
Not one thermo forever.

**Live watch (Os 2026-08-23):** Someone looks at the hop **while it
flies**. The Commander watches telem/gates. Unusual →
`python main.py note <Name> "…"` and/or hold/abort per emergencies
(in-flight radio, not a review after recover). **Hank** (parent)
periodically runs **`python main.py ship`** (disk envelope from
`ship.md`). No `status` Session. Do not `read_file` the growing jsonl. Off-nominal (wreck
flags, lithobrake, empty tanks + still flying, heading never moving,
EC=0 before dwell, crash UI): **do something** — `uplink abort|hold`
if wreck-class; spawn **Gene** if the plan/`go` must change
mid-sortie; spawn **Lars** if hop_factory/physics_warp/control; spawn **Wernher** if
kRPC/telem/desk. Issue-clear → that desk, not a Gene novel.
**Nominal** hop: no Gene, no 15 s narration, no heartbeat swallow.
“Do not spawn Gene during the phase” is **repealed for off-nominal
only**. Depth 1. Gene does **not** take the stick (Commander is the
writer); Gene may uplink / stamp `go: wait` / open tickets. After
CLI exit, tape is still Hank (T-101).

**Uncrewed campaign (I-016, amended):** Gene stamps
`payload.campaign=uncrewed` on the first `go: yes` of a cheap probe
sit. He renders seated `plan.md`. Parent, lock free, leftover clean:
`python main.py desk` then `protocol fly`. `fly: yes` → spawn the
Commander with that `cli:` (`payload.cli`). **Do not hire Gene
between hops** on clean 0 **or** on a miss of a hang that is still
capable. Pad does not idle for Learn or for “consideration.”

After a hop: **Hank leftover first.** Walk home: `recover()` the ship
and **Close** to KSC (`recover-probe --recover` if recoverable). Os
disabled reverting flights. Never revert. Never leftover-ksc save/load
(that looked like a reload / return to pre-launch).
Then: clean 0 → re-fly last `cli:` **only if that bind can still
pay**. Miss (nonzero / ABORT / `science (none)`): spawn **Lars**
on the named control file. **sci unchanged** on a living recover:
Linus rebinds last-envelope biome/sit — not Lars unless the live
`.py` actually broke, not Gene to consider. Pad waits only for
leftover and for a patch of the **live** control `.py` (cannot hop
while Lars writes the named control `.py`). **Do not hire Gene to replan a miss.**
If `go:` is still yes and the hang still capable **and the bind
still pays**: re-fly last `cli:` after leftover. If this hang died
(aero shear, modules gone): next **already-signed** Gus alt — Gene
stamps that fly ticket only if it has no `go:` yet.
No alt on disk → hire Gus while leftover cleans, not a novel.
Stop the string only: dirty hangar (`recover` / `blocked`), f013
fail, Os wait, crewed/firsts Learn, empty shelf (no capable craft
in the batch), `go: wait`. Gene **Learn** is `payload.learn`. `ops next` hires
Gene for Learn only when campaign is **not** `uncrewed` and
`payload.learn` is empty. `python main.py protocol fly` still owns
the gate — missing `go: yes` is wait.

## Parallel (same parent turn, still depth 1)

| Together | Wait for |
|---|---|
| Linus opportunities + Gus `capable` (not bind) | Linus bind to named craft |
| Wernher systems + ground on other files | never the live writer’s `.py` |
| Parent **re-desk** after Gus `capable: yes` (I-014) | Linus bind / Gene `go` on stale capable/f013 |
| Disk `python main.py world` anytime | never a second writer |
| Verena writing `docs/press/` + README from disk | Gene `shot:` before a grab |
| Parent `python main.py screenshot --name <slug>` | Verena `shot: now` (or Gene `shot:` at dwell / after-recover). No kRPC. |
| Gene / Commander `python main.py screenshot --name stuck-<stem>` | logs first; one still; read the PNG. No kRPC. |
| Retro comments on open F- items (gym archive) | Gene chairs ops; Mortimer if org/goal |
| Ground `ops --tag ask` tickets | addressee’s next spawn (lock free) |
| Gene `payload.learn` stamp | never mid-phase |
| Hank `python main.py ship` (lock live) | never `status` Session; never the jsonl |

Not parallel: two Commanders; Lars on a clean 0. Gene **+** flight is
legal **only** off-nominal (Gene no stick). Uncrewed campaign hops
are **serial** re-flies after lock free, not two writers. Nominal
dwell: no children; Walt silent unless unexpected. Off-nominal
dwell: hire. No retro while lock live.

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

Packet is **`docs/program/desk.md`** (parent just wrote it) +
`python main.py tickets packet T-NNN` stdout + BRIEF. No BOARD.md
novel. `read:` is desk plus at most two role paths. Tickets how-to is
always skim: `docs/program/tickets/BRIEF.md`. First command is
`tickets inbox --desk <you>`. PNG / craft / last-flight only on `--deep`.
Jsonl is **disk**: `python main.py telem <jsonl>` or `tickets landing`.
Do not read the tape. **Reasoning floors (Os 2026-08-23):** never
xhigh. Jeb / Lars **low**. Wernher **medium**. Mortimer **medium**.
Gene / Gus / Linus **medium**. Hank is the TUI session — do not bump.
Packet is skim; `--deep` is opt-in. Landing **envelope**
is a skim block on the fly ticket after `tickets attach-run`. Commander
`cli:` is fly `payload.cli`
**copied verbatim** (F-004) from `python main.py protocol fly` — not
Gene `recommended:`, not seated `plan.md`. Lars `read:` third path is
the **named control file** (`hop_factory.py` inland, `physics_warp.py`
warp, `pad.py` pad, `science.py` sit-match) — not `hop.py` for a
factory miss. Lars first command is inbox,
skim, not a named jsonl. Parent copies **f013**
from desk. Do not send parked campaign notes. Children do
not re-run `world`/`tech`/`parts` if desk is this sit.

**Hire freshness (token tax):** a child that `resume_from`s keeps the
whole prior transcript. That is the tax. **Fresh spawn** (no
`resume_from`): every Commander hop, a **new** ticket id, after CLI
exit, a different file, Gene `go:` stamp. **`resume_from`:** only the
**same** ticket on the **same** file while the patch is unfinished.
Never resume the Commander. Never resume after hop exit. A hire that
already ran many turns is **fresh next time**, not another history
dump.

**Envelope (review / ticket landing, not last-flight prose):** Learn /
miss / bind that claims a heading or a biome cites the review envelope
(`heading`, `horiz`, pitch) or `tickets landing T-NNN`. Jsonl stays on
disk. `docs/last-flight.md` is abort/exit only — it can look like
skill while heading never 090. **Hank** `attach-run` + `landing` after
Commander CLI exit. Gene stamps `payload.learn` from that envelope
when `ops next` hires him — **never** from Commander Return prose.
Linus does not bind Water/east if the tape never held heading; does
not bind Grasslands if tape never left Forest; does not bind
SrfLanded if the hang splashed (or splash if it landed). Lars
does not patch a miss from last-flight alone. Commander Return does
**not** cite heading. Flight ends at exit.

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

Gene is the only `go:`. Hire Gene when `ops next` names him
(unstamped `go`, or campaign-stop Learn: campaign not `uncrewed` and
`payload.learn` empty), **or** lock live and `ship.md` is off-nominal
and the plan/`go` must change. Uncrewed hops **between** (lock free)
are not Gene. Crewed / `campaign: none` / firsts: Learn each hop
(`needs_learn`). Do **not** hire Gene as a merge bus after specialists.
Do not hire Gene after every clean 0 on an uncrewed string. **Do not
hire Gene to consider an uncrewed miss after exit.** Open
`type=systems` → Wernher without a Gene in between (standing explore).

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
learn: <one line | none>
f013: <instrument tech unlocked on_craft>
shot: none|dwell|after-recover
slate: docs/program/slate.md
```

Stamp: `tickets stamp T-NNN --field go --value yes|wait --who gene` and
patch `payload.cli` / `payload.campaign` / `payload.phase` /
`payload.learn`. Then render seated `plan.md`. Do not `from-need` from
this body.

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

**Katherine** — `tickets:` `model:` `ask:`. Disk tape only. Ask is a ticket
id, not prose.

**Mortimer** — `goal:` `org:` `tickets:` `unlocked:` `need_os: none|charter|roster` (creed only). Drop `need_builder` / `need_qol` / `need_gene` / `recommended`.

**Hank** — `ops:` `hire:` `packet:` `pad:` `why:` `rsi:`. Leftover/KSC: he **runs** `recover-probe` / `ksc` (lock free). After Commander CLI: `desk`, `attach-run`, `landing`, leftover, then `ops next`. Leftover `need_*` in a child return → `tickets from-need` (shim). Desks must not emit those keys. Do not hire the Commander to explain the hop.

**Pilot** — `result:` `exit:` `handoff:` `abort:` `last:`. Drop `envelope:` / `improve:` / `feedback:` / `need_*`. CLI exit **ends** the hop. Miss `type=control` only **during** the hop if still connected; after exit Hank opens from last-flight. Hop abort `ksc leftover` → Hank, not Commander recover. No attach-run, no landing, no jsonl cite.

## Files

Gene last-writes **briefing prose + seated plan.md render** (`go` /
`cli` / `campaign` / `phase` / `learn` from the fly ticket; `hop_apo` /
`expect_*` / `emergencies` stay on the plan). Flight-layer facts on
`world-model.md` may update between exits — that is not a hire.
Mortimer last-writes **Practice**,
PROTOCOL, and job cards on an org hire. Gus last-writes `vab.md`/`.craft`.
Linus last-writes science **dump**. Bind source is science-ticket
payload. Verena last-writes `README.md` (portrait) and `docs/press/`
(story layer). The Commander takes `uplink.md`. `loop.md` is talk, not
stick. Disagreement → Gene `go: wait`. Missing `go:` = wait.

Milestone stills. Press: Verena picks from `screenshots/runs/` after the hop (beauty beats already hid HUD). Parent `--name` / `--beauty` between exits. **Stuck:** Gene (between exits) or the seated Commander **during the hop** may grab **one** HUD-on still when logs cannot explain the scene. Read the PNG. Not a postmortem after CLI exit. Not a heartbeat. Not press.

Flight cadence (capture only — do not read): `screenshots/runs/<stamp>-<command>/`. Tape: ~10 s ticks (old ticks trimmed to 3) plus sit/stage/wreck — HUD on. Press: named beats (`light`, `airborne`, `science`, `chute`, `splash`, `recover`) hide HUD (F2) and pose the camera, then restore. Verena picks from that folder after the hop. Never grim during a live `phase`. Never clobber press heroes.

```bash
python main.py screenshot --name <slug>         # screenshots/<slug>.png
python main.py screenshot --name stuck-<stem>   # Gene / Commander, stuck only
python main.py screenshot --full                # monitor-size, then restore tile
python main.py screenshot --beauty              # F2 hide HUD for a press still (flight)
```

Refuses `screenshots/first-mystery-goo.png` unless `--force`. `--full` only if the still is unreadable.

## Linus bind

Science-ticket payload (dump may still print the same kv):

```
experiment_id / part / duration_s / ec_rate / recover_banks: yes|no
```

Gus sizes EC from `ec_rate × duration_s` **before** `capable: yes`. If `world` sci does not move after a briefed recover → Linus, then Gene.

## Feedback

Gym `F-NNN` / `I-NNN` twins live on the ticket board. Nested gym MD is
parked — not dispatch. Flight bugs stay in
`docs/lessons.md` as **run — title** headings (the filename stem, not letter-codes).

Leftover `improve:` / `feedback:` → parent `tickets open --type ops --tag feedback`
(or `type=rsi` if repeating house friction). Do not file live `I-NNN.md`.
Leftover `ask:` → `--type ops --tag ask` (not the world-model table).
Mortimer `need_os: none|charter|roster` is creed only.
