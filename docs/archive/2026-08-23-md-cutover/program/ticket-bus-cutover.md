# Ticket-bus cutover (compile, leftover cards, implementation)

The ticket bus landed **2026-08-21** (`T-001` at `2026-08-21T20:42:25Z`) as a
second sit object. `tickets.py` / `ops.py` / `ops next` were already native.
`protocol fly`, job-card Returns, and parent spawn still compiled markdown
`go:` / `recommended:` / `need_*` / `card:` / `ask:`. This sit cut over **one
compile path + slim Returns**. No new `TYPES`. `protocol fly` prefers the
seated fly ticket and **falls back** to `plan.md` + `science.md` so a missing
board does not brick.

Live board is still **open 7 / 24**. No new ticket opens this sit.

---

## 1. What the ticket era already did

Kernel store is append-only `docs/program/tickets/board.jsonl` plus rebuilt
`head.json` / `BOARD.md` / `fingerprints.json`. Docstring:

```1:1:tickets.py
"""Ticket bus. Source of truth for Hank. Disk, no kRPC."""
```

Eleven types, eleven categories, eight leftover-need keys. Runtime stamp
enforces only Gene `go` and Gus `capable` (`tickets.py` 496–499). `need_retro`
was never a `NEED_MAP` key.

```18:30:tickets.py
TYPES = (
    "fly",
    "science",
    "vehicle",
    "control",
    "systems",
    "org",
    "rsi",
    "ctt",
    "recover",
    "press",
    "ops",
)
```

```107:116:tickets.py
NEED_MAP = {
    "need_stack": ("control", "lars"),
    "need_builder": ("vehicle", "gus"),
    "need_science": ("science", "linus"),
    "need_pr": ("press", "verena"),
    "need_mortimer": ("org", "mortimer"),
    "need_qol": ("systems", "wernher"),
    "need_os": ("org", "mortimer"),
    "need_gene": ("fly", "gene"),
}
```

**Already on the board before this sit**

| Piece | What it did |
|---|---|
| Fly `T-013` | Top-level `go: yes`, payload `cli` / `campaign: uncrewed` / `phase: hop-to-water`, landing after `attach-run`. `payload.go` empty. |
| Science `T-019` / `T-020` | Splash pair (`mysteryGoo` seq 1, `kerbalism_TELEMETRY` seq 0) — the seated card as payload. |
| Vehicle `T-014` | `capable: yes`, done. |
| Control inbox | `T-016` / `T-005` / `T-024` (Lars). `T-008` fly blocked on `T-013`. |
| `from-need` | Adapter leftover-string → `open_ticket`. Live use is `T-012` CLI smoke, not mailbox conversion. |
| Packet | Skim `desk.md` + `BOARD.md` + `BRIEF.md` + one role board; jsonl/PNG `--deep`. |
| `ops next` | Occupancy procedure over `head.json` + desk lock/leftover. `ops.fly_gate` is tickets-only. |
| RSI | Fingerprint count ≥ 3 → `type=rsi`. Live counts max **2**. No `type=rsi` row. |
| Seed | Idempotent titles I-013/I-017/I-018/I-019 → `T-002`…`T-005`. |
| Hop bind | `hop.py` already tickets-first, science.md “legacy” fallback. |

Types **used** on 24 tickets: control 12, science 4, systems 3, fly 2, recover
2, vehicle 1. Unused schema types: `org`, `rsi`, `ctt`, `press`, `ops`.

CLI that existed (and still exists): `open` `list` `show` `assign` `close`
`evidence` `stamp` `packet` `from-need` `tag` `inbox` `landing` `attach-run`
`board` `seed`. **No** `tickets block`. **No** `ops-log.jsonl`. OPS had claimed
both; this sit struck the claims rather than adding the tools.

`hop.py` preferred science-ticket ids. `pad.py` / `splash.py` /
`protocol.fly_gate` did not. Two functions named `fly_gate`, two CLIs
(`protocol fly` vs `ops fly`), two house texts (`CHARTER`/`AGENTS.md` vs
`OPS.md`). That was the dual source of truth.

---

## 2. Leftover card returns (quoted)

Compile (2026-08-21 overlay): desks still **emitted** a job-card kv block the
parent still **consumed**. `protocol.SCHEMAS` only failed **missing** required
keys; extras stayed in `fields`. `## Return (this job)` was **MISSING** from
`PROTOCOL.md` (now at line 180). Return fences lived on `.grok/agents/*.md`.

**Machine parse (required then)** — Gene `recommended` and Linus `card` were
the leftover compile:

```
gene: go, recommended, phase, f013
linus: science, card, f013
```

Linus `card` is dropped this sit. Gene’s schema **name** is still
`recommended`; `cli:` aliases it (section 5).

**Compile-era Gene fence (stripped this sit).** Same Return listed ticket ids
*and* mailbox / routing keys:

```
tickets: T-NNN [go=yes|wait] | none
go: yes|wait
need_pr: none
need_retro: none
need_mortimer: none
campaign: none|uncrewed
envelope: …
recommended: <one line>
ask: / explore: / improve: / feedback:
```

Gene’s **body** already forbade handing `need_*` and then the fence asked for
three of them. Linus body said “do not bind via science.md” and still required
`card: docs/missions/<id>/science.md`. Idle waited on Gene `need_science`.

**Compile-era leftover keys on Return fences** (focus list; not `SCHEMAS`
except Linus `card`):

| Key | Fences (overlay) |
|---|---|
| `need_stack:` as a fence key | **0** (AGENTS spawn + seated plan still had it) |
| `need_builder:` | linus, mortimer |
| `need_science:` | gus |
| `need_pr:` | gene |
| `need_gene:` | gus, linus, lars, mortimer, verena |
| `need_retro:` | gene, gus, linus, lars, verena — **not** in `NEED_MAP` |
| `need_mortimer:` | all eight specialist fences including pilot |
| `need_qol:` / `need_os:` | mortimer |
| `ask:` / `explore:` | gene, gus, linus, lars |
| `improve:` / `feedback:` | those four + mortimer, wernher, verena, pilot |
| `card:` | linus — **also** `SCHEMAS["linus"]` |
| `recommended:` | gene (schema + `fly_gate`), mortimer |
| `campaign:` / `envelope:` | gene; envelope also pilot |
| `tickets:` | gene, gus, linus, mortimer only. Lars / Wernher / Verena / Pilot had none |

Crew logs never wrote `tickets:` as kv. `T-NNN` was inline. `need_pr` /
`need_retro` / `need_gene` / `need_qol` / `need_os` / `need_mortimer` as kv:
**0** under `docs/crew/log/` (OPS already recorded that). Gene/Linus 08-21
lines still said `need_stack hop-splash` / `need_builder`. Newest Gene lines
were already `T-013 go yes` + `campaign:` + CLI.

**Parent still compiled the card gate** (bytes before this sit):

```
go = plan.get("go")
rec = plan.get("recommended")
if go != "yes":
    return FlyGate("wait", "missing go: yes", rec)
```

`cmd_protocol("fly")` fed seated `plan.md` + seated `science.md`. Empty-card
wait was `{pad, hop, splash}` only. Seated phase `hop-to-water` is in
`phases.NAMES` but not that set, so that wait did not fire. `campaign:` was
**not** a `fly_gate` field; AGENTS read it off seated `plan.md` for I-016
continue.

**Live leftover kv still on the render / dump** (not stripped — KEEP-MD
render):

```15:21:docs/missions/jebediah/plan.md
go: yes
campaign: uncrewed
recommended: python main.py hop-to-water
emergencies: hold, cut, no_warp, stage, recover, science, abort_pad
need_builder: none
need_science: none
need_stack: none
```

Shim `docs/program/plan.md` matches. Seated science header is still a card:

```1:8:docs/missions/jebediah/science.md
# jebediah science card

science: card
flight: jebediah
craft: kspstuff-hop-valiant-east-t3-pbc
at: splash
body: Earth
need_builder: no
```

Desk snapshot still prints `card:` from bound eids:

```12:12:docs/program/desk.md
card: kerbalism_TELEMETRY,mysteryGoo
```

Compile-era PROTOCOL Questions / improve / Feedback named `ask:` →
world-model, `improve:` → `I-NNN`, `feedback:` → `F-NNN`, `need_retro:`.
`tests/test_protocol.py` froze `need_retro` + `improve:` + `protocol fly`.
`GLOSSARY.md` defined `need_stack` as an internal flag. Those house texts
were rewritten this sit (section 5); the plan/science/desk bytes above
were not.

---

## 3. Why fallback happened

The 2026-08-21 bus was **overlaid**. Kernel + BRIEF + Hank Return were
ticket-native. The LLM surfaces that emit a hire return, and the parent
compile that hires the Commander, were not rewritten.

1. **Job cards were the old Return plus a `tickets:` line.**
   `prompt_mode: full` children fill the fence. Extra keys never failed
   `parse_return`. PROTOCOL spawn packet said `return: the named block` with
   no `## Return (this job)`.

2. **OPS construction item 8 added a second gate.** `ops.fly_gate` reads
   tickets. It did **not** retarget `protocol.fly_gate`. CHARTER / PROTOCOL /
   AGENTS parent-fly sentences named `protocol fly`. Gene kept writing
   `recommended:` on seated `plan.md` because that line **was** Commander
   `cli:`.

3. **`from-need` made deleting the tokens unnecessary.** Eight `NEED_MAP`
   keys, unknown `need_retro` raises, `need_qol` mapped to Wernher while
   AGENTS/CHARTER sent it to Lars. Hank taught: if a desk still returns
   `need_stack` / `need_builder` / `need_science`, run `from-need`. Native
   BRIEF path is `tickets open`.

4. **Last-write tables and tests froze the overlay.** Gene last-writes
   plan/briefing. Linus last-writes both science.md files. Pad/splash/desk
   f013 parsed the markdown card. `tests/test_protocol.py` asserted
   `need_retro` and Mortimer `need_qol`. `tests/test_protocol_gate.py` fed a
   plan dict, not `head.json`.

5. **This sit keeps fallback on purpose.** DESIGN: prefer the fly ticket;
   missing `head.json` / no seated fly → same as today from `plan` +
   `science_text`. Do not brick. Do not merge `protocol fly` / `ops fly`.
   Do not expand empty-card wait to `hop-to-water`.

---

## 4. MOVE vs KEEP

No new types. Reuse the eleven that already exist. `from-need` stays the
leftover on-ramp. Desks open with `tickets open --type …`.

### MOVE (leftover key → existing field)

| Leftover key | Lands on |
|---|---|
| `recommended:` | fly `payload.cli` (`T-013` already). Fence says `cli:` |
| `campaign:` | fly `payload.campaign` (`uncrewed`/`none`) |
| `go:` | Gene stamp on the **fly ticket** (`t.go`; `payload.go` optional). One source |
| `need_stack` | `type=control` desk lars |
| `need_builder` | `type=vehicle` + Gus `capable` |
| `need_science` / Linus `card:` | `type=science` `payload.experiment_id` + `situation` |
| `need_pr` / `pr:` | `type=press` desk verena |
| `need_gene` | unstamped `type=fly` — `ops next` already hires Gene |
| `need_mortimer` paid node | `type=ctt` (new opens; `NEED_MAP` shim may still dump to `org`) |
| `need_mortimer` org | `type=org` |
| `need_qol` | `type=systems` desk wernher (`NEED_MAP`; AGENTS→Lars was the bug) |
| `ask:` | `type=ops` `--tag ask` `payload.to` (desk = addressee). P1 if it blocks `go` |
| `improve:` / live `I-NNN` | `type=ops` `--tag feedback` **or** `type=rsi` if repeating house friction. Stop filing `I-NNN.md` |
| `feedback:` | same `ops` `--tag feedback`. Gym `F-NNN` stays archive |
| `explore:` | `type=ops` `--tag explore` P3 |
| `envelope:` kv | fly/control `payload.landing` after `attach-run`. Jsonl stays evidence |
| `note-tech` as bus | `tickets open --type control\|recover`. File may still append |
| dual `plan.md` kv | **render** of the fly ticket (`go`/`cli`/`campaign`/`phase`) |
| `science.md` bind | board dump. Bind source is science-ticket payload |

### KEEP-MD (not a ticket)

- CHARTER creed, Kardashev, Os-is-founder, roster speech
- `docs/crew/<slug>.md` portraits / voice; `docs/crew/log/` one-liners
- `docs/lessons.md` dated run headings (Lars XOR Wernher)
- `docs/program/desk.md` sit snapshot (lock, leftover occupancy, f013, sci, stack)
- `docs/program/slate.md` goal
- jsonl tape + `last-flight.md`. PROTOCOL Envelope **rule** stays prose
- seated `briefing.md` prose; seated `plan.md` as **render** (`hop_apo` /
  `expect_*` / `emergencies` — not ticket fields)
- `docs/program/science.md` opportunities dump (not parser input)
- `world-model.md` Facts/Meaning/Practice + Open questions **table** (Gene
  chair). Dispatch does not live there
- gym `feedback.md` / `F-NNN` as record; `improve/` as archive
- packet shape: `desk.md` + `BRIEF.md` (+ kernel may add `BOARD.md`)
- Verena `shot:` / `story:` (press stamp, not a new type)
- `need_os` — CHARTER/roster, Os. Mortimer fence only
- `need_retro` — gym trip flag. Do not invent `type=retro`
- `agents_md: false`, isolation `none`, Hank `ops next` occupancy

Do **not** ticket portraits, CHARTER, lessons, or `desk.md`. Skeptics:
`real=false` on type zoo / house tickets / deleted-card brick.

---

## 5. What we changed (files)

One PR-shaped slice. Kernel helpers + `fly_gate` prefer-ticket, parse alias,
slim fences, PROTOCOL `## Return (this job)`, AGENTS spawn table, tests.

### `tickets.py`

- `fly_fields(t)` → `{go, cli, campaign, phase, science_ids}`. `go` is `t.go`
  or `payload.go`. `cli` is `payload.cli` or `payload.recommended`. Empty
  `payload.go` with `t.go=yes` is yes (`T-013` pattern).
- `seated_fly_ticket()` → open `type=fly` not `done`/`wont`/`blocked`; prefer
  `verify`/`in_progress`/`assigned`/`ready` with `go=yes`. Missing `head.json`
  → `None` (do not throw).
- `patch_fly_payload` merges `cli`/`campaign`/`phase`/`science_ids`; **keeps**
  top-level `go`.
- `attach_run` merges into payload; **does not** blank top-level `go`.
- `science_ids_for` unchanged (empty → caller falls back).
- No `tickets block`. No `ops-log.jsonl`. No type additions. `NEED_MAP` +
  `from-need` stay.

```551:566:tickets.py
def fly_fields(t: dict[str, Any] | None) -> dict[str, Any]:
    """go / cli / campaign / phase / science_ids. go is t.go or payload.go."""
    empty: dict[str, Any] = {
        "go": "",
        "cli": "",
        "campaign": "",
        "phase": "",
        "science_ids": (),
    }
    if not t:
        return empty
    pl = t.get("payload") or {}
    if not isinstance(pl, dict):
        pl = {}
    go = str(t.get("go") or pl.get("go") or "").strip()
    cli = str(pl.get("cli") or pl.get("recommended") or t.get("cli") or "").strip()
```

### `protocol.py`

- `FlyGate` gained `campaign: str = "none"`.
- `fly_gate(..., ticket=None)`: seated fly ticket (or passed-in), then plan.
  Same wait order: missing go, lock live, leftover occupancy, phase not in
  `NAMES`, capable on `_HANGAR_PHASES`, leftover `phase …` CLI, f013.
- Bound ids: payload `science_ids` → `science_ids_for` → `_card_ids`.
  Empty-card wait **stays** `{pad, hop, splash}`.
- `format_gate` prints `campaign:` so I-016 continue reads the **print**, not
  seated `plan.md`.
- `parse_return`: Gene `cli:` copies to `recommended` when that key is empty.
  Do not require `need_*` or `tickets:`.
- Linus schema `("science", "f013")` — no `card`.

```12:21:protocol.py
SCHEMAS: dict[str, tuple[str, ...]] = {
    "gene": ("go", "recommended", "phase", "f013"),
    "gus": ("capable", "craft", "f013"),
    "linus": ("science", "f013"),
    "lars": ("stack", "lesson", "f013"),
    "mortimer": ("org", "goal"),
    "wernher": ("ready_to_fly", "files"),
    "verena": ("story", "shot"),
    "pilot": ("result", "exit", "handoff"),
}
```

```134:137:protocol.py
    go = (ff.get("go") or plan.get("go") or "").lower()
    phase = (ff.get("phase") or plan.get("phase") or "").lower()
    rec = (ff.get("cli") or plan.get("recommended") or plan.get("cli") or "").strip()
    campaign = (ff.get("campaign") or plan.get("campaign") or "none").strip() or "none"
```

```187:193:protocol.py
def format_gate(gate: FlyGate) -> str:
    return (
        f"fly: {gate.fly}\n"
        f"reason: {gate.reason}\n"
        f"cli: {gate.cli or 'none'}\n"
        f"campaign: {gate.campaign or 'none'}\n"
    )
```

`cmd_protocol("fly")` still `build_sit()` + seated science text as **fallback
food**; passes `ticket=seated_fly_ticket()`.

### `ops.py`

`fly_gate` / `next_actions` use `fly_fields` for `go`/`cli`. `ops fly` may
print `campaign:`. **Does not** fold lock / leftover occupancy / f013 into
occupancy. **Does not** retarget AGENTS to `ops fly`. Two `fly_gate`s stay
(occupancy vs physics).

### Bind path

- `pad.pad_science_ids` / `splash.splash_science_ids`: tickets-first +
  science.md fallback (copy hop).
- `hop.hop_wants_flying_high`: open science tickets with `FlyingHigh` **or**
  seated card.
- `desk.build_sit`: `eids = science_ids_for(craft=…) or card_experiments(science.md)`.
  Snapshot **format** of `desk.md` unchanged (`card:` line stays).

### Docs + job cards

| File | Change |
|---|---|
| `docs/program/PROTOCOL.md` | Added `## Return (this job)`. Questions / improve / feedback → `tickets open --type ops --tag …`. I-016 continue from `protocol fly` print. Commander `cli:` = `payload.cli` (F-004). Gym named archive. Dropped `need_retro` as a return key. |
| `AGENTS.md` | Hire from `ops next` ids. Commander iff `protocol fly` → `fly: yes` (ticket + desk waits; plan fallback). Continue: `campaign: uncrewed` **on that print**. Specialists from **open types**. Leftover `need_*` = shim only. `need_qol` → Wernher/`systems`. Paid `need_mortimer` → `ctt`. Do not file `I-NNN` / world-model from `ask:`/`improve:`. |
| `docs/program/CHARTER.md` | CLI gloss: `protocol fly` = fly ticket + desk, plan fallback. How-it-runs `ask`/`need_qol` retargeted. **Creed not rewritten.** |
| `docs/program/OPS.md` | Sit object = fly ticket + desk. `protocol fly` reads `head.json` **with plan+card fallback**. Dual plan is a render, not a delete. Struck `tickets block` / `ops-log.jsonl`. Construction item 8 rewritten. |
| `docs/program/GLOSSARY.md` | `campaign:` = fly payload; `need_stack` = shim; `improve:`/`ask:`/`explore:` = ops tags; `note-tech.md` = tape not bus. |
| `docs/program/tickets/BRIEF.md` | `ops --tag ask\|feedback\|explore`; `cli` not `recommended`; leftover `need_*` never in a Return fence. |
| `docs/program/tickets/README.md` | Sit object + fallback sentence; do not emit leftover return keys. |
| `.grok/agents/{gene,linus,gus,lars,wernher,verena,mortimer,pilot}.md` | Slim fences. Bodies: open tickets, do not emit leftover keys. Hank shim sentence stays. |

**Canonical Gene fence** (PROTOCOL; gene job card matches `fly`/`go`/`cli`/
`campaign`/`tickets`):

```192:204:docs/program/PROTOCOL.md
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

**Others (fences now):** Gus `capable`/`craft`/`f013`/`tickets`. Linus
`science: tickets`/`f013`/`tickets` (bind on payload). Lars
`tickets`/`stack`/`lesson`/`f013`/`blocks`. Wernher
`tickets`/`ready_to_fly`/`files`. Verena `tickets`/`story`/`shot`/`readme`.
Mortimer `goal`/`org`/`tickets`/`unlocked`/`need_os` (creed only). Pilot
`result`/`exit`/`handoff`/`abort`/`last` — no `envelope:`/`improve:`/`feedback:`.
Hank unchanged (`ops`/`hire`/`packet`/`pad`/`why`/`rsi`) plus from-need shim.

No Return block in those job cards lists `need_builder`, `need_retro`,
`card:`, `ask:`, or `recommended:` as a fence key. Mortimer `need_os:` is
DESIGN-kept.

### Do not touch (this slice)

`TYPES` / `CATEGORIES` / `NEED_MAP` / `seed_legacy` / live board rows /
I-012…I-020 and F-001…F-015 **contents** / RSI auto-open / `ops.next_actions`
order / merging the two fly CLIs / CHARTER creed / portraits / `lessons.md`
forensics / `slate.md` / jsonl files / briefing prose / `phases.py` `hop_apo`
on the plan render / `agents_md: false` / expanding empty-card wait /
requiring `tickets:` in `parse_return` / ticketing leftover gym opens.

---

## 6. Tests

Verified method counts (not a re-run here). The TESTS suite is **86** methods:

| File | `def test_` |
|---|---|
| `tests/test_tickets.py` | 25 |
| `tests/test_protocol.py` | 9 |
| `tests/test_protocol_gate.py` | 17 |
| `tests/test_desk.py` | 12 |
| `tests/test_world.py` | 23 |
| **sum** | **86** |

KERNEL counted **78** on `test_tickets` + `test_protocol` + `test_protocol_gate`
+ `test_desk` plus pad/splash/hop card-id cases, without `test_world`. TESTS
re-ran with `test_world` and reported **86 passed, 0.131 s**. Nothing to patch.
Did not fly KSP.

```
source .venv/bin/activate
python -m unittest tests.test_tickets tests.test_protocol \
  tests.test_protocol_gate tests.test_desk tests.test_world -q
```

**`test_protocol_gate.py`** — keep every current wait (missing go, capable,
leftover occupancy, empty card, f013, yes, phase leftover CLI), plus:

- `test_ticket_wins_over_plan` — ticket `{go:yes, payload:{cli, campaign, phase}}`
  + plan `go:wait` / other `recommended` → `fly: yes`, `cli` from payload,
  `campaign: uncrewed` on the print.
- `test_no_ticket_falls_back_to_plan` — `ticket=None` → same as today from plan
  + `science_text`.
- `test_ticket_science_ids_skip_card` — payload `science_ids` skips empty card.
- `test_gene_cli_aliases_recommended` — Gene `cli:` without `recommended:` is
  not missing.
- `test_gene_without_need_keys_ok`.
- `test_linus_without_card_ok`; missing `science` or `f013` still missing.

**`test_protocol.py`** — asserts `## Return (this job)`; keeps `protocol fly`,
`desk.md`, `duration_s` / `ec_rate` / `recover_banks`, `Practice`, gym
`feedback.md` / `F-NNN`. Dropped needle `need_retro`. Mortimer fence has
`tickets:` and **not** `need_builder`.

**`test_tickets.py`** — occupancy / `from-need` / `science_ids_for` / packet
skim kept. Added `fly_fields` either-or `go`, `seated_fly_ticket` missing-head
and prefer-`go=yes`, `patch_fly_payload` keeps top-level `go`,
`attach_run_preserves_top_level_go`.

**Pad / splash** — `test_science_tickets_skip_markdown`: non-empty
`science_ids_for` skips the fixture card; empty still uses markdown / aborts
empty.

Do not require `protocol.fly_gate` to ignore plan when the ticket is absent.

---

## 7. What is still markdown and why

The bus stores the sit. Markdown keeps creed, voice, physics envelope, and
snapshots the kernel does not replace.

| Still markdown | Why |
|---|---|
| CHARTER | Creed / founder / roster. CLI gloss only. |
| Portraits + logs | Voice. Not dispatch. |
| `lessons.md` | Dated run headings. Lars XOR Wernher. Last 3 on a miss packet. |
| `desk.md` | Parent snapshot once per conference (lock, leftover occupancy, f013, sci, stack). |
| seated `plan.md` + shim | **Render.** `hop_apo` / `expect_*` / `emergencies` live here (`phases._kv`). Gene still last-writes it so fallback and loft lid keep working. |
| seated `briefing.md` | Gene prose between exits. |
| `docs/program/science.md` | Opportunities dump. Packet skim still attaches it. Bind is ticket payload. |
| seated `science.md` | Dump / fallback food for `card.py`. Pad/splash/hop still parse it when tickets are empty. |
| `world-model.md` | Gene chairs flight meaning. Open questions table stays; parent stops filing `ask:` there as the bus. |
| gym `F-NNN` + `improve/` | Archive-of-record. Live friction is `ops`/`rsi`. |
| jsonl + `last-flight.md` | Evidence / abort. Envelope **rule** in PROTOCOL is prose. |
| `note-tech.md` | Optional Commander tape, not the bus. |
| `slate.md` | Mortimer goal. |
| `vab.md` / `.craft` | Gus last-write. |
| PROTOCOL / job cards | House how-to. Children still eat `.grok/agents/*.md` (`agents_md: false`). |
| `card.py` | Fallback parser. Empty is not a sit (`NO_BOUND_CARD`). Test fixtures `PAD`/`HOP`/`SPLASH_EXPERIMENTS` are not fly defaults (F-005). |

`protocol fly` **still** feeds seated science text. `_bound_ids` is payload →
tickets → card. Missing board → plan+card. That is the anti-brick.

Gene still **renders** seated `plan.md` from the fly ticket. Linus still
rewrites `docs/program/science.md` (and may rewrite seated `science.md`) as
dump only. Idle is open science tickets, not `need_science`.

---

## 8. Open risks

**Dual compile, by design.** `ops.fly_gate` is occupancy (`fly_ready` +
`payload.cli`). `protocol.fly_gate` is the parent Commander gate (ticket then
plan, plus lock / leftover occupancy / capable / f013 / empty-card). AGENTS
still names `protocol fly`. A lying seated `plan.md` can still fly if
`seated_fly_ticket()` is `None`. Clearing seated `go:` no longer waits when
`T-013` is stamped; clearing the stamp waits even if the plan says `yes`.

**Fly payload is incomplete vs OPS claims.** `T-013` has top-level `go: yes`
and `payload.go: ""` (`head.json` 362–368). `fly_fields` treats that as yes.
No `science_ids[]`, no `science: [T-019, T-020]` on the fly ticket. Bind for
this sit is open science tickets (`T-019`/`T-020`) plus desk eids. TELEMETRY
desk `f013` is `unlocked=n/a`; the science ticket says `unlocked: yes`.

**Renders still carry leftover kv.** Seated/shim `plan.md` still have
`recommended:` and `need_*: none`. Seated `science.md` still has `science:
card` and `need_builder: no`. Desk still prints `card:`. Children are told not
to *return* those keys; the files were not scrubbed (KEEP-MD render / dump).

**Shim residue.** `NEED_MAP["need_mortimer"]` still opens `type=org`, not
`ctt`. AGENTS maps leftover *paid* `need_mortimer` to `ctt` in prose only.
`from-need` remains; DESIGN dropped it from the Gene **body**, but Gene /
Linus / Gus / Lars / Wernher / Verena still have “if you still think `need_*`,
`from-need` — never in the fence.” Hank owns the shim. `SCHEMAS["gene"]` still
requires the field name `recommended` (alias from `cli:`). `parse_return` does
not require `tickets:`.

**Empty-card wait is still `{pad, hop, splash}`.** `hop-to-water` /
`hop-splash` do not newly wait empty card. `phases.py` module comment still
says “when Gene need_stack.”

**Unused types never opened.** `org` / `rsi` / `ctt` / `press` / `ops` exist
in schema and have **zero** live ids. Fingerprints at count 2
(`heading-never-090`, `leftover-prelaunch-ghost`); none at 3. RSI auto-open
never fired. Leftover `need_pr` / `need_mortimer` still have nowhere live to
point except the shim.

**Archive freeze.** `improve/README.md` still says parent numbers `I-NNN`.
I-012/I-014/I-015/I-016/I-020 have no titled twins. Gym F-007–F-009,
F-011–F-012, F-014–F-015 remain `open` with empty `decided:`. World-model Open
questions still hold old `need_stack` answers (table stays; dispatch must not
live there). Gitignored `sit-card.json` is a leftover t7 shape vs seated
east-t3. `ORG-INTERACTIONS.md` / `NEXT-ORG.md` / gym F-004 still speak leftover
(`agents_md: true`, Gene `recommended` as helm). They are not spawn prompts.

**Fence drift (nits).** PROTOCOL Gene fence has `fly:` **and** `flight:`;
DESIGN listed `flight:` first. gene.md `tickets: T-NNN \| none` vs PROTOCOL
`tickets: T-NNN [go=yes\|wait]`. `STAMP_RULES` still lists
`science_payload`/`lesson`/`systems`/`org`; `patch_ticket` does not enforce
them.

**Not this slice (left closed).** Merging `protocol fly` and `ops fly`.
`tickets block`. `ops-log.jsonl`. Expanding empty-card wait. Requiring
`tickets:` in parse. Seeding leftover gym / untitled I-items “for
completeness.” New types `ask`/`explore`/`retro`. Ticketing CHARTER /
portraits / lessons / `desk.md`.
