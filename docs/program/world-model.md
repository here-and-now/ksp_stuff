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
**start, engineering101, basicRocketry**. Desk `sci = 4.4896`
(10-47-59Z **4.0894 → 4.4896, +0.4002** — geiger file, recover missed).
Cape Surface geiger **capped**. FlyingLow TELEMETRY **capped**. Landed
TELEMETRY **capped**. FlyingLow thermo leftover **0.045**.
`recovery@EarthFlew` leftover **0.167**. FlyingLow geiger leftover
**2.098**. `capable: yes`. craft `kspstuff-hop-flea-pbc`. card
`geigerCounter`. f013 `kerbalism-geigercounter` tech engineering101
unlocked yes on_craft yes. KSC empty. hangar: none. Do not recover
Ast. XRL-564.

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

11-09-13Z hop miss: exit 0, sci **4.49 unchanged**. Geiger started.
FAR envelope **apo 7.5 km** held. Last telem **flying 75 m**, MET 66,
EC 9.9 — same lithobrake as 10-47-59Z. `recoverable=no` through wreck.
`recover()` after dismiss logged recovered sit=pre_launch; not
`recovery@EarthFlew`. Leftovers still **2.10** geiger / **0.17** HD.
Lars: `recover()` while still Flight at ≤250 m. Same hop. Gus
`capable: yes`. f013 on_craft yes. KSC empty. `go: yes`.
`python main.py hop`. Catalog 497 is not a hang expect. hop_apo 18 km
is a cut wish. OffPlan lid 50 km. Never rails. Never revert. Chute
still locked.

10-47-59Z: geiger filed **+0.40**; recover never (600 s then dismiss).
10-42-32Z living recover: flying 199 m, EC 306, sci **+1.13**.
10-30-35Z taught dismiss ≠ bank (wreck 74 m, EC=0).

## Horizon (Linus)

start + e101 + basicRocketry owned. FlyingLow geiger leftover **2.10**
still hang-limited (Flea ~64 s files ~0.35). Recovery leftover **0.17**.
Survivability 15 wants ~10.51. **Visit Ast. XRL-564** someday.

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
- Flight Results dismiss is not `recover()`. Flying ≤250 m calls
  `recover()` while still Flight. Post-dismiss `pre_launch` recoverable
  is not `recovery@EarthFlew`. Last 1 Hz may still be flying at KSC
  range.

**Open (aero):** FAR hops 10-30-35Z wreck apo 7.6 km / 10-42-32Z living
apo 7.5 km / 10-47-59Z and 11-09-13Z lithobrake apo 7.5 km at 75 m.
Envelope held. RealChute still locked. RealHeat not the story this fly.

---

## Practice (Mortimer)

- `desk.md` is the sit. Children do not re-run `world`/`tech`/`parts`
  if that file is this sit.
- `hangar:` is the Hangar call (`none` / `recover <name>` / `blocked`).
- `f013` on every bind / capable / `go:` / miss. Missing line = wait.
- `agents_md: false`. Gene max two hires per sit. Lars miss only.
- `load rd-<node>` never `load persistent`. One kRPC writer. No rewind.
- Os mid-flight → parent reads `ship.md`. Wreck → Walt + one PNG.
- Seat **`~/Games/KSP-rss` / letsgrok**. `KSP-RO` is a parked tree.

## Open questions (between exits)

| from | to | q | status |
|---|---|---|---|
| parent | Lars | FAR+RealHeat on the next hop: keep `python main.py hop` or `need_stack` first? | **Gene 2026-08-21:** keep hop. Envelope apo ~7.5 km both flies. Miss was dismiss, not Q. `need_stack: none`. |
| Lars | Gene | Next hop Hangars for a living recover after unpause, not a wreck dismiss? | **Gene 2026-08-21:** **done** 10-42-32Z. Living recover banked +1.13. |
| parent | Gus | Any chute at this tree? Disk: survivability LOCKED. | **answered 2026-08-21:** no unlocked chute. RC_cone / Mk16 are survivability 15. |
| Gene | Gus Grokman, VP Build | Hang `kerbalism-geigercounter` on a hop-named motor (not geiger-pbc); sign recover-HD, not 497 s FlyingLow. | **Gus 2026-08-21:** `capable: yes` `kspstuff-hop-flea-pbc`. Geiger part on Flea. Recover-HD, not 497 s. **merged.** |
| Jebediah | Lars Grokman, Vehicle Engineering | Recover line: recoverable+situation so flying-KSC-range vs splash vs wreck is obvious. Last 1 Hz still flying alt=199 m. | **Lars 10-47-59Z:** 1 Hz recover line names sit + recoverable. **done.** |
