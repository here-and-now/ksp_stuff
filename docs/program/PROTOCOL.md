# Protocol — who hands to whom

Os is Founder. **Hank Grokman, COO** is the room sequencer (depth 1).
Speech is **name + title**. Ticket bus: `docs/program/OPS.md`.
Machine slugs stay internal.

**Mortimer Grokman, CEO** owns the objective and org RSI. **Hank**
owns who is hired, the pad, leftover/KSC hygiene
(`recover()` + Close; persist-then-KSC; never leftover-ksc load), and **after-flight tape** (`desk`,
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
| Hank | hop pid | `fly: yes` | exact `cli` (parent starts it when `commander: none`) | last-flight; lock on that **control** pid |
| Hank | Commander | `commander: jebediah` (crewed / firsts / `campaign: none`) | fly ticket + exact `cli`; abort officer | `result:` `exit:` `handoff:` |
| Hank | leftover / KSC | lock free, leftover or crash UI | desk then `recover()` + Close (`recover-probe --recover` if recoverable). Recoverable ground Debris is leftover. Persist throw → quit KSP. Never revert. Never leftover-ksc load | pad clean |
| Hank | tape | Commander CLI returned | `desk`, leftover, `attach-run`, `landing` | `ops next` — no Jeb debrief |
| Commander | Hank | hop abort leftover / crash UI | `ksc leftover` — do **not** recover or Close | Hank hygiene |
| Hank | Gus, Vehicle Engineering Lead | open vehicle tickets | ids (batch) | `capable:` on those tickets |
| Hank | Linus, Director of Research | open science tickets | ids (batch) | payload bind (blocked until vehicle `capable`) |
| Hank | Lars + Gus + Linus | open `ops --tag plan` (unsigned, or hang/bind/pulse would change `agree.md`) | **that plan ticket** (three hires, same id) | section last-write on `docs/program/agree.md`, then split to own files |
| Hank | Lars, Vehicle Systems Engineer | control **pulse** miss | ticket + `live_run` | `stack:` close |
| Hank | Wernher, Chief Systems Engineer | systems / kRPC world / **control sit/warp blocks** | ticket | systems close |
| Commander | ticket bus | miss **during hop** (still connected) | `tickets open --type control --fingerprint <stem>` | Hank after exit |
| Hank | ticket bus | miss after process exit | open control from last-flight abort **with `--fingerprint`** | Lars if needed — **no Jeb debrief** |
| Commander / hop pid | Hank | campaign clean 0 CLI exit | last-flight only | Hank tape then uncrewed re-run `cli:` — **no Gene, no Jeb** |
| Anyone | ticket bus | friction | `tickets open --fingerprint <stem>` | Hank routes |
| Hank | Mortimer | `type=ctt` / `org` / rsi×3 | ticket | RD spend / PROTOCOL mutation |
| Hank | Verena, Communications | `type=press` firsts | ticket | `story:` `shot:` |
| Hank | Eleanor, Director of Constellation Operations | `desk=eleanor` / `--tag constellation` | ticket | `net:` / Wernher ask |
| Walt, CAPCOM | Os | phase start / end / unexpected | one line, name+title | — |
| Gene (between exits) or Commander (**during hop**) | KSP window | stuck | `screenshot --name stuck-<stem>` then read PNG | scene — not a postmortem |
| Commander | radio | unusual **during hop** | `note` / hold / abort | in-flight — not a review |
| Hank | `python main.py ship` | lock live, from time to time | disk envelope (no jsonl) | uplink or hire if off-nominal. Reader `status` is `kspstuff-read` (T-454) |
| Hank | Gene | off-nominal, plan/`go` must change | `ship.md` + fly ticket | uplink / `go: wait` / tickets — **not stick** |

Linus ↛ Commander. Gus ↛ Hangar. Commander ↛ `.py`/`.craft`. Commander ↛ leftover recover / Close crash UI. Commander ↛ after-flight review / jsonl / attach-run / landing. Gene ↛ stick while lock live. Parent ↛ patch `.py` in the fly turn.
Mortimer ↛ GameData. Mortimer ↛ flight/UT in the save. Mortimer **may**
edit `persistent.sfs` ResearchAndDevelopment (`sci`, `Tech` node) when
Linus/Lars/Gene brief a paid unlock.
Commander ↛ revert / quickload / return to VAB / rewind UT. Crash UI is
honest: **Hank** recovers the ship (`recover()`) and **Close**s to KSC,
then Hangar the next stack on a **clean** pad. Persist must survive a
split wreck; skip-dup is persist not the broom. Os disabled reverting
flights. Never revert. Never leftover-ksc save/load. Os will not click
it. Screenshot when stuck; do not wait for a founder click.
Clean-pad Hangar of the seated craft for the sortie may stay inside
hop (`install_and_launch`) — that is **launch**, not leftover hygiene.
Splash HD recover of **this** hop after a briefed dwell stays mission.

**Hop light vs airborne:** `hop light` on hop stdout is pad plume, not
airborne. Lock live ≠ flying. Parent mid-hop reads `ship.md`. Do **not**
wait hop stdout. Radio already prints **thrust / plume / parts_n / fuel**
— those kv are first-class eyes. Throttle 1 + thrust 0 + plume no +
fuel frozen while parts intact is **unexpected** (engine already dead)
— **not** FAR shear. Last-flight `shear` / hop stdout `hop shear parts
N→M` is the wreck, not the cause (16-05-34Z: MET 21 thrust=0 fuel
frozen parts=30; hop logged shear 30→9 at impact). Sit/MET/log
disagree → one `screenshot --name stuck-<stem>` then read the PNG.
TUI is phase start / phase end / unexpected only (Walt). Off-nominal
Gene / Lars / Wernher is parent TUI reading `ship.md`, not `ops next`.
Lock-live `ops next` is ground batch only. After CLI: `telem --window`,
not last-flight 40.

**Inner circle (Lars / Gus / Linus):** they sit **one** achievable
plan (`docs/program/agree.md`: sit, hang, bind duration vs High
window, recover yes/no, MECO), then split to implement. Not a chat
spawn. Not Gene as merge. Not leftover `ops --tag ask`. One
`ops --tag plan` ticket is the hire packet. Hank hires the three in
**parallel on that id** — not leftover wreck tickets from the last
miss. Each last-writes **only their section** (Hang Gus, Bind Linus,
Pulse Lars), files `tickets feedback --claim`, then does their part
on their own files the same hire (`.craft` / science payload / pulse
`.py`). Katherine is **opt-in** (`ops --tag ask --desk katherine` or
`--tag dynamics`) when the plan needs tape windows / FAR / High-band
time — not every `ops next`. Eleanor is **opt-in** (`ops --tag ask
--desk eleanor` or `--tag constellation`) when the plan needs Cape /
ground / a path to a future craft — not every `ops next`. Hank talks
to her directly; inner circle (Gus / Lars / Linus / Katherine) and
anyone else may. Do **not** reopen the plan because the
last hop sheared: wreck rec=no re-flies last `cli:` **when Hank
schedules it**. Change hang / bind / recover / MECO only by rewriting
`agree.md` together. Fly ready that still pays `agree.md` may still
fly — Hank schedules hop vs ground. A conference may sit the pad;
it does **not** empty it as a religion. Idle is not a miss.

**Ground talk (between exits, lock free):** leftover `ops --tag ask`
is mail, not the shared goal. Gene, Wernher, Mortimer, Verena, Eleanor may
address by name. Still not the stick. Nominal hop: still not
mid-phase hire of Gene. Off-nominal `ship.md`: parent TUI may hire.
Still different files in one turn. They do not spawn each other.

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
`feedback:` / `good:` / `self:` / `them:` / `recommended:` / `card:` /
`need_*` as the bus. Every hire **does** file structured feedback on
the **work ticket** (packet T-id):

```
python main.py tickets feedback T-NNN --claim "…"
```

That is RSI ore, not a hire token, not a Return key, not a second
bus. Open tickets (`payload.to` = addressee on `ask`):

```
python main.py tickets open --type ops --tag ask --title "…" --desk <addressee>
python main.py tickets open --type ops --tag explore --priority P3 --title "…"
python main.py tickets open --type ops --tag plan --title "sit hang bind recover meco" --desk hank
python main.py tickets open --type ops --tag ask --desk katherine --title "High-band / FAR window"
python main.py tickets open --type ops --tag ask --desk eleanor --title "Cape path / future craft"
python main.py tickets open --type ops --tag feedback --title "…" --fingerprint <stem>
python main.py tickets open --type control --title "…" --fingerprint <stem>
python main.py tickets open --type systems --title "…" --fingerprint <stem>
python main.py tickets open --type rsi --title "…"
python main.py tickets open --type ctt --title "…"
python main.py tickets open --type press --title "…"
```

`ask` P1 if it blocks `go`. Parent opens that `ops` ticket — it does
**not** file leftover `ask:` onto the world-model table as the bus.
`need_os` is **not a ticket** (CHARTER creed / roster — Os). Leftover
`need_*` in a return is not a hire token. Desks open
with `--type` as above. Do not emit those leftover keys.
**Fingerprint** is a short stem (`flyinghigh-lid`,
`sci-unchanged-recovered`), never an abort novel, never a timestamp,
never `hop-<digits>`. Lookup `docs/program/tickets/fingerprints.json`.
Reuse the existing stem; a longer kebab aliases onto the shortest
prefix (`flyinghigh-lid-18km-hop` → `flyinghigh-lid`). Do not map
inland heading 299 onto `heading-never-090` (Water-dead). Empty fp
is **refused** on new `control` / `systems` / `ops --tag feedback`
(`legacy-twin` seed exempt) — `tickets open` prints `reuse (count):`
plus a copy line. Hop-class friction is that bump, not a remembered
CLI. Third hit opens `type=rsi` (software → Wernher, else Mortimer).
Lock live skips org; fly_ready still hires Mortimer without emptying
the pad as a religion. Idle is not a miss. Do not tell another desk in Return prose — open `ops --tag
ask` (`payload.to` / `--desk` = addressee). **Landing envelope wins**
over fly `payload.learn` (uncrewed: hop-exit `attach-run` overwrites
it; Gene stamps only when `ops next` hires him).

**Tree + hardware (F-013):** experiment_id is not a part. Every bind /
capable / `go:` / Lars science-miss packet must say **tree node** and
whether the **Science-category instrument** is unlocked and on the
craft. Stayputnik PAW is a host, not a Geiger Counter. Desk `f013` is
that line — do not send `tech` / `parts --search` if desk is this sit.
If the instrument is LOCKED: Linus does not bind it as hardware; Gus
`capable: no`; Gene `go: wait`; Lars does not patch a sit for a part we
do not have. Parent copies that line into Lars’s packet so he is not
sequencing a ghost instrument.

**Serial:** `go: yes` (Gene only); Linus **bind** after Gus `capable:`
(**FED** + f013 + EC; collider-clear HS only when the hang *has* an HS —
C-534 loft is no-HS, recover silk; C-504 shelf); one **control** writer; kRPC GET readers legal; Lars XOR Wernher on a **miss**. Open `type=systems` →
Wernher (desk/ops/ticket kernel, hangar scene, telem, kRPC trap,
**control blocks**: sit, warp, timeout, leftover abort, chute sits, sit-match)
without waiting for a miss. Flying-card Toggle at High lid is High, not InSpaceLow (T-517).
`physics_warp.py` (sit / warp / timeout / leftover abort / chute sits)
and `rf_throttle.py` (RF live catalog) are Wernher **blocks**. Lars
**composes one living rocket's pulse** from those blocks:
`hop_factory.py` inland science hop, `hop_factory_pad.py` RF pad
(**one sit**, no `_pad_*` per stamp), **`ascent.py` orbit**
(`python main.py ascent`) — Valiant loft now; Terrier two-stage later
is still this file. A t7-only compose is legal. `pad.py` /
`science.py` / `blocks.md` stay pulse/phase. `hop.py` is parked
water/splash + **shared** helpers that are actually shared. T-548
minted `ascent.py`; mint is not this-hop pulse (T-554). A miss on
`ascent.py` is Lars (`type=control`). Wernher may extract a sit-named
block from the compose into `rf_throttle.py` / `physics_warp.py`; he
does not retune loft / MECO / gravity-turn numbers in `ascent.py`.
XOR: one `.py` owner per miss of the **same** file. Legal: Wernher
blocks ∥ Lars `ascent.py`. RF live throttle is
`independentThrottlePercentage` / PAW Current Throttle — kRPC
`control.throttle` is the UI MainThrottle bar, not the burn. One
immortal factory that remembers Flea, Hammer, 4t, and splash-090 is
not the way. Do not wait Terrier to transfer `ascent.py`. Tests lock
the **blocks**, not dead-hang envelopes. No stamp-named `_after_skip`.

**Engines (Os 2026-08-25 / T-456 / T-470):** ReStockPlus liquids are RF
ullage + finite ignitions. Pad 1 g still lights. Throttle 0 then 1
is a restart. Desks verify **this hang** (cfg / ConfigCache / live
module). Do **not** paste a part→N ignition table here or in spawn
prompts. Confirmed pad light is **plume** / currentThrottle rising
after the engine fires — not ignitions remaining 1→0, not kRPC
`Engine.throttle` GET. Independent setpoint is the RF live
(`rf_throttle.apply` — not UI MainThrottle). Staging
a chute (or any empty-of-engine stage) is not hop light.
Pad-dead-no-plume with a **fed** engine is Lars `hop_factory_pad.py`
(`rf-ignition-ullage`) — not loft, not Wernher, not a GameData raise.
Tanks full and pad Δv 0/0 is **starved** (`craft fuel` BLOCKED) —
Gus `capable: no`, not RF, not Lars, not a GameData `fuelCrossFeed`
flip (C-477 dish HS). Failed coast/suicide
relight with fuel left is **engine physics** until a desk has read
that engine. RF pad is one sit — not a `_pad_*` per stamp. Do not
open `type=systems` / kRPC for “engine did not light” first. Do not
raise ignitions. Never GameData.

**Pad occupancy (Os 2026-08-26 / T-543):** Tape is the product.
**Hank schedules hops.** Pad may sit while ground cooks (inner
circle, Eleanor, leftover Close). Idle is **not** a miss. Do **not**
empty the pad as a religion. A **living recover that cannot pay is
still waste**. Wreck rec=no re-flies last `cli:` **when Hank
schedules it** — not a religion.
Inventory stays full: Linus many `science_opportunity`; Gus many
signed `.craft` alts (not one hang designed after a wreck). Gene
**picks from that shelf** a bind this hang can bank and stamps `go:`
on a fly ticket. **This-hop bind** is last-envelope biome/sit
(Forest tape is Forest; Grasslands waits Grasslands; SrfLanded vs
splash match the hang; FlyingHigh waits ≥50 km on **C-534**
`kspstuff-hop-valiant-proc-redstone-pbc` (FED, no HS, no girders;
recover silk; C-504 loft-pbc shelf), not C-477
(`capable: no` — Hangar 15-52-38Z blob even after T-500 dish), not t7-wheel-pbc
(T-400 `capable: no` — lithobrake is not recover), not a 30 km stiff
loft, not t7-chute Mk16). FlyingHigh wait is loft live-alt ≥50 km /
Toggle / cut / chute / land leftover — not a sit at 800 m apo, not
wait-then-pitch in the first km, not throttle-0 at light, not
abort-at-lid, not skip-chute, not OffPlan under `expect_apo_max`.
Silk is recover, not the wait. Throttle 1 + SAS vertical
until lid; inland slew after. Thick air ≤18 km is 1×. 4× silk /
chute Arm shears t7 — `chute_arm_sit` 1× is Arm, **not** apo
(`hop-coast-phys-warp`). Quiet loft after lid honors Hank
`phys-warp` (High dwell is not a burn). Do not Hangar FAR-sheared 4t
/ dv5 / girderless lite / a 4×-sheared t7 / t7-chute Mk16 / **C-477**
this sit. Do not Hangar **t7-wheel-nose** (T-409) as silk. Pad this
sit belongs to **C-534** until `advRocketry` 45.
C-504 tape 16-23-52Z held through burnout apo 268 km rec=no — C-534
iterates that family.
268 km loft is not orbit. Today is **first orbit** (phased): pay
Terrier this tree, circularize after `advRocketry` 45, leftover
science on the way later. Leftover High / Forest / splash stays
shelf — do not unbind forever; do not make it this-hop. Inner-circle
orbital-phase conference does **not** empty the pad.
T-428 HS-only / T-430 silk-only stay alts — not a Hangar from this
letter. Do not gather a
subject this stack cannot reach. Warp the coast (physics 2–4×;
uplink `phys-warp` / `no_warp`; never rails / WarpTo). Ground fills
the shelf **during** flight (lock live, other files). Wernher **logs
more kRPC** and explores unused 0.6 surfaces **without waiting for a
miss** (`type=systems` standing). All data is good data if stored.
A 10–15 min Gene conference, an RSI letter, “consider the 154 m/s”,
or conference-then-+0 hops does **not** empty the pad as a
religion — Hank may sit it for ground — and does **not** re-fly the
same +0 bind. After sci unchanged: rebind from the envelope or the
next signed hang that can bank. Living recover + `sci_run=0` is the
waste class (`sci-unchanged-recovered`) — **not** clean 0. Bind can
still pay = last-envelope sit/biome/apo matches bound tickets (08-44
Shores land ≠ Forest leftover; 10-57 Forest splash ≠ SrfLanded).
Wreck rec=no is a miss: re-fly last `cli:` **when Hank schedules
it**. Pad abort sit=`pre_launch` never lofted: not this waste class —
re-fly last `cli:` when scheduled (control miss). Do not rebind
FlyingHigh to a pad card (T-472). Loft-only FlyingHigh/FlyingLow bind
+ short recovered dud (655 m landed rec=yes `sci_run=0`): re-fly last
`cli:` when scheduled — High cannot pay 655 m and that does not idle
the loft or turn High into a Surface card (T-475). Forest leftover vs
Shores land still waits. Stop the batch leftover / crash UI, f013
fail, live control `.py` must be patched, or Os wait. Hank may also
sit the pad for ground. `go: wait` **only** leftover / crash UI /
f013 / empty shelf / Os wait — idle is not `go: wait`.

**Thin tape is first-class:** a 9-column space program is not a log
shrug. Every desk that stumbles on it opens `--type systems` (or
`--type ops --tag feedback`). Cite it on capable / bind / `go:` the
way `f013` is cited. Do **not** treat it as a reason to miss a
scheduled hop — Wernher patches during lock live. Idle is Hank's.
Query **Tape**, never raw jsonl. Last-flight 40
lines is abort/exit, not the vessel. **Do not reason a Learn from it.**
Last-flight rec=yes is not rec. One **control** writer; kRPC GET
readers are legal. Cadence is the writer’s duty. Desks that touch tape
file `tickets feedback --claim` and missing helpers as `type=systems
--fingerprint telem-eyes-library`. Thin pulse → `thin-tape`.

**Science side-by-side:** Linus binds every honest instrument that can
share a hop (thermo + TELEMETRY + goo + PresMat if not capped / F-013 / tape).
Not one thermo forever. Duration-file idle rem=0 (2HOT, PresMat) is
still the card — skip not-in-card is a miss when the part is on_craft
and the envelope sit can pay (`hold-ground-card`). Bound leftover
stays in the card — fly extras cannot hide splash leftover as
not-in-card; wrong sit is cannot-pay. Airborne cannot-pay is not
card-done: after High dwell, splash leftover still Toggles on splash
sit before recover. Cape **64 bps** is honest radio — TX is a tool,
not a cheat, not the only path; recover still banks the HD when
`recover()` works; file leftover credits while recording; sample
leftover is the can (Goo ~429 MB does not TX at TL2); splash leftover
unpaid is Toggle-at-sit, not a reason to forbid TX.

**Live watch (Os 2026-08-23 / T-508):** Someone looks at the hop **while it
flies**. The Commander watches telem/gates — **throttle / thrust /
plume / fuel vs parts**. Unusual →
`python main.py note <Name> "…"` and/or hold/abort per emergencies
(in-flight radio, not a review after recover). **Hank** (parent)
periodically runs **`python main.py ship`** (disk envelope from
`ship.md`). Read **thrust / plume / parts_n / fuel**. Do **not**
wait hop stdout. `hop light` is pad plume —
**not airborne**. Lock live ≠ flying. Sit/MET/log disagree → one
`screenshot --name stuck-<stem>` then read the PNG. TUI is phase
start / phase end / unexpected only (Walt). Unexpected includes
throttle 1 + thrust 0 + plume no + fuel frozen while parts intact
(engine already dead) — Walt says **engine dead**, not shear.
Lock-live `status` /
leftover GET is a reader Session (`kspstuff-read`, T-454) — it does
**not** write jsonl. Writer `Telem.read` still owns jsonl /
`ship.md`. Do not `read_file`
the growing jsonl. Off-nominal (wreck
flags, lithobrake, empty tanks + still flying, heading never moving,
EC=0 before dwell, crash UI, **engine dead with stack intact**): **do something** — parent TUI reading
`ship.md`, not `ops next`. `uplink abort|hold`
if wreck-class; spawn **Gene** if the plan/`go` must change
mid-sortie; spawn **Lars** if the living pulse / control / flameout
(`rf-ignition-ullage`); spawn **Wernher** if kRPC/telem/desk/control-blocks (`physics_warp.py`) or hop abort still names parts-drop **shear**. Issue-clear → that desk, not a Gene novel. Do not stamp `far-shear` from last-flight when radio already had thrust 0.
**Nominal** hop: no Gene, no 15 s narration, no heartbeat swallow.
“Do not spawn Gene during the phase” is **repealed for off-nominal
only**. Depth 1. Gene does **not** take the stick (hop pid is the
control writer); Gene may uplink / stamp `go: wait` / open tickets. After
CLI exit, tape is still Hank (T-101).

**Uncrewed campaign (I-016, amended):** Gene stamps
`payload.campaign=uncrewed` on the first `go: yes` of a cheap probe
sit. Seated `plan.md` is envelope only (`hop_apo` / `expect_*` /
`emergencies`) — do not copy `go` / `cli` / `campaign` onto it. Parent,
lock free, leftover clean:
`python main.py desk` then `protocol fly`. `fly: yes` /
`commander: none` → parent starts `cli:` (hop pid is the **control** writer).
**Do not hire Gene between hops** on clean 0 **or** on a miss of a
hang that is still capable. Do not hire Jeb. Learn or “consideration”
do not own the pad; Hank schedules hop vs ground. Idle is not a miss.
Uncrewed `payload.learn` is **kernel**:
hop-exit `attach-run` overwrites it every hop (`who=hank`, one line
from the envelope: landing + apo + biome + rec + sci). Next packet
prints **this** hop. Gene is not that writer. `needs_learn` stays
false. Do not restore Batch Learn.

After a hop: **Hank leftover first.** Walk home: `recover()` the ship
and **Close** to KSC (`recover-probe --recover` if recoverable). Os
disabled reverting flights. Never revert. Never leftover-ksc save/load
(that looked like a reload / return to pre-launch). Recoverable ground
Debris (pad Goo) is leftover — leftover_ship must see it; wait recover
by GUID not name. `recover()` is persist-then-KSC; Python RPC returning
is not despawn. Harmony skip-dup is persist fail-open, not the broom.
Flying rec=0 blobs that throw Kerbalism persist make recover a no-op —
quit KSP is walk home that sit (leftover-probe first after restart; no
Hangar on dirty persist). Crash-UI rec=0 MET frozen is **not** pad
occupancy (Os will not click Recover). Living SUB_ORBITAL leftover:
wait land on MET then `recover()`; Close while flying does not drop it
(`leftover-prelaunch-ghost`).
Then: clean 0 → re-fly last `cli:` **when Hank schedules it and
that bind can still pay** (envelope sit/biome/apo matches bound
tickets; FlyingHigh ≥50 km). Living recover + `sci_run=0` is **not**
that path — do not light last `cli:` on the `sci-unchanged-recovered`
bump. Wreck rec=no re-flies last `cli:` **when Hank schedules it**.
Pad abort sit=`pre_launch` re-flies last `cli:` when scheduled
(control miss, T-472) — High still cannot pay pad, and that does not
idle the loft. Loft-only High/Low bind + short recovered dud re-flies
last `cli:` when scheduled (T-475) — High cannot pay 655 m landed,
and that does not idle the loft. Miss (nonzero / ABORT / `science (none)` / `science skip`):
spawn **Lars** on the named **helper** file (`ascent.py` orbit /
`python main.py ascent`, `hop_factory_pad.py` pad-RF,
`hop_factory.py` inland, or the living rocket's compose). Warp / sit /
timeout / leftover-abort / chute-sit / RF live-throttle **blocks** →
Wernher (`physics_warp.py`, `rf_throttle.py`).
Last-flight abort `shear` / `hop shear parts N→M` is **not** the miss
class when tape already had throttle 1 + thrust 0 + plume no + fuel
frozen + parts intact — query `telem --window airborne|burnout`.
Flameout with fuel left is engine physics (`rf-ignition-ullage`,
Lars T-509) — not FAR. Kernel still naming parts-drop as hop abort is
Wernher `telem-eyes-library`, not a hop.py steal of T-509.
Failed coast/suicide relight with fuel left is engine physics
(`rf-ignition-ullage`, Lars `hop_factory_pad.py`) — not Wernher, not
`type=systems` — until ignitions remaining, ullage, and EC ignitor
are checked on **this hang**. Confirmed light is plume, not
ignitions 1→0. Pad-dead-no-plume waits that file (T-471) — High
stays High. Airborne cutoff with a **fed** tank **and a burn still owed** is the
same engine physics (T-509), not shear. Honest MECO leftover fuel
(16-23-52Z burnout fuel 28 thrust 0 parts=30 apo 268 km) is the
coast, not engine-dead.
Airborne cannot-pay skip is **not** a dwell and **not** Gene —
still loft, cut, coast, chute, land leftover, **then Toggle splash
leftover**. Skip-latch is
**FlyingLow cannot-pay only** — bound FlyingHigh waits the lid, then
Toggle. Splash / missing flying card still waits the High lid
(≥50 km); bound FlyingLow flying card is airborne Toggle. Do not
clamp `hop_apo` to 18 km. Timeout while flying:
Hank `recover()` if recoverable, else Close / `ksc leftover`. Never
revert. **sci unchanged** on a living recover:
Linus rebinds last-envelope biome/sit **before** the next light — not Lars unless the live
`.py` actually broke, not Gene to consider. Pad abort sit=`pre_launch`
is not that rebind (High stays High). Loft-only High/Low + short dud
is not that rebind either (T-475). Pad waits only for
leftover and for a patch of the **live** control `.py` (cannot hop
while Lars writes the named control `.py`). **Do not hire Gene to replan a miss.**
If `go:` is still yes and the hang still capable **and the bind
still pays**: re-fly last `cli:` after leftover **when Hank
schedules it**. If this hang died (aero shear, modules gone): next
**already-signed** Gus alt — Gene stamps that fly ticket only if it
has no `go:` yet. No alt on disk → hire Gus while leftover cleans,
not a novel. Stop the string: dirty hangar (`recover` / `blocked`),
f013 fail, Os wait, crewed/firsts Learn, empty shelf (no capable
craft in the batch), `go: wait`. Hank may also sit the pad for
ground — idle is not a miss. Gene **Learn** is campaign-stop only:
`ops next` hires him when campaign is **not** `uncrewed` and
`payload.learn` is empty (crewed / `campaign: none` / firsts).
Uncrewed Learn is already on the ticket from `attach-run`.
`python main.py protocol fly` still owns the gate — missing
`go: yes` is wait.

## Parallel (same parent turn, still depth 1)

| Together | Wait for |
|---|---|
| Inner circle on `ops --tag plan` (same ticket; Hang / Bind / Pulse sections + own files) | Gene merge; leftover wreck tickets that contradict `agree.md` |
| Linus opportunities + Gus `capable` (not bind) | Linus bind to named craft; **and** `agree.md` hang/bind |
| Wernher systems/blocks + Lars pulse on **other files** | never both on the same `.py` |
| Parent **re-desk** after Gus `capable: yes` (I-014) | Linus bind / Gene `go` on stale capable/f013 |
| Disk `python main.py world` anytime | never a second **control** writer |
| Disk `python main.py science-scan` / `comms` (MM last write) | never Kerbalism tweak cfg as gospel |
| Verena writing `docs/press/` + README from disk | Gene `shot:` before a grab |
| Parent `python main.py screenshot --name <slug>` | Verena `shot: now` (or Gene `shot:` at dwell / after-recover). No kRPC. |
| Gene / Commander `python main.py screenshot --name stuck-<stem>` | logs first; one still; read the PNG. No kRPC. |
| Retro comments on open F- items (gym archive) | Gene chairs ops; Mortimer if org/goal |
| Ground `ops --tag ask` tickets | addressee’s next spawn (lock free) |
| Hank `attach-run` uncrewed `learn` | every hop-exit (kernel overwrite) |
| Gene `payload.learn` stamp | campaign-stop / crewed / firsts; never mid-phase; never uncrewed |
| Hank `python main.py ship` (lock live) | never eat the jsonl; `status` is a GET reader (`kspstuff-read`, T-454) |

Not parallel: two Commanders; Lars on a clean 0; leftover wreck
tickets **with** an unsigned `--tag plan` (plan first, then split).
Gene **+** flight is
legal **only** off-nominal (Gene no stick). Uncrewed campaign hops
are **serial** re-flies after lock free, not two control writers. Nominal
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
`python main.py tickets packet T-NNN` (also S-/M-/C-) stdout + BRIEF.
Not BOARD.md. Not jsonl. Not `docs/lessons.md`. Not `science.md` /
`vab.md` / `blocks.md`. New science/fly/vehicle mint `S-`/`M-`/`C-`;
control / systems / ops / rsi stay `T-`. Global N. Live T- ids stay.
`read:` is desk plus at most two role paths (Lars: **named helper**;
`--tag plan`: `docs/program/agree.md`).
Tickets how-to is always skim: `docs/program/tickets/BRIEF.md`. First
command is `tickets packet <Hank-named id>` (live T- stay). PNG /
craft / last-flight only on `--deep`. Jsonl is **disk**:
`python main.py telem <jsonl>` or `tickets landing`. Do not read the
tape. **Reasoning:** inherit current TUI reasoning. Hank does **not**
copy `reasoning=` into spawn packets. Never xhigh. Packet is skim;
`--deep` is opt-in. Landing **envelope**
is a skim block on the fly ticket after `tickets attach-run`
(uncrewed `learn:` is that overwrite). Commander
`cli:` is fly `payload.cli`
**copied verbatim** (F-004) from `python main.py protocol fly` — not
Gene `recommended:`, not seated `plan.md`. Lars `read:` third path is
the **named helper file** (`ascent.py` orbit, `hop_factory_pad.py`
pad-RF, else `hop_factory.py` inland compose, `pad.py` pad,
`science.py` sit-match) — not the immortal factory for a pad miss,
not `hop.py` for a factory miss, not `physics_warp.py` /
`rf_throttle.py` (Wernher blocks). Lars first command is
that packet, skim, not a named jsonl. Parent copies **f013**
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
skill while heading never 090, and it can lie rec=yes while jsonl is
still flying. **Do not reason a Learn from last-flight 40 lines.**
**Hank** `attach-run` + `landing`
after Commander CLI exit. Uncrewed `attach-run` **overwrites**
`payload.learn` from the envelope (`who=hank`). Gene stamps
`payload.learn` from that envelope only when `ops next` hires him
(campaign-stop / crewed / firsts) — **never** from Commander Return
prose, **never** between uncrewed hops, **never** from last-flight.
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
come from the fly ticket. Missing fly ticket = wait (no plan.go
fallback). Do not vibe a hop because the last exit was 0.

Gene is the only `go:`. Hire Gene when `ops next` names him
(unstamped `go`, or campaign-stop Learn: campaign not `uncrewed` and
`payload.learn` empty), **or** lock live and parent TUI reading
`ship.md` is off-nominal and the plan/`go` must change. Lock-live
`ops next` is ground batch only. Uncrewed hops **between** (lock free)
are not Gene — and are not a skip of Learn: hop-exit `attach-run`
already wrote `payload.learn`. Crewed / `campaign: none` / firsts:
Learn each hop (`needs_learn`). Do **not** hire Gene as a merge bus
after specialists. Do not hire Gene after every clean 0 on an
uncrewed string. **Do not hire Gene to consider an uncrewed miss
after exit.** Open `type=systems` → Wernher without a Gene in
between (standing explore).

A **run** is one Commander command. Filename Earth UTC with seconds
(`2026-08-20T12-35-42Z-pad`). Review also has Kerbal UT + MET. Verena
dates stories from those lines. Logs: `docs/missions/<id>/logs/`.

## Git (Os 2026-08-25)

Every desk **commits** when they change the checkout: `.py`, `.craft`,
org (CHARTER / PROTOCOL / tickets / agents), tests, press. `git add`
the paths they touched, `git commit` with a sentence of what changed.
Do not wait for Hank or Os to harvest. Do not commit gitignored tape
(`desk.md`, `last-flight.md`, jsonl, `overlay.last`). Push is Hank/Os
unless they said otherwise.

## Return (this job)

Open tickets. Do not emit `need_*`, `ask:`, `explore:`, `improve:`,
`feedback:`, `good:`, `self:`, `them:`, Linus `card:`, or Gene
`recommended:` (`cli:` is the fence). After the work, file on the
packet T-id (T-378; not a card):

```
python main.py tickets feedback T-NNN --claim "…"
```

Body text may say `tickets open --type ops --tag
ask|explore|feedback` (paid node `--type ctt`; press `--type press`).
Leftover `need_*` is not a hire token. Do not shim leftover Return
`good:` into tickets — desks run `tickets feedback`.

**Gene** (stamps + identity; routing is ticket ids). `flight:` is tape
id. Hire is `commander_for` (`none`|`jebediah`):

```
fly: T-NNN
flight: <tape id>
seat: <kerbal | none>
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
patch `payload.cli` / `payload.campaign` / `payload.phase`. Stamp
`payload.learn` only when hired for Learn (crewed / firsts /
campaign-stop). Uncrewed: do not stamp learn (`attach-run` already
did). Seated `plan.md` is envelope only (`hop_apo` / `expect_*` /
`emergencies`). Do not copy `go` / `cli` / `campaign` onto it. Do not
emit leftover `need_*`.

**Linus**

```
science: tickets|none
tickets: T-NNN | none
f013: <instrument tech unlocked on_craft>
```

Bind = patch science payload (`experiment_id` / `part` / `duration_s` /
`ec_rate` / `recover_banks`). Do not rewrite `science.md`. Idle on open
science tickets, not `need_science`.

**Gus** — `capable:` `craft:` `f013:` FED (`craft fuel`) collider `tickets:` `blocker:` (if no). Then `tickets feedback`.

**Lars** — `tickets:` `stack:` `f013:` `blocks:`. Then `tickets feedback`.

**Wernher** — `tickets:` `ready_to_fly:` `files:` `blocker:`. Then `tickets feedback`.

**Verena** — `tickets:` `story:` `shot:` `readme:`. Then `tickets feedback`.

**Katherine** — `tickets:` `model:`. Disk tape only. Ask is a ticket
id, not a Return key. Then `tickets feedback`.

**Eleanor** — `tickets:` `net:`. Disk only (`comms` dump / `ra-rate.md`).
Ask is a ticket id, not a Return key. Then `tickets feedback`.

**Mortimer** — `goal:` `org:` `tickets:` `unlocked:` `need_os: none|charter|roster` (creed only). Drop `need_builder` / `need_qol` / `need_gene` / `recommended`. Then `tickets feedback`.

**Hank** — `ops:` `hire:` `packet:` `pad:` `why:` `rsi:`. Leftover/KSC: he **runs** `recover-probe` / `ksc` (lock free). He **schedules hops**; pad may sit while ground cooks. After Commander CLI: `desk`, `attach-run`, `landing`, leftover, then `ops next`. Child skipped `tickets feedback` → nag; harvest writes; idle is not a miss. Desks must not emit `need_*` or Return `good:`/`self:`/`them:`. Do not hire the Commander to explain the hop. Warp law is Wernher.

**Pilot** — `result:` `exit:` `handoff:` `abort:` `last:`. Then `tickets feedback` on the fly ticket (`--claim`, not a landing essay). Drop `envelope:` / `improve:` / `feedback:` / `good:` / `need_*`. CLI exit **ends** the hop. Miss `type=control` only **during** the hop if still connected; after exit Hank opens from last-flight. Hop abort `ksc leftover` → Hank, not Commander recover. No attach-run, no landing, no jsonl cite.

## Files

Gene last-writes **briefing prose + seated plan.md envelope** (`hop_apo` /
`expect_*` / `emergencies` stay on the plan). `go` / `cli` / `campaign` /
`phase` / `learn` live on the fly ticket — do not copy them onto seated
plan. Flight-layer facts on
`world-model.md` may update between exits — that is not a hire.
**Inner circle** last-writes `docs/program/agree.md` by section (Hang
Gus, Bind Linus, Pulse Lars). Katherine last-writes **Dynamics** when
pulled; Eleanor last-writes **Constellation** when pulled. That file is the
shared goal — not seated envelope, not last-flight. Gene **reads** it
when stamping `go:`; he does not chair it. Mortimer last-writes **Practice**,
PROTOCOL, and job cards on an org hire. Gus last-writes `.craft` and
vehicle-ticket payload. Linus last-writes science **payload**. Do not
rewrite `vab.md` / `science.md` dumps. Bind source is science-ticket
payload. Verena last-writes `README.md` (portrait) and `docs/press/`
(story layer). The Commander takes `uplink.md`. `loop.md` is talk, not
stick. Disagreement on hang/bind/pulse → `--tag plan`, not Gene
`go: wait`. Missing `go:` = wait.

Milestone stills. Press: Verena picks from `screenshots/runs/` after the hop (beauty beats already hid HUD). Parent `--name` / `--beauty` between exits. **Stuck:** parent mid-hop (sit/MET/log disagree), Gene (between exits), or the seated Commander **during the hop** may grab **one** HUD-on still when logs cannot explain the scene. Read the PNG. Not a postmortem after CLI exit. Not a heartbeat. Not press.

Flight cadence (capture only — do not read): `screenshots/runs/<stamp>-<command>/`. Tape: ~10 s ticks (old ticks trimmed to 3) plus sit/stage/wreck — HUD on. Press: named beats (`light`, `airborne`, `science`, `chute`, `splash`, `recover`) hide HUD (F2) and pose the camera, then restore. Verena picks from that folder after the hop. Never grim during a live `phase`. Never clobber press heroes.

```bash
python main.py screenshot --name <slug>         # screenshots/<slug>.png
python main.py screenshot --name stuck-<stem>   # Gene / Commander, stuck only
python main.py screenshot --full                # monitor-size, then restore tile
python main.py screenshot --beauty              # F2 hide HUD for a press still (flight)
```

Refuses `screenshots/first-mystery-goo.png` unless `--force`. `--full` only if the still is unreadable.

## Linus bind

Science-ticket payload:

```
experiment_id / part / duration_s / ec_rate / recover_banks: yes|no
```

Gus sizes EC from `ec_rate × duration_s` **and** proves **FED**
(`python main.py craft fuel <craft>`) **before** `capable: yes`.
Starved / BLOCKED is `capable: no`. Hangar-detonating HS splice is
`capable: no` (T-500 collider). If `world` sci does not move after a briefed recover → Linus, then Gene.

## Feedback (T-375 amended; findings)

Every hire files **at least one finding** on the **work ticket**
(packet T-id). Content is free (own work, own workflow, or a request).
Os: not a card. Not Return keys. Not `need_*`. Not a markdown log as
the bus.

```
python main.py tickets feedback T-NNN --claim "…" [--evidence "path:line"] [--owner desk|none] [--real]
```

`--claim` is the one required line. `--evidence` / `--owner` optional.
`--real` only with nonempty evidence. Cheap. Not a 15 min novel. Not
Learn. Not a hire token. Not a second bus (do not open a child
`ops --tag feedback` per hire). Kernel **appends** `payload.findings`
`{who,claim,evidence,owner,real,at}`. Close harvests nonempty
`close_why` when findings are empty; refuses if both empty.
`attach-run` harvests one `learn:` finding when empty. Packet skim
prints all findings (cap 8) and a `--claim` copy-line. `tickets inbox
--desk X --feedback` lists every `owner=X` plus owned tickets with
zero findings.

CHARTER “every hire leaves a sharper sit, a pitfall, a question, or
code” is this CLI + harvest — **not** `protocol parse`. Do not
add `good`/`self`/`them` to Return fences. Do not land
`from-feedback` as a leftover shim.

Stumble *during* work still
`tickets open --type ops --tag feedback --fingerprint <stem>`
(RSI ×3 clock). Empty stem still refused. Gym `F-NNN` / `I-NNN`
twins stay tickets. Leftover
`ask:` → `--type ops --tag ask`. Mortimer `need_os` is creed only.
