# Operations — Hank Grokman, COO

This is the house **operations kernel**. It is not a retrofit of
`I-NNN` / `F-NNN` / leftover `ask:` / `need_*`. Those are archive and
shims. The board is the source of truth. Seated `plan.md` is a
**render** of the fly ticket — not a second live plan, and not a
delete. `python main.py protocol fly` reads `head.json` **with
plan+card fallback**.

**Read first:** `docs/program/org-session-audit.md` (full 447 lines).
That audit is as-is. This file is the construction.

---

## 0. What the audit actually showed (full report)

Depth-1 star: unnamed parent sequences every hire. Gene 83 sessions /
86 log lines in two days (36 `go: yes` / 38 `go: wait`). Jeb 67 CLI
(23×0, 37×2). Lars 37. Linus 33. Gus 24. Mortimer 10. After **18-15**
Gene, Lars, and `lessons.md` **stop**; Jeb `note-tech` runs to 19:51;
**14** reviews stay `_Gene fills this.`; hop-splash keeps Gene’s last
`go: yes` as a campaign. Dual plans: seated `go: yes` hop-splash vs
shim `go: wait` `need_stack: hop-splash`. Board sci **10.96** after
13-58; live desk later **13.26**; `science.md` still prints 10.96.

Spawn tax ~**2 min/hire**. Clean 9 s pad still hired Lars (F-002).
Miss loop Gene→Lars→Gene is ~**6 min of models**. CTT spends 6–7
child layers. hop-to-water **13/13 +0** (heading never 090).
hop-splash **11/11 +0** on that board (`ec=0`, science skip, leftover
ghost). Pad idle while Learn/merge (I-016). `need_mortimer` /
`need_pr` / `need_gene` / `need_qol` **never appear in crew logs**.
Parent log **MISSING**. Walt has no agent card. Bill/Bob never hired.

The bus is **prose the parent LLM interprets**. That is the
communication failure.

---

## 1. Split of power

| Who | Title | Owns | Never |
|---|---|---|---|
| **Os** | Founder | Goal ratification, talk-by-name | Click crash UI, fly |
| **Mortimer Grokman** | CEO / Administrator | Slate *objective*, org RSI, CTT spend, CHARTER/PROTOCOL mutation | Day-to-day dispatch, fly, Hangar, `.py` |
| **Hank Grokman** | COO | Ticket bus, who is hired, pad occupancy, leftover/KSC, **after-flight tape** (`desk` / `attach-run` / `landing`), time, parallel ground vs flight | `go:` (Gene), mission CLI, Hangar, `.craft` (Gus), science bind (Linus), control.*, `.py` on a fly turn, hiring Commander to debrief |
| **Gene Grokman** | Launch / Flight Director | `go:` stamp on a **fly ticket**, briefing, leftover vs Hangar honesty; off-nominal mid-sortie uplink / `go: wait` | PROTOCOL, ticket routing, **stick** (Commander writes) |
| **Gus Grokman** | Vehicle Engineering Lead | `.craft` proposals (many per hire), `capable:` on vehicle tickets | Hangar, fly, `.py` |
| **Linus Grokman** | Director of Research | Science tickets (many open, kept live), bind when vehicle capable | Commander radio, Hangar, `.craft` |
| **Wernher Grokman** | Chief Systems Engineer | Software/world architecture: kRPC, desk, hangar scenes, telem schema, ops kernel, protocol | Vehicle *control* loops, `.craft` |
| **Lars Grokman** | Vehicle Systems Engineer | How the vehicle is *flown*: pad/hop/splash/control, **this-hop** splash HD recover, blocks.md phases | Leftover recover-then-Hangar (Hank/Wernher), world-interface, org, Hangar from Gene |
| **Seated Commander** | Pilot | Exact CLI on a fly ticket until **exit**; one kRPC writer | leftover recover / Close crash UI; `.py`, `.craft`; after-flight review / jsonl / attach-run / landing; miss tickets **after** process exit |
| **Walt** | CAPCOM | Phase edge speech | Hire |
| **Verena** | Communications | Press tickets | Fly |

**Os talks to Hank** (this session, default). Os talks to Mortimer
when the *objective* or the *house constitution* changes.

**The Grok parent process *is* Hank** for operations. Not an unnamed
switchboard. `subagent_type: hank` exists for isolated ops writes;
Os addressing “Hank” is this process. Children still do not spawn.
Depth 1 stays.

---

## 2. Recursive self-improvement (wired, not a speech)

Three RSI clocks, all **tickets**:

1. **Org (Mortimer).** Trip: same ops-class failure 3 times, or Os
   org, or Hank files `type=org` P0. Mutates PROTOCOL / job cards.
2. **Ops (Hank).** Pad-idle vs fly-time is a metric, not a vibe.
   Recurring fingerprint → auto `type=rsi`. (No `ops-log.jsonl` in
   this slice.)
3. **Software (Wernher CSE).** Architecture of how we *see* the world
   (desk, leftover, crash UI, telem frame). Vehicle control patches
   stay Lars. XOR: one of them patches `.py` per miss.

A closed ticket with fingerprint `F` increments `tickets/fingerprints.json`.
At count **3**, kernel opens `type=rsi` P1. `rsi_loop=software` →
desk **wernher**; else Hank. Hank still routes org/ops RSI. That is
the imperative: the loop *must* open the ticket; no LLM “we should
maybe improve.”

---

## 3. Ticket bus (source of truth)

Not markdown `I-NNN` as the live system. Not `need_*` as a chat
token. Not `ask:` as a table Hank never reads on the next hire.

**Store:** `docs/program/tickets/board.jsonl` (append-only events)
+ `docs/program/tickets/head.json` (current snapshot). Human dump:
`python main.py tickets board` → `docs/program/tickets/BOARD.md`.

**CLI (disk, no kRPC):**

```
python main.py tickets open --type science --title "…" --severity S2 --priority P1 --desk linus
python main.py tickets list [--status ready] [--desk gus] [--open]
python main.py tickets show T-014
python main.py tickets assign T-014 --desk gus
python main.py tickets evidence T-014 --path docs/missions/jebediah/logs/….jsonl
python main.py tickets stamp T-014 --field go --value yes   # Gene only, enforced in code
python main.py tickets close T-014 --why …
python main.py ops next     # Hank dispatch: who to hire, which tickets, why
```

### 3.1 Schema

Every ticket:

- `id` — `T-NNN`
- `type` — `fly` | `science` | `vehicle` | `control` | `systems` | `org` | `rsi` | `ctt` | `recover` | `press` | `ops`
- `title` — one line
- `reporter` — name+title
- `desk` — owning queue (`hank` until routed)
- `assignee` — slug or empty
- `severity` — **S1** writer/safety/lock  **S2** blocks a fly  **S3** degrades bank  **S4** hygiene
- `priority` — **P0** now  **P1** this sit  **P2** this slate  **P3** backlog
- `status` — `inbox` `triage` `ready` `assigned` `in_progress` `blocked` `verify` `done` `wont`
- `blockers` — other ticket ids
- `fingerprint` — stable class (`heading-never-090`, `ec=0-after-loft`, `leftover-prelaunch-ghost`, `science-skip-no-modules`, `hangar-can-revert`)
- `category` — `craft` | `science_opportunity` | `bug` | `improvement` | `flight` | `recover` | `org` | `control` | `systems` | `press` | `ops` (replaces cards)
- `tags` — free list (`hard-splash`, `heading-090`, `east-t3`)
- `rsi_loop` — `org` | `ops` | `software` | `vehicle` | `science` | `none`
- `payload` — type-specific (see below)
- `evidence` — paths (jsonl, PNG, lesson heading)
- `sci_expect` — float or null
- `created` / `updated` — ISO
- `sla_s` — optional wall budget for a hire

**Science ticket payload** *is* the experiment card: `experiment_id`,
`part`, `instrument`, `tech`, `unlocked`, `on_craft`, `duration_s`,
`ec_rate`, `situation`, `biome`, `recover_banks`. Linus last-writes
payload. He may open **N science tickets in one hire** when the tree
moves or leftover-science shows unstarted REACH.

**Vehicle ticket payload** *is* the craft proposal: `craft`, `parts`,
`capable`, `why`, `tree`. Gus may open **N vehicle tickets in one
hire** when a node unlocks.

**Fly ticket payload:** `cli`, `phase`, `science_ids[]`, `vehicle` (T-id),
`science` (T-ids), `go` (`yes`|`wait`|empty), `campaign` (`uncrewed`|`none`),
`leftover_policy`. Gene stamps `go` **on this ticket only**. Seated
`plan.md` is a **render** of the fly ticket (Gene may still write
briefing prose; `hop_apo` / `expect_*` stay on the plan).
`python main.py protocol fly` reads `head.json` **with plan+card
fallback**. `ops fly` is occupancy only (do not retarget AGENTS).

**Control ticket:** Lars, named `.py`, lesson heading, miss `live_run`.

**Systems ticket:** Wernher, world-interface (desk leftover, hangar
scene, telem reference frame, kRPC connect).

**Recover ticket:** leftover sit, recoverable, wreck vs living. Desk
**hank**. CLI is Hank `recover-probe` / `ksc`, not Commander hop.

**CTT ticket:** node, cost, parents, sci — Mortimer.

**Press ticket:** Verena, `shot:`.

**RSI ticket:** fingerprint, count, assigned loop.

### 3.2 Who may write which field

Enforced in `tickets.py`, not job-card prose:

- Anyone spawned (and Hank, and Os) may **open**.
- Hank may **route** (`desk`, `priority` within policy) and **assign**.
- Gene may stamp `go` on `type=fly` only.
- Gus may last-write `capable` / `craft` on `type=vehicle`.
- Linus may last-write science payload.
- Lars may close `type=control` with `lesson`.
- Wernher may close `type=systems`.
- Commander may open `type=control` **during the hop** (still connected). After CLI exit, **Hank** opens control from last-flight abort (`tickets open` / `from-need`). Hop abort leftover files to Hank, not a Commander recover CLI. Do not hire the Commander to debrief.
- Hank may close `type=recover` after leftover/KSC CLI.
- Mortimer may close `type=org|ctt`.
- Nobody else stamps `go`.

### 3.3 Severity × priority (Hank’s grid)

Hank does **not** invent a new scale per sit. Dispatch order:

1. S1 (lock, two writers, crash leftover recoverable sitting in Flight)
2. P0 recover / leftover
3. Ready **fly** tickets if lock **free** (pad occupancy)
4. P0/P1 ground on **different files**, batched by desk
5. P2 slate, P3 backlog
6. RSI at count≥3 even if P2 — never blocks S1 or a ready fly

A science ticket with `unlocked=no` cannot become a fly ticket
(F-013 in the kernel). A vehicle ticket `capable: no` cannot bind.

---

## 4. Hank’s operations loop

Hank runs **every parent turn**. Not a spawn after Gene. Not “if Os
said go.” The kernel prints `python main.py ops next`:

```
lock: free|live
pad: idle|flight
fly_ready: T-014 | none
hire:
  - desk: jebediah
    tickets: [T-014]
    cli: python main.py hop-splash
    why: lock free, go yes, leftover recover policy ok
  - desk: gus
    tickets: [T-022, T-023]
    why: tree unlock batch, parallel to flight (lock will be live)
```

### 4.1 Decision procedure (code)

```
if lock live:
    python main.py ship  (disk envelope). never status Session. never the jsonl.
    if off-nominal (wreck flags, lithobrake, empty tanks+flying,
                    heading dead, EC=0 before dwell, crash UI):
        uplink abort|hold if wreck-class
        hire Gene if plan/go must change (no stick)
        hire Lars if hop.py / control
        hire Wernher if kRPC / telem / desk
        issue-clear → that desk, not a Gene novel
    ground_only = tickets ready whose desk ≠ jebediah
    batch by desk (one hire per desk, many tickets)
    never a second Commander
    return

# lock free — leftover hygiene before pad occupancy
if leftover (desk hangar recover/blocked, live probe, crash UI):
    open/boost recover ticket S1 desk=hank
    Hank runs (not Commander):
      recover-probe                    # signal only
      recover-probe --recover          # recoverable leftover — recover()
      ksc                              # scene after Close, not a reload
    # Walk home: recover() the ship and Close to KSC. Os disabled
    # reverting flights. Never revert. Never leftover-ksc save/load
    # (that looked like a reload / return to pre-launch).
    # pad occupancy after leftover is clean
    return

# after Commander CLI return — tape before the next hire
# desk; attach-run fly ticket jsonl; tickets landing; open control
# from last-flight abort if none exists. Do not hire Commander to
# explain. Then leftover (above) or fly_ready (below).

if fly ticket T with go=yes, blockers empty, f013 ok, hangar none, phase in catalog:
    hire Commander with T.cli
    if other desks have ready tickets on other files:
        also hire those (parallel, they must not Hangar)
    return

if fly ticket T with go empty or wait:
    hire Gene ONCE (go stamp, or campaign-stop Learn if
    campaign != uncrewed and payload.learn empty)
    if vehicle tickets unsigned: hire Gus with those ids (batch)
    if science tickets unbound: hire Linus with those ids (batch)
    if control tickets open: hire Lars with those ids (batch)
    if systems tickets / desk=wernher: hire Wernher (batch)
    # not a merge bus after every Gus line
    # bind after capable is still serial honesty: Linus tickets stay
    # blocked on vehicle.capable until Gus returns
    return

if only ground (control miss, systems, org):
    hire the owning desk; batch
    return

idle: Hank files ops ticket "pad idle" if lock free and no fly_ready
      for > N seconds of wall (config). That is I-016 as a metric.
```

### 4.2 When Hank calls whom

| Condition | Hire | Tickets in packet |
|---|---|---|
| Lock live, `ship.md` off-nominal | **Hank** then Gene / Lars / Wernher as the issue | uplink wreck-class; Gene if plan/`go`; Lars hop.py; Wernher kRPC — **no stick**, no `status` |
| Lock live, nominal | ground desks (not Commander, not Gene) | inventory; Hank reads `ship.md` from time to time |
| Lock free, leftover live / crash UI | **Hank** | recover ticket; `recover()` + Close (`recover-probe --recover` if recoverable). Never revert. Never leftover-ksc load |
| Commander CLI just returned | **Hank** (tape, not a Jeb hire) | `desk`, `attach-run`, `landing`; control from last-flight if miss |
| Lock free, fly ready, hangar none | Commander | that fly ticket — CLI only, no review |
| Fly needs `go` | Gene | that fly ticket; batch vehicle/science/control/**systems** |
| Campaign-stop Learn (not uncrewed, empty `payload.learn`) | Gene | that fly ticket |
| Tree unlocked, no crafts | Gus | all open vehicle tickets for that node |
| Unstarted REACH / leftover science | Linus | all open science tickets |
| Miss abort / control fingerprint | Lars | control ticket + live_run |
| Open `type=systems` / unused kRPC / leftover overlay / telem frame | **Wernher** (standing; not miss-only) | systems tickets (also lock-live and `needing_go`) |
| CTT payable | Mortimer | ctt ticket |
| First sci/orbit/unlock | Verena | press ticket |
| Fingerprint count ≥ 3 | kernel opens rsi (`software` → Wernher, else Hank) | rsi ticket |
| Os talks org/objective | Mortimer | org ticket |
| Os talks ops | Hank (this process) | — |

**Gene is not hired** because a specialist returned. Specialists
write the ticket. Hank reads the board. Gene is hired when a fly
ticket lacks `go`, or `needs_learn` (campaign is not `uncrewed` and
`payload.learn` is empty). Uncrewed `go: yes` hires the Commander,
not Gene. **Do not hire Gene to consider an uncrewed miss.**

**Lars is not hired** after clean 0. Campaign re-fly is kernel:
same fly ticket, lock free, last exit 0, abort none, sci moved or
science started. After a miss: leftover first, then Lars on the
**live** control file if it broke; pad waits that file. Hang still
capable + `go: yes` → Commander last `cli:`. Hang died → next
already-signed alt (Gene only if that fly ticket has no `go:`).

### 4.3 Time is valued

- One hire, many tickets of the same desk.
- Tape is the product. An idle pad is a miss. A 10–15 min Gene
  conference after a test hop is the anti-pattern. A Commander
  after-flight review is the same waste — CLI exit ends the hop.
- Pad/flight never waits on Gene Learn (I-016): campaign fly ticket
  stays `go: yes` until stop conditions. Uncrewed miss is leftover +
  live-file patch + re-fly, not Learn.
- Ground work **during** `flight.lock` (Gus/Linus/CSE on other
  files — inventory). Legal because they do not Hangar.
- Spawn tax is paid only when the kernel emits `hire:`.
- SLA on a control ticket: one `.py` + one lesson heading, then
  stop (Lars wall).

### 4.4 Parallelism that is actually parallel

While Jeb flies T-fly:

- Gus may write T-vehicle-next for the *next* tree node.
- Linus may update T-science backlog (not the bound fly card).
- Wernher may patch desk leftover (systems) if it is not the live
  writer’s files.
- Hank does not hire Gene.

Bind of the *current* fly’s science card still waits `capable: yes`
on its vehicle ticket (F-013). That serial is honesty, not ritual.

---

## 5. Data flow

```
desk.md          ← python main.py desk (snapshot, not the board)
tickets/head.json ← source of truth
jsonl envelope   ← evidence on fly/control tickets (heading, horiz, pitch, aoa, biome); Hank attach-run after CLI
last-flight.md   ← abort/handoff only (I-020); Commander Return is this, not a review
lessons.md       ← VSE/CSE dated physics/API
ship.md          ← radio, Walt
```

**One sit object:** the fly ticket + desk snapshot. Seated `plan.md`
is a **render** of the fly ticket (not a second source; do not delete
it). `python main.py protocol fly` reads `head.json` with plan+card
fallback so a missing fly ticket does not brick.

**Commander packet `read:`:** skim from
`python main.py tickets packet T-NNN` (desk + BRIEF + this ticket +
landing envelope — **no BOARD.md**, **no jsonl rows**). `--deep` is
opt-in (PNG, craft, last-flight, `tape: python main.py telem …`).
Hank does **not** auto-`--deep`. Never xhigh. Desk floors (Os
2026-08-23): Jeb/Lars **low**, Wernher **medium**, Mortimer **medium**,
Gene/Gus/Linus **medium**. Hank is the TUI session. Fresh spawn vs
`resume_from`: Commander and new tickets are fresh; resume only an
unfinished patch on the same file.

**Learn:** `payload.learn` on the fly ticket (Gene stamp from
`tickets landing` / tape envelope — never Commander Return
prose). Review auto-fills heading/horiz/pitch; `ksc`/`load`/`recover-probe`
skip the Gene blank. `needs_learn` is campaign not `uncrewed` and learn
empty. Hygiene reviews are not a Gene hire. After-flight attach-run is
**Hank**, not the Commander.

---

## 6. Flight walls

One kRPC writer. Depth 1. Never revert / quickload / rewind UT.
Os disabled reverting flights. Lock live: Hank reads `ship.md`. No
`status`. Off-nominal → hire.
Os does not click crash UI. Commander does not recover leftover or
Close the crash dialog — hop abort `ksc leftover` is a handoff to
Hank. Commander does not review after CLI exit. Hank leftover (lock
**free**) is `recover()` + Close — never leftover-ksc load. Clean-pad
Hangar of the seated craft for the sortie may stay inside hop
(`install_and_launch`) — launch, not leftover hygiene. Splash HD
recover of **this** hop after a briefed dwell stays mission.
Commander does not edit `.py`/`.craft`. Gus does not Hangar. Linus
does not talk to the stick. Missing Gene `go` on a fly ticket =
wait. Gene `go: wait` if hangar is `recover` / `blocked`. Parent/Hank
does not patch `.py` on a fly turn — opens a control or systems
ticket. Leftover recover-then-Hangar in hop.py is Wernher (T-029),
not Lars vehicle control.

---

## 7. Construction order (this implementation)

1. `tickets.py` + `docs/program/tickets/` + `python main.py tickets` + tests.
2. `ops.py` `next` dispatch (lock, leftover, fly_ready, batch).
3. Hank portrait + job card; parent AGENTS table: COO default.
4. Wernher → Chief Systems Engineer card; Lars → Vehicle Systems Engineer card.
5. Gus title Vehicle Engineering Lead; Gene Launch/Flight Director.
6. Mortimer stays CEO; CHARTER/PROTOCOL rewritten around the bus.
7. Seed board from open I-/F- items as *import*, then stop using them live.
8. `protocol fly` prefers the fly ticket; plan+card remain fallback.
9. Fingerprint counter + auto RSI tickets.

Do not Hangar or fly as part of this construction.
