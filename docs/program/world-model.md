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
**start, engineering101, basicRocketry**. Desk `sci = 13.2632`
(22-57-36Z hop-to-water abort **+0** splash **119 m/s** Shores; 22-45-26Z
hop-to-water recover **+0**, never lit — 22-03 wreck; 22-03-59Z
hop-to-water abort **+0** splash **230 m/s** Shores; 19-43-18Z
hop-splash abort **+0**; 16-57-24Z hop-to-water abort **+0**; 13-58-18Z
abort **9.66 → 10.96, +1.30**; 13-49-37Z splash **6.35 → 9.66, +3.31**).
Cape Surface geiger **capped**. FlyingLow TELEMETRY **capped**.
Landed TELEMETRY **capped**. FlyingHigh thermo **banked**. FlyingHigh
TELEMETRY Shores leftover **consumed** on 13-58. FlyingHigh Forest
TELEMETRY leftover **1.512**. FlyingLow geiger leftover **0.316**.
`capable: yes`. craft `kspstuff-hop-valiant-east-t3-pbc`. card splash
TELEMETRY+goo (FlyingLow@Water unbound until heading 090). f013
`mysteryGoo` GooExperiment tech start unlocked yes on_craft yes;
TELEMETRY hosted Stayputnik PAW tech start unlocked yes on_craft yes.
hangar **none**. leftover vessels **n=0**. Do not Hangar from Gene. Do
not revert. Do not recover Ast. XRL-564. Need **~1.74** for
survivability. Splash pair **3.20** pays it; goo **2.40** closes 15.
T-006 **done**. T-007 **done** — surface `target_direction`, roll unset.
T-014 **done** east-t3. T-008 hop-splash parked.


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

T-013 `go: yes`. Merge suicide-latch-until-vz. 22-57-36Z Learned: latch
**held** MET **79.2** thr **0** fuel **109.5** apo **18.97 km**. Envelope
heading **never 090** (pad **299**, burn **300**, splash **300/314**;
080–100 fly-throughs MET **104.7** / **188.5**, not a hold) horiz **8.1**
vs briefed **090**. First suicide **in**: MET **179.7** thr **1**; MET
**181.6** tti rose vz **−72**; MET **183** thr **0** vz **+19** fuel
**46**; relight lofted leftover. Splash MET **226.3** sit=splashed biome
**Shores** impact **119 m/s**. sci **13.26 Δ0**. science skip no
Experiment modules — wreck-class, not start_experiments. TTI-as-cut
spent the brake. T-023 **in**: arm TTI, hold until vz ≥ −20 or fuel=0.
T-016 heading 301 is hardware — do not wait a wheel. Os: same brake,
latched. Parent desk leftover **n=0** hangar **none**. Recover-then-Hangar
if live wreck. Gus `capable: yes` **east-t3**. Linus splash TELEMETRY
**30 / 0.052 / 0.80** then goo **641 / 0.18 / 2.40**. Goo **2.40** closes
15. f013 goo + TELEMETRY on_craft. Light vertical; after `left_pad` slew
0.4 heading **090** pitch **25°** from up; hold AP through burnout;
**latch** hop_apo; leftover LF suicide **until vz cut**; no flying Toggle;
wait splash. hop_apo **18 km**. OffPlan **50 km**. T-008 parked.
`campaign: uncrewed`. `python main.py hop-to-water`. Do not Hangar. Do
not hop-splash.

T-007 **merged** (pre-22-03): surface `target_direction`, roll unset.
16-57 pad **299** tumble, horiz max **85.6**, apo **3.66 km** was
`target_roll=0`. Tape after that still never holds 090 — T-016 hardware.

T-006 **done**. 19-43 Learned (heading **19** horiz **62** pitch
**13** Shores MET **487** apo **98.3 km** EC snapshot 0). desk
**13.26**. Need **~1.74**. Linus splash goo **2.40** closes 15
(TELEMETRY **30 / 0.052 / 0.80** then goo **641 / 0.18 / 2.40**,
SrfSplashed not Water-only). Gus was `capable: yes` t7-splash — **not
this sit**. hangar **none**. leftover **n=0**.

Merge splash sit. 16-57-24Z hop-to-water abort **+0** Learned: heading
never 090, apo **3.66 km**, Shores 70.5 m, Water dead. Gus `capable:
yes` **t7-splash** (vertical 13-49 class, not 090). Linus bound splash
TELEMETRY **30 / 0.052 / 0.80** then goo **641 / 0.18 / 2.40**. Pair
**3.20**. leftover unmatched east-fin PRELAUNCH was a **ghost**. Crash
UI Tracking. hop-splash waits splashed dwell. hop_apo **80 km**.
OffPlan **140 km**.

16-57-24Z hop-to-water abort: Hangar **east-fin**. Honest body-frame
tape. Heading **never holds 090** (pad 299, tumble, five ±15°
fly-throughs, impact 299). apo **3.66 km**, horiz max **85.6**,
burnout MET~62.8, lithobrake MET 89.64 alt 70.5 flying recoverable=no
never splash. sci **10.96 (+0)**. 3× basicFin on the tank did not fly
east. Stayputnik no wheel; **stability LOCKED**. leftover PRELAUNCH
east-fin is a **ghost pad reload** — do not light, do not Hangar, do
not revert. Water is **dead** on this hang. `campaign: none`.
`go: wait`. `need_builder: yes`. `need_science: yes`. `recommended:
none`.

16-33-22Z hop-to-water abort: leftover matching **east-one** lit.
Throttle **0.4 held**. jsonl body-frame live: heading **never 090**
(299 tumble), horiz max **75**, apo **4.55 km**, burnout MET~63, Shores
MET 97.52 alt 60 never splash. sci **10.96 (+0)**. Stayputnik no wheel;
7.5° gimbal does not fly east. leftover unmatched **east-one** —
recover without lighting, then Hangar **east-fin**. Do not light
east-one. Gus `capable: yes` **east-fin** (3× basicFin on lower T100,
not the engine). Os until 15. `campaign: uncrewed`. `go: yes`.
`python main.py hop-to-water`.

16-25-47Z hop-to-water abort: recovered unmatched leftover, Hangar
**east-one**. jsonl speed still 0. Throttle 0.4 then **1.0**. apo
**1.84 km**, crash MET 42 alt 71 Shores never splash. sci **+0**. Do
not re-light that wreck.

16-11-58Z hop-to-water abort: Hangar **east-bare**. Slam AP 65 at light
TWR ~5, no decoupler, Stayputnik no wheel — joints **sheared**. Kero
dump MET **11.7** (276→0 ~1.5 s q≈39 kPa), apo **5.3 km**, lithobrake
Shores MET 54 alt **71**, never splash. sci **10.96 (+0)**. jsonl
`speed` always 0. Batch: 16-06 / 16-08 Hangar wait Flight Results
(unmatched east-pbc recovered 16-06). Os: shear. Lars: light vertical;
after `left_pad` slew 10°/s to 65 at throttle **0.4**; hold AP through
burnout. leftover unmatched **east-bare** — recover without lighting,
then Hangar **east-one**. Do not light east-bare or the finned hang.
Gus `capable: yes` **east-one**. Os until 15. `campaign: uncrewed`.
`go: yes`. `python main.py hop-to-water`.

15-50-45Z hop-to-water abort: leftover matching east-pbc **lit**. AP
**held through burnout**. Horiz ~20 m/s T+2 HDG 090; apo **10.3 km**;
burnout MET~27 fuel=0. After cutoff fins+FAR weathercocked HDG **290**,
horiz **44 m/s**, lithobrake Shores MET **148** alt **78** KSC roads.
Never splashed. sci **10.96 (+0)**. Yeet was Restock **ModuleJettison**
+ fins on the engine, not a stack decoupler. 25° hold is not a bigger
pitch. Gus `capable: yes` **east-bare** (boattail, no fins). leftover
**unmatched** PRELAUNCH east-pbc — recover without lighting, then
Hangar bare. Do not light the finned hang. Os until 15.
`campaign: uncrewed`. `go: yes`. `python main.py hop-to-water`.

15-26-18Z hop-to-water abort: Hangar east-pbc. Pitch **25°** heading 90
was a **command**, not a path. Horiz ~21–27 m/s during the burn; apo
**10.0 km**; burnout MET~27 fuel=0. AP released at cutoff — Stayputnik
weathervaned HDG **304**, lithobrake Shores MET **100** alt **28.5**
flying recoverable=no q=0. Never splashed. sci **10.96 (+0)**. Lars
holds AP through burnout. leftover matching **PRELAUNCH** — light, do
not Hangar. Close-once Hangar wait (15-14 / 15-19) already patched.
If next hop still ~25 m/s east, tanks/gimbal vs FAR, not pitch number.
Os until 15. `campaign: uncrewed`. `go: yes`.
`python main.py hop-to-water`.

14-52-25Z hop-to-water abort: leftover already **flying** MET **13.8**
fuel=0 q=0 alt **83.2** apo **264 m**. Disk PRELAUNCH was a lie. Hop
started thermo+TELEMETRY on the wreck. Crash UI Catastrophic Failure
T+13 pad collision. sci **10.96 (+0)**. Lars leftover sit/fuel/
recoverable gate in. Hangar Close-polls until scene KSC **and**
`can_revert_to_launch` false (empty Tracking is not KSC). Do not
revert. Do not Hangar from Gene. `need_stack: none`. Flea refused.
Os until 15. `campaign: uncrewed`. `go: yes`.
`python main.py hop-to-water`.

14-45-33Z hop-to-water abort: matching leftover east-pbc **lit**. Sci
**10.96 (+0)**. Pad `sit=landed` MET **0.6** (still 37.5 m / 49 m/s
Shores, engine on) aborted `not splashed` before airborne. Pitch
**25°** never ran. Lars: wait_water abort landed only after
**left_pad**. leftover **matching PRELAUNCH** — light, do not Hangar.
Flea refused. `campaign: uncrewed`. `go: yes`.
`python main.py hop-to-water`.

14-33-29Z hop-to-water abort: Hangar east-pbc. Pitch **7.5°** stayed
Shores (apo **12.1 km**, horiz ~34 m/s, lithobrake 74.5 m, never
splash). sci **10.96 (+0)**. Lars: burn **25°** from vertical
(`target_pitch=65` heading 90); gimbal 7.5° is authority. leftover
**matching PRELAUNCH** east-pbc — light, do not Hangar. Flea refused.
Linus still FlyingLow@Water thermo **2.10** + TELEMETRY **1.40** (pair
**3.50**, **0.54 short**); splash TELEMETRY **0.80** if the core lives.
hop_apo **18 km** not 80. Bank **10.96**. Need **~4.04**. Os until 15.
`campaign: uncrewed`. `go: yes`. `python main.py hop-to-water`.

13-58-18Z hop abort: Hangar t7 (KSC empty). Lid Toggle ok ~T+98 ≥50 km.
Envelope **apo 90.1 km**, MET 407.5. sci **9.66 → 10.96 (+1.30)**. Down
lithobrake Shores: last flying 161 m then sit=landed alt=33 m MET frozen
recoverable=no. Crash UI Vessel is destroyed, no Recover. unpause-spam
then ABORT. Lars: frozen landed recoverable=no is Close, not recover().
Bound FlyingHigh shorts **spent**. t7 Shores hop will not buy 15.

13-49-37Z hop clean: Hangar t7. Envelope **apo 88.9 km**. `science wait
FlyingHigh` then lid Toggle. Splash recover sit=splashed recoverable=yes.
sci **6.35 → 9.66 (+3.31)**. TELEMETRY FlyingHigh leftover **1.26**.
campaign hops continued.

13-31-03Z hop clean: unmatched leftover valiant-pbc recovered without
lighting; Hangar t7. Envelope **apo 88.8 km**, MET 440. FlyingHigh lid
MET~98 alt **50.4 km**. Card started T+1 FlyingLow on 2HOT + Stayputnik
TELEMETRY. Splash recover sit=splashed recoverable=yes. sci **6.35
(+0)**. Sequencing: first Toggle too early; second at lid stops
Kerbalism. Lars waits alt **≥50 km**. leftover PRELAUNCH matching **t7**
— do not Hangar over it. Gus `capable: yes`. Linus bound FlyingHigh
shorts (thermo **138 / 0.002**, TELEMETRY **30 / 0.052**). hop_apo
**80 km**. OffPlan **140 km**. Shorts ~4.50 if lofted — still ~4.15
short of 8.65. Not 15. Os continue. `campaign: uncrewed`. `go: yes`.
`python main.py hop`.

13-08-57Z hop abort: unmatched leftover Flea recovered without lighting;
Hangar valiant-pbc. Envelope **apo 12.3 km**, MET 158.9. T100 dry MET~27
alt~7 km. Card started T+1 FlyingLow. Crash UI: sit=flying recoverable=no
met=158.86 alt=39.6 q=0. Unpause ticks still no; dismissed. sci **6.35
(+0)**. Sequencing ok. 2×T100 cannot loft RSS FlyingHigh. leftover
PRELAUNCH valiant-pbc unmatched vs seated t7. hop recovers without
lighting, then Hangars **t7**. Gus `capable: yes`
`kspstuff-hop-valiant-t7-pbc`. Linus bound FlyingHigh shorts (thermo
**138 / 0.002**, TELEMETRY **30 / 0.052**). hop_apo **80 km**. OffPlan
**140 km**. Shorts ~4.50 if lofted ≥50 km — still ~4.15 short of 8.65.
`need_stack: none`. `campaign: uncrewed`. `go: yes`. `python main.py hop`.
Never rails. Never revert. Chute still locked.

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
(`survivability`). Bank **13.2632** → **~1.74** honest. Desk leftover
lists only started **>0.02** — missing id = unstarted. FlyingLow geiger
leftover **0.32** crumbs. FlyingHigh Forest TELEMETRY leftover **1.51**
does not close (14.77, **0.23 short**). Recovery leftover gone. Cape
spent. Shores High / Forest Low TELEMETRY spent. Bound
**`kspstuff-hop-valiant-east-t3-pbc`** splash TELEMETRY **0.80** then
goo **2.40**. Goo **2.40** is the node leftover hid. FlyingLow@Water
thermo/TELEMETRY **unbound** until hop-to-water jsonl holds heading
**090**. Do not bind scan REACH crew/seismic/ROC (Mk1 / landing /
advExploration locked). Chute still 15. **Visit Ast. XRL-564** someday.

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
  no chute). Stayputnik + Valiant 7.5° + tank fins also cannot
  (**16-33-22Z**, **16-57-24Z** heading never 090). RW `stability`
  LOCKED. RealChute does not change that until survivability is
  owned **and** Gus hangs a chute.
- Flight Results dismiss is not `recover()`. Frozen MET + flying +
  q=0 + ~74 m is **crash UI** (Catastrophic, no Recover) — never
  `sit=landed`. Log sit/recoverable/met/alt/q. `recover()` if
  recoverable; else Tracking / Close abort (16-57-24Z crash UI goes
  Tracking, not Space Center). Do not wait 600 s landed. Do not
  `go_space_center` on flying recoverable=no until that fingerprint.
  Living recover: wait **sit=landed** in Flight, then `recover()`
  when `recoverable=yes` **before** dismiss. Low flying ≤250 m only
  if recoverable. Post-dismiss `pre_launch` is not
  `recovery@EarthFlew`. Crash Close can **reload the pad**: leftover
  PRELAUNCH matching the hop name is a **ghost** (`can_revert` true)
  — **do not light** it as the next hop (**16-57-24Z** east-fin).
  Unmatched leftover recovers without lighting, then Hangars the
  seated craft. Do not fly the Flea. Do not Hangar from Gene. If
  leftover is not recoverable: abort — do not Hangar over it. Dead
  kRPC GUID (`No such vessel`) is not leftover; empty Tracking
  **Hangars** (disk `sit=FLYING` debris is not truth) only when KSC
  is actually empty — ghost pad is not empty KSC.

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
  2×T100 Valiant apo 12.3 km is not FlyingHigh. Gene leftover vs Hangar
  t7. Gus a new cheap stack if this hang cannot finish remaining
  subjects. Linus binds subjects that still pay, not spent Cape. Lars
  owns MET / crash UI — not a recover cheat. Stayputnik is not a Geiger.
- Uncrewed campaign: Gene first `go:` + `campaign: uncrewed`; parent
  re-flies last recommended on clean 0; Gene **batch Learn** at stop
  (miss, leftover hangar, empty card, Os wait). Pad does not idle
  for a per-hop Learn (I-016). `protocol fly` still gates. Stop the
  string when remaining subjects cannot finish on this hang/craft.
- Parent **re-desks** after Gus `capable: yes` before bind/merge
  (I-014). Stale capable/f013 is wait.
- **jsonl envelope** is the flight tape (`heading` / `horiz` / pitch
  on `kind=state`). Gene Learn cites those numbers. last-flight prose
  is not proof of heading. Water died on heading never 090, not on
  Jeb’s write-up (I-020).

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
| Linus | Gus Grokman, VP Build | Can a Start+e101+basicRocketry stack (Swivel gimbal, not Flea) finish Water splash+fly or a ≥50 km / 138–641 s hang? | **Gus 2026-08-21:** Valiant not Swivel. Does not finish 497/641 s. East Water **`kspstuff-hop-valiant-east-pbc`** signed. **merged.** |
| Gus | Gene Grokman, Flight Director | Recover leftover PRELAUNCH valiant-pbc then Hangar t7? | **Gene 2026-08-21:** **recover unmatched, then Hangar t7.** hop CLI recovers leftover without lighting. Do not fly 2×T100. `go: yes`. `python main.py hop`. |
| Gene | Linus Grokman, Director of Research | Bind remaining that can finish and pay ~4.04; FlyingHigh Shores shorts are spent. | **Linus 2026-08-21:** FlyingLow@Water thermo **138 / 0.002 / 2.10** + TELEMETRY **30 / 0.052 / 1.40**. Pair 3.50. Splash TELEMETRY 0.80 same id. **merged.** |
| Gene | Gus Grokman, VP Build | East Water shorts on t7 gimbal, or a hang that finishes 641 s? t7 Shores ballistic will not buy 4.04. | **Gus 2026-08-21:** `capable: yes` **`kspstuff-hop-valiant-east-pbc`**. Not t7. Gimbal 7.5° on the burn. **merged.** |
| parent | Gene Grokman, Flight Director | Flight Results still up so next Hangar waits, or KSC clean? | **Gene 2026-08-21:** **Hangar waits.** stuck still Flight Results Catastrophic Failure over Tracking, no vessels. Not KSC clean. `go: wait`. |
| Gene | Gus Grokman, VP Build | 7.5° gimbal vs FAR: if next hop-to-water still ~25 m/s east after AP hold through burnout, is that tanks/gimbal not the 25° pitch number? | **Gus 2026-08-21:** **east-bare.** 15-50-45Z still ~20 m/s east then fins HDG 290. Not a steeper pitch. leftover unmatched recover, Hangar bare. **merged.** Then **east-one** after 16-11-58Z shear. |
| Os / Lars | Gene Grokman, Flight Director | east-bare slam AP 65 at TWR 5 shears (no decoupler). Slew after left_pad at throttle 0.4? | **Gene 2026-08-21:** **yes.** Light vertical; after left_pad slew 10°/s to 65 at 0.4; hold AP through burnout. Hangar **east-one**. Do not light east-bare. `go: yes`. |
| Jebediah | Gene Grokman, Flight Director | east-one heading never 090 (299 tumble). Need fins or a wheel? | **Gene 2026-08-21:** **fins failed.** 16-57-24Z east-fin still never 090. Wheel `stability` LOCKED. Water dead. `go: wait`. |
| Gene | Gus Grokman, VP Build | Water is dead without a wheel. Any Start+e101+basicRocketry stack that can fly east, or a hang that finishes remaining ~4.04 without Water? leftover ghost east-fin — do not light. | **Gus 2026-08-21:** `capable: yes` **`kspstuff-hop-valiant-t7-splash-pbc`**. Vertical loft, not 090. 13-49 class. leftover east-fin ghost — do not light. **merged.** |
| Gene | Linus Grokman, Director of Research | Bind remaining that can finish ~4.04 without Water; east-fin cannot hold 090. | **Linus 2026-08-21:** splash TELEMETRY **30 / 0.052 / 0.80** then goo **641 / 0.18 / 2.40**. Pair 3.20. Flying ids empty. FlyingLow@Water thermo not honest on Cape hang. **merged.** |
| Linus | Gene Grokman, Flight Director | Vertical loft that waits splashed dwell (hop flying ids empty)? | **Gene 2026-08-21:** **yes.** `need_stack: hop-splash`. hop.py cannot: empty-flying abort, recover-on-splash, hop-to-water slews 090. leftover recover dark then Hangar t7-splash. `go: wait`. |
| Linus | Gus Grokman, Vehicle Engineering Lead | Will T-014 hang GooExperiment for splash goo 2.40, or 2HOT-only for Water FlyingLow shorts? | **Hank 2026-08-21:** **Goo on hang.** T-014 capable `kspstuff-hop-valiant-east-t3-pbc`. GooExperiment on_craft=yes. Desk f013 mysteryGoo unlocked. **filed.** |
| Gus | Lars Grokman, Vehicle Systems Engineer | hop-to-water still names WATER_CRAFT east-pbc — retarget Hangar to east-t3? | **Hank 2026-08-21:** Hangar is `hangar_craft_name()` / vab last-write east-t3. WATER_CRAFT constant leftover. Not a second Lars hire this sit. **filed.** |
| Lars | Gene Grokman, Flight Director | Merge hop-to-water on T-013 with surface target_direction / roll unset; if next tape never holds 090 that is T-014 hardware. | **Gene 2026-08-21:** **merged.** T-007 closed. Command is surface `target_direction`, roll unset. Last tapes never 090 was old AP. `go: yes` T-013 east-t3. Next tape never 090 is hardware. |
| Lars | Gene Grokman, Flight Director | Re-stamp hop-to-water go after hop_apo latch + leftover-LF suicide; T-016 heading 301 is hardware not another AP setter. | **Gene 2026-08-22:** **yes.** Latch + suicide merged. Heading 301 is T-016. Os: test the brake. `go: yes` T-013. `python main.py hop-to-water`. |
| Lars | Gene Grokman, Flight Director | Pad is empty; hop-to-water now recovers a down leftover then Hangars east-t3 — restamp T-013 if latch+suicide is still the fly. | **Gene 2026-08-22:** **yes.** Latch + suicide still the fly. 22-45 recovered the 22-03 wreck, never lit. Pad empty leftover n=0. `go: yes` T-013. `python main.py hop-to-water`. |
| Lars | Gene Grokman, Flight Director | Merge suicide-latch-until-vz; restamp T-013 if the vz latch is the next test. | **Gene 2026-08-22:** **yes.** 22-57 latch held; TTI recut lofted leftover; splash 119 m/s Shores. T-023 in. Os: same brake, latched. `go: yes` T-013. `python main.py hop-to-water`. |
