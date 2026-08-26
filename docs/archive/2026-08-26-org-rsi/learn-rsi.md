# Learn/RSI (applied)

All six hypotheses hold on disk. rsi-jump (2026-08-22) correctly
skipped Gene between uncrewed hops; it also skipped the only writer
who ever rolled `payload.learn`. Tape still lands. The sit does not —
until hop-exit `attach_run` overwrites it. Kernel stamps the envelope;
RSI counts stems, not novels; Gene stays off the pad. Do not restore
Batch Learn. Do not flip `needs_learn`. An RSI letter does not empty
the pad.

## 1 Sit

Lock free, leftover 0, sci 8.7721 (`docs/program/desk.md:1-8`). Last
abort is FlyingHigh lid (`:15`) — pad occupancy, not this paper.
T-081 `go: yes` `campaign: uncrewed` (`head.json:3165-3169`).
`learn:` is the 22-33-35Z envelope
(`landing: soft impact=5 m/s heading=299 horiz=0 pitch=90 sit=landed apo=1611 biome=Shores rec=yes sci=run=0 bank=8.77`,
`:3372`, `telem_run` `:3378`), not 07-06-08Z shear (still evidence
`:3123`). Packet skim prints that `learn:` (`tickets.py:505-507`).
T-013 has **no** `learn` (`head.json:542-564`, status `wont`).
T-323/T-324 `done` (`:11813-11861`). BOARD `open: 59 / 324`.
`fingerprints.json` 191 stems; count≥3 is only
`leftover-prelaunch-ghost=4` (`:88`). Count 2:
`heading-never-090`, `hung-preflight-ksc`,
`module-fields-reaction-wheels`, `science-skip-no-modules`.
`sci-unchanged-recovered=1` (`:145`). `flyinghigh-lid=1` (`:31`).
126 `"fingerprint": ""` still in `head.json`. No open RSI. Next CTT
still `stability` 18. Bank 8.7721 is not a stunt.

## 2 Then vs now (08-21 Learn vs 08-23 silence)

Then (08-21/22): Gene **Batch Learn** even on uncrewed T-013
(`docs/crew/log/gene.md` ×10, e.g. `:12-39`). `heading-never-090`
reused (count 2). Tape (heading never 090, suicide latch, crumbs)
moved Lars tickets. T-013 never got the field.

Now (08-23/24): rsi-jump law is live (`CHARTER.md:150-152`,
`PROTOCOL.md:187-191`, `OPS.md:368-375`). Gene newest lines are
“Not Learn (uncrewed)” (`docs/crew/log/gene.md:3-4`). 08-23 reviews
still nag “Stamp payload.learn” in the archive; live `learn_block`
drops that nag when `campaign=uncrewed` (`review.py:269-270`).
Kernel one-liner is the sit. Lars still patches and writes
`lessons.md`; unique/empty fps so RSI never rolled the inland
299 / Shores / hop-down class. CHARTER “every hire leaves a sharper
sit” (`CHARTER.md:14-16`) is no longer speech: the next packet
reads this hop.

## 3 Why it died

`needs_learn` is false if `campaign=uncrewed` (`tickets.py:763-769`).
`ops next` fly_ready hires Hank, not Gene (`ops.py:234-246`). Gene
Learn is only `needing_go` (`:274-282`). Hop-exit already
`attach_run`s (`main.py:98-105`) but, before T-323, wrote
`payload.landing` not `learn`. Frozen 07-06-08Z shear latched
`needs_learn` false anyway. Review nags a hire the kernel will not
make. Hank after-flight omitted `--fingerprint` → T-151…T-164 `""`.
Desks wrote log novels (crew logs: **0** `fingerprint` after search,
except Verena once). Return fences forbid `feedback:` / `need_*`
(`PROTOCOL.md:80-87`) so the allowed body CLI went unused.
`from_need` increments `stack`/`builder`, not the miss class
(`tickets.py:540`). `seed_legacy` still mints empty-fp twins
(`:1264-1273`, `legacy-twin` exempt). Clock is fine
(`tickets.py:153-170`, `:266-290`, `:1061-1096`); input never
collided.

## 4 Design

**Primary:** hop-exit `attach_run` overwrites `payload.learn`
(`who=hank`) from `format_landing` + apo + biome + rec + sci
(`tickets.py:893-927`, `:971-1008`). Next packet is this hop. Gene
unhired. `needs_learn` stays false for uncrewed. Reject Nth +0 Gene
(I-016 / `OPS.md:297-298`). Reject Return one-liner (kernel never
files the fence; Gene `learn:` is unused proof).

**Fingerprints.** Reuse the class (`heading-never-090`,
`sci-unchanged-recovered`, `flyinghigh-lid`). Alias longer kebab
onto the shortest existing prefix (`flyinghigh-lid-18km-hop` →
`flyinghigh-lid`). Refuse empty on `control` / `systems` /
`ops --tag feedback` (`legacy-twin` exempt); error prints
`reuse (count):` plus a copy line (`tickets.py:173-180`,
`:206-227`, `:598-600`). Novels (`hop-<digits>`, timestamps,
abort >80 chars) → `""`. `_rebuild` counts patch-add-fp and `fp`
bumps. Living recover + `sci_run=0` bumps
`sci-unchanged-recovered` once per new jsonl. Do **not** map inland
heading 299 → `heading-never-090` (Water-dead). ×3 still opens
`type=rsi`; lock-live still skips Mortimer (`ops.py:210-220`);
fly_ready already hires him without emptying the pad (`:254-256`).

**Feedback door.** Hop-class friction is the bump, not a remembered
CLI. House friction keeps **one** tag: `ops --tag feedback
--fingerprint <existing>`. No new TYPE. **Amended T-375 / T-378 (Os):**
after-hire door is `tickets feedback T-NNN --good --self --them` on
the work ticket — not Return keys, not a card.

## 5 Files changed

| file | change | owner | why | learn win |
|---|---|---|---|---|
| `tickets.py` `attach_run` | overwrite `learn` one-liner; `stamp_learn` `who=hank` | wernher | path already runs | next packet is this hop |
| `tickets.py` `open_ticket` | refuse empty fp; alias prefix; print catalog | wernher | T-151 `""` | ×3 can fire |
| `tickets.py` `_rebuild` / attach_run | increment on patch-add-fp; +0 bump | wernher | Forest +0 never counted | RSI on waste class |
| `review.py` `learn_block` | no Stamp nag when campaign=uncrewed | wernher | nag is a lie | no Gene novel |
| `tests/test_tickets.py` | auto-stamp; refuse empty; alias; +0 bump | wernher | law | no regress |
| `.grok/agents/{hank,gene,lars,mortimer}.md` + `BRIEF.md` | always `--fingerprint`; kernel learn | mortimer | cards omit/gag | desks stop minting |
| `PROTOCOL.md` `OPS.md` Learn | attach_run owns uncrewed `learn` | mortimer | docs said Gene | next hire reads ticket |
| `world-model.md` Practice | skip-Learn pitfall (`:398-405`) | mortimer | Practice is the sit | CHARTER not speech |

`main.py:105` still passes `who="wernher"` into `attach_run`; the
learn stamp inside is hank (`tickets.py:1000`). Sit is correct;
caller attribution is leftover (§10).

## 6 Tests

`tests/test_tickets.py`: refuse empty on control and `ops --tag
feedback`; legacy-twin exempt (`:199-228`). Alias
`flyinghigh-lid-18km-hop` → `flyinghigh-lid`; inland 299 is not
`heading-never-090` (`:230-272`). +0 bump once per new jsonl, not
on same path or wreck (`:1245-1309`). Uncrewed `needs_learn` false
(`:78-81`, `:1279`). Review drops Stamp nag (`:1358-1401`). Packet
skim has `learn:` (`:1280-1282`). No `tests/test_review.py` in tree
(cases live here). Quoted run: **133 OK** in 0.5s
(`test_tickets` `test_protocol` `test_protocol_gate` `test_desk`
`test_world`). `needs_learn` uncrewed=false was not flipped.

## 7 Skeptics

Overscope **real=false**. `TYPES` still 11 (`tickets.py:19-31`).
Feedback stays `ops --tag` (`:173-180`). `hop.py` /
`hop_factory.py` / `physics_warp.py` have no `payload.learn` /
`fingerprint_required` matches. `protocol.py:132` still
`ff.get("go") or plan.get("go")`. CHARTER creed, portraits, and
`docs/lessons.md` were not ticketed. Uncrewed `go: yes` still
hires Hank (`ops.py:234-246`). One kRPC writer: hop-exit
`attach_run` is disk (`main.py:98-105`). Historical catalog is
still 1-heavy; new opens are fail-closed. `science-skip-no-modules`
is now count 2 (`fingerprints.json:147`) — still not ×3.

## 8 Tickets opened

| id | type | desk | fp | status |
|---|---|---|---|---|
| T-323 | systems | wernher | `payload-learn-attach` | done |
| T-324 | org | mortimer | `learn-rsi-jump` | done |

Do not mint a third id for `sci-unchanged-recovered` or
`flyinghigh-lid`. Do not open RSI until the clock ticks. This file
is the applied write. Leftover kernel nits (§10) — one systems
ticket, reuse `payload-learn-attach` (count 2, not ×3):

```
python main.py tickets open --type systems --category bug --title "Leftover learn-rsi: hop-exit attach_run who=wernher; from_need stack/builder; ops needing_go still batch Learn" --severity S3 --priority P2 --desk wernher --fingerprint payload-learn-attach --tag learn --reporter "Mortimer Grokman, CEO"
```

## 9 Still markdown and why

Crew logs, `lessons.md` headings, Practice, portraits, archived
reviews stay markdown: voice, pitfall, run title — not the sit
object. CHARTER sit is `payload.learn` + packet skim. Lars
`lessons.md` heading **names** the reusable fingerprint
(`.grok/agents/lars.md:88-90`); that is not RSI. Gene log novels
that duplicate `go`/`cli`/`campaign` are waste; the door is
`ops --tag feedback --fingerprint <stem>`. Return fences still
forbid `feedback:` / `need_*`. Kernel does not parse Return
`learn:`. Practice last-write is from rsi tickets (stem, count,
pitfall), not only Os letters.

## 10 Open risks

- Hop-exit still `attach_run(..., who="wernher")` (`main.py:105`).
- `from_need` still fingerprints `stack`/`builder` (`tickets.py:540`).
- `seed_legacy` lesson twins still `fingerprint=""` (`:1264-1273`) —
  exempt by design.
- Historical 126 empty fps and abort-novel keys
  (`fingerprints.json:2`, `:146`, `:160`) are not re-normalized.
  Clock ticks on **new** opens.
- `ops.py:278` hire-why still says “batch Learn”.
- Hop-exit `attach_run` exceptions are swallowed (`main.py:106-107`).
- `sci-unchanged-recovered` T-337 RSI ×3 (stem count 4). Practice
  last-write: living +0 is not clean-0 re-fly; envelope sit/biome
  must match bound tickets. Splash now T-313/T-288. Chute-late is
  T-339 (`chute-deploy-sit`).
- Lock-live still skips Mortimer (`ops.py:210-220`) — by design.
- Gene log still novels (`docs/crew/log/gene.md:3`). Cards patched;
  habit is not.
- T-081 last abort is FlyingHigh lid. Bind T-069 is already T-321.
  Pad occupancy is Hank. Do not idle the pad for this paper.
