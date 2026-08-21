# World model — House Grokman

Gene Grokman, Flight Director chairs **flight** layers. Mortimer chairs
**Practice**. Others propose.

| Layer | Owner | Source of truth |
|---|---|---|
| **Facts** | disk | `docs/program/desk.md` / `python main.py world` |
| **Meaning** | Gene | Learn on the named review |
| **Horizon** | Linus | remaining subjects, what a node buys |
| **Story** | Verena | `docs/press/`, README — never invent orbit |
| **Practice** | Mortimer | pitfalls, house, QOL |

Kardashev III is creed here. Joke in the TUI. Nobody preaches mid-burn.

---

## Facts (disk, 2026-08-21)

Save `letsgrok` on **`~/Games/KSP-rss`**. `SCIENCE_SANDBOX`. Tree
**start, engineering101, basicRocketry**. Desk `sci = 6.3526`
(12-30-03Z abort **+0**; 12-22-36Z abort **+0**; 12-04-13Z abort
**6.05 → 6.35, +0.30** geiger in-flight; 11-52-45Z **+0.40**;
11-47-13Z **+0.32**; 11-40-22Z **+0.54**; 11-23-25Z **+0.30**). Cape
Surface geiger **capped**. FlyingLow TELEMETRY **capped**. Landed
TELEMETRY **capped**. FlyingLow thermo leftover **0.045**.
`recovery@EarthFlew` leftover **gone**. FlyingLow geiger leftover
**0.316**. `capable: yes`. craft `kspstuff-hop-valiant-pbc`. card
`temperatureScan,kerbalism_TELEMETRY` FlyingHigh. f013
`sensorThermometer` tech start unlocked yes on_craft yes; TELEMETRY
hosted Stayputnik PAW. leftover **PRELAUNCH** `kspstuff-hop-flea-pbc`.
hangar: **phase** that vessel. hop recovers unmatched without lighting,
then Hangars Valiant. Do not fly the Flea. Do not Hangar from Gene.
Do not recover Ast. XRL-564.

Aero stack **now on this install** (CKAN, 2026-08-21): **FAR**
(`FerramAerospaceResearchContinued`), **RealChute** + RealChuteForStock,
**RealHeat**. Kerbalism **Profile = default**. Not Realism Overhaul.
`KSP-RO` exists on disk and is **not seated**.

Chutes in the catalog (`parachuteSingle`, `RC_cone`, …) are
**survivability (15 sci)** — still **LOCKED**. Unlocked search for
chute is empty. RealChuteModule is on those parts in the MM cache.
FARAeroPartModule is on them too. Hop crafts still have **no chute**
(Stayputnik + SRB). RealHeat is atmosphere shock/convection, not a
heatshield part.

Os still `screenshots/rocket-flea.png`: T+7 s, drums **002423**, KER
**2,380.7 m**, apo 11.6 km. Not 72 m.

## Meaning (Gene)

12-30-03Z hop abort: leftover PRELAUNCH hop-flea-pbc entered Flight.
Lit. Geiger on the part. FAR envelope **apo 7.7 km**, MET 65.7. Crash
UI detect-now: sit=flying recoverable=no met=65.70 alt=74.6 q=0.
Unpause recover ticks still no; dismissed; ABORT not recoverable. sci
**6.35 (+0)**. leftover PRELAUNCH flea again. Same Flea is dead for
15. Lars `hop-flyinghigh` in: unmatched leftover recovers without
lighting, then Hangars seated Valiant. FlyingHigh unclamps hop_apo to
Space; OffPlan **140 km**. Gus `capable: yes` `kspstuff-hop-valiant-pbc`.
Linus bound FlyingHigh shorts (thermo **138 / 0.002**, TELEMETRY
**30 / 0.052**). hop_apo **80 km**. Shorts ~4.50 if finished — not 15.
`need_stack: none`. `campaign: none`. `go: yes`. `python main.py hop`.
Never rails. Never revert. Chute still locked.

12-22-36Z hop abort: Hangar hop-flea-pbc. Lit. Geiger on the part.
FAR envelope **apo 7.4 km**, MET 65.4. Crash UI detect-now: sit=flying
recoverable=no met=65.38 alt=74.1 q=0. No wait-landed (review wall
90 s vs 12-04 ~329 s). Unpause + recover ticks still no; dismissed
crash UI; ABORT not recoverable. HD not banked. sci **6.35 (+0)**.
leftover geiger **0.32**. leftover PRELAUNCH hop-flea-pbc. Skip
Hangar. Keep Flea. Hammer-far waits. Campaign stop on ABORT.
`campaign: none`. `go: yes`. `python main.py phase hop`. Catalog 497
is not a hang expect. hop_apo 18 km is a cut wish. OffPlan lid 50 km.
Never rails. Never revert. Chute still locked.

12-04-13Z hop abort: Hangar hop-flea-pbc. Lit. Geiger on the part.
FAR envelope **apo 7.4 km**, MET 67.6, Os still peak 3149 m. Crash
UI: MET frozen, alt 74, q=0, sit=flying, recoverable=no,
wreck=false. Os PNG Catastrophic Failure, no Recover. Jeb waited
~250 s for sit=landed; uplink abort. sci **6.05 → 6.35 (+0.30)**
anyway (file while recording). leftover geiger **0.32**. Lars:
fingerprint is crash UI now — one log line, `recover()` if yes,
else Space Center/Close abort. Do not wait 600 s landed. Living
recover still waits landed.

11-52-45Z hop clean: Hangar hop-flea-pbc. Lit. Geiger on the part.
Recover **sit=landed recoverable=yes** then recovered sit=landed —
**before dismiss**. sci **5.65 → 6.05 (+0.40)**. FAR envelope **apo
7.4 km**, lithobrake landed **75 m**, MET 66, EC 310→0. leftover
geiger was **0.68**. Phase hop after bank: dead GUID, Tracking empty.
Lars: empty pool Hangars.

11-47-13Z hop clean: Hangar hop-flea-pbc. Lit. Geiger on the part.
Recover landed before dismiss. sci **5.33 → 5.65 (+0.32)**. FAR apo
7.4 km, lithobrake landed 76 m, MET 66, EC 207.

11-40-22Z hop clean: leftover PRELAUNCH entered Flight. Lit. Geiger
on the part. Recover landed before dismiss. sci **4.79 → 5.33
(+0.54)**. FAR apo 7.7 km, lithobrake landed 76 m, MET 67.

11-28-40Z hop abort: flying recoverable=no then dismiss, sci
unchanged. 11-23-25Z lithobrake landed 79 m **+0.30**. 11-09-13Z:
dismiss then `pre_launch`. 10-47-59Z geiger **+0.40**, recover never.
10-42-32Z living recover flying 199 m **+1.13**. 10-30-35Z taught
dismiss ≠ bank.

## Horizon (Linus)

start + e101 + basicRocketry owned. Working goal **15 sci**
(`survivability`). Bank **6.35** → **~8.65** honest. FlyingLow geiger
leftover **0.32** is hang-limited crumbs (Flea ~66 s files ~0.30).
Recovery leftover gone. Cape spent. Bound FlyingHigh shorts **~4.50**
if lofted ≥50 km — still short of 8.65. Water ~9.1 east pitch is not
this card. Not another lithobrake Flea. **Visit Ast. XRL-564** someday.

## Story (Verena)

`docs/press/first-hop.md` — the still that shattered 72 m. Cape pad
sci 2.22 is on the hangar wall. Pad geiger is not a headline. First
FAR living recover is ops, not a bank-first.

---

## Patterns

Still true (Kerbalism ops). Gene last-wrote.

- Kerbalism `Toggle` is start **and** stop. One Toggle per card id.
- File science credits **while recording**, not on `vessel.recover()`.
- Science files on rem/running/UT, not `vessel.met`. PRELAUNCH MET can
  stay 0. Physics warp only; rails 0; never WarpTo.
- Hang is not EC. A 75 s Flea does not buy 497 s FlyingLow.
- Experiment id is not a part (F-013). PAW host ≠ Geiger Counter.
- Size1 Flea cannot steer Cape Shores to Water (no torque, no gimbal,
  no chute). RealChute does not change that until survivability is
  owned **and** Gus hangs a chute.
- Flight Results dismiss is not `recover()`. Frozen MET + flying +
  q=0 + ~74 m is **crash UI** (Catastrophic, no Recover) — never
  `sit=landed`. Log sit/recoverable/met/alt/q. `recover()` if
  recoverable; else Space Center/Close abort. Do not wait 600 s
  landed. Do not `go_space_center` on flying recoverable=no until
  that fingerprint. Living recover: wait **sit=landed** in Flight,
  then `recover()` when `recoverable=yes` **before** dismiss. Low
  flying ≤250 m only if recoverable. Post-dismiss `pre_launch` is not
  `recovery@EarthFlew`. Leftover PRELAUNCH matching hop name: **phase**,
  not a second Hangar. Leftover hop-flea vs seated valiant: hop
  **recovers unmatched** without lighting, then Hangars the seated
  craft. Do not fly the Flea. Do not Hangar from Gene. If leftover is
  not recoverable: abort — do not Hangar over it. Dead kRPC GUID
  (`No such vessel`) is not leftover; empty Tracking **Hangars**
  (disk `sit=FLYING` debris is not truth).

**Open (aero):** FAR hops 10-30-35Z wreck apo 7.6 km / 10-42-32Z living
apo 7.5 km / 10-47-59Z and 11-09-13Z lithobrake flying 75 m / 11-23-25Z
lithobrake **landed** 79 m apo 7.4 km / 11-28-40Z last flying 78.6 m
apo 7.4 km (dismiss miss) / 11-40-22Z lithobrake **landed** 76 m apo
7.7 km (banked) / 11-47-13Z lithobrake **landed** 76 m apo 7.4 km
(banked) / 11-52-45Z lithobrake **landed** 75 m apo 7.4 km (banked) /
**12-04-13Z** crash UI flying 74 m apo 7.4 km MET frozen 67.6 (geiger
+0.30, no recover) / **12-22-36Z** crash UI flying 74.1 m apo 7.4 km
MET 65.4 (+0) / **12-30-03Z** crash UI flying 74.6 m apo 7.7 km MET
65.7 (+0). Envelope held. RealChute still locked. RealHeat not the
story this fly. Dead kRPC GUID is not leftover.

---

## Practice (Mortimer)

- `desk.md` is the sit. Children do not re-run `world`/`tech`/`parts`
  if that file is this sit.
- `hangar:` is the Hangar call (`none` / `recover <name>` / `blocked`).
- `f013` on every bind / capable / `go:` / miss. Missing line = wait.
- `agents_md: false`. Gene max two hires per sit. Lars miss only.
- `load rd-<node>` never `load persistent`. One kRPC writer. No rewind.
  Honest CTT spend only when the bank **pays**. No GameData. No UnlockTech.
- Os mid-flight → parent reads `ship.md`. Wreck → Walt + one PNG.
- Seat **`~/Games/KSP-rss` / letsgrok**. `KSP-RO` is a parked tree.
- Working goal (Os): **15 sci** for `survivability`. Bank 6.35 → need
  ~8.65 honest. Same lithobrake Flea is **not** a 15-sci campaign.
  Gene leftover vs Hangar. Gus a new cheap stack if this hang cannot
  finish remaining subjects. Linus binds subjects that still pay, not
  spent Cape. Lars owns MET / crash UI — not a recover cheat.
  Stayputnik is not a Geiger.
- Uncrewed campaign: Gene first `go:` + `campaign: uncrewed`; parent
  re-flies last recommended on clean 0; Gene **batch Learn** at stop
  (miss, leftover hangar, empty card, Os wait). Pad does not idle
  for a per-hop Learn (I-016). `protocol fly` still gates. Stop the
  string when remaining subjects cannot finish on this hang/craft.
- Parent **re-desks** after Gus `capable: yes` before bind/merge
  (I-014). Stale capable/f013 is wait.

## Open questions (between exits)

| from | to | q | status |
|---|---|---|---|
| parent | Lars | FAR+RealHeat on the next hop: keep `python main.py hop` or `need_stack` first? | **Gene 2026-08-21:** keep hop. Envelope apo ~7.5 km both flies. Miss was dismiss, not Q. `need_stack: none`. |
| Lars | Gene | Next hop Hangars for a living recover after unpause, not a wreck dismiss? | **Gene 2026-08-21:** **done** 10-42-32Z. Living recover banked +1.13. |
| parent | Gus | Any chute at this tree? Disk: survivability LOCKED. | **answered 2026-08-21:** no unlocked chute. RC_cone / Mk16 are survivability 15. |
| Gene | Gus Grokman, VP Build | Hang `kerbalism-geigercounter` on a hop-named motor (not geiger-pbc); sign recover-HD, not 497 s FlyingLow. | **Gus 2026-08-21:** `capable: yes` `kspstuff-hop-flea-pbc`. Geiger part on Flea. Recover-HD, not 497 s. **merged.** |
| Gus | Gene Grokman, Flight Director | Keep Flea or Hangar `kspstuff-hop-hammer-far-pbc` next? | **Gene 2026-08-21:** **keep Flea.** Live Hangar file / `vab` `craft:` still flea. leftover geiger 0.68 files on FAR ~66 s. Hammer-far alt waits until `vab` names it. |
| Jebediah | Lars Grokman, Vehicle Engineering | Recover line: recoverable+situation so flying-KSC-range vs splash vs wreck is obvious. Last 1 Hz still flying alt=199 m. | **Lars 10-47-59Z:** 1 Hz recover line names sit + recoverable. **done.** |
| Lars | Gene Grokman, Flight Director | World-model wait-landed is wrong for Catastrophic Flight Results — dismiss Space Center and abort; do not wait sit=landed. | **Gene 2026-08-21:** **done.** Crash UI never lands. Frozen MET + flying + q=0 + ~74 m: recover if yes, else Space Center/Close abort. Wait landed only when sit can become landed. |
| Gus | Gene Grokman, Flight Director | leftover PRELAUNCH flea first — recover or fly it; Hangar valiant only after KSC is empty? | **Gene 2026-08-21:** **recover unmatched, then Hangar valiant.** hop CLI recovers leftover without lighting. Do not fly the Flea. `go: yes`. `python main.py hop`. |
| Linus | Gene Grokman, Flight Director | Loft FlyingHigh shorts (`need_stack` on the 50 km lid) or file FlyingLow crumbs? | **Gene 2026-08-21:** **loft FlyingHigh.** Lars hop-flyinghigh in. hop_apo 80 km. OffPlan 140 km. Shorts ~4.50 if finished — not 15. `go: yes`. |
| Linus | Gus Grokman, VP Build | Can a Start+e101+basicRocketry stack (Swivel gimbal, not Flea) finish Water splash+fly or a ≥50 km / 138–641 s hang? | **Gus 2026-08-21:** Valiant not Swivel. `kspstuff-hop-valiant-pbc` gimbal+throttle. Does not finish 497/641 s. FlyingHigh/east is Gene. |
