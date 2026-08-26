# Feedback plan (compile, no apply)

T-378 shipped `--good --self --them` (`tickets.py:1605–1607`). Flying desks never typed it. Os rejected the trio. Replace with skeptic-shaped **findings** on the work T-id. Harvest **writes** a row (Skeptic 1 `real=true`). No apply. No new TYPE. No Return keys. No hop.py.

## 1 Sit

Lock free, leftover 0, T-081 `go: yes` uncrewed (`desk.md:1–12`; `head.json:3220`). `learn:` 16-02-25Z 101 m/s Shores rec=no (`:3429`). Bind FlyingHigh T-069/T-368/T-369 (`:3436–3454`); craft t7-chute-pbc (`:3456`). BOARD 62/379; open `tag=feedback` **0** (`BOARD.md:3–7`). Four `payload.feedback` rows: mortimer×2 + wernher×2 on T-375/378/379 (`:13356`, `:13443`, `:13450`, `:13495`). Flying desks who **0**. `feedback-return: 2`. `TYPES` 11 (`tickets.py:19–31`). SCHEMAS have no finding (`protocol.py:12–22`).

## 2 What the last loop did

**Gene.** `go: yes` T-081 08-23/24 (`docs/crew/log/gene.md:3–10`); Not Learn; newest seats T-318 vs t7; T-321 ask→Linus (`head.json:11651`). **0** rows. **Lars.** T-335 compose then lid/chute `if`s (`hop_factory.py:33–58`; `docs/crew/log/lars.md:3–8`). T-326/T-374 `payload: {}` (`head.json:11990`, `:13315`) before T-378. T-379 `close_why` “No hop_factory” (`:13482`) — false (`hop_factory.py:1`). who=lars **0**. **Wernher.** T-378 kernel (`tickets.py:586–627`); T-379 extract; `leftover_wreck_before_light` still `hop.py:892`; two of four rows. **Gus.** t7 88.8 km (`docs/crew/log/gus.md:3`). **0**. **Linus.** High binds vs 2.5 km Shores (`docs/crew/log/linus.md:3`; `:3429` vs `:3436`). **0**. **Hank.** `attach-run` wrote learn (`tickets.py:1218`); nag, do not idle pad (`.grok/agents/hank.md:115`). **0**. **Commander.** `none`; pilot fence still trio (`PROTOCOL.md:420`). Unused.

## 3 What went well

t7 88 km (Gus T-366). Leftover recover, not revert. Kernel `attach-run` learn (T-323). T-335 XOR compose. Gene off stick, did not overwrite `learn`. rsi-jump killed Return keys. Some sits extracted. Fingerprints reused (`flyinghigh-lid`).

## 4 What went wrong

T-378 is a three-slot card. Flying desks never typed it. Close-refuse cannot bind T-081. Last-row inbox kills `them=lars` (`test_tickets.py:351`). Gene hired on uncrewed. `go: yes` survived rec=no vs FlyingHigh. Lars overfit lid/chute `if`s (T-376). Unique-per-hop stems still mint. T-379 denies `hop_factory`. Two briefings drifted. Pad occupancy beat the remembered CLI.

## 5 Cross-desk learn/request

Gene→Hank: after `attach-run`, rec=no or sit≠`waste.bind` → hire Gene `go: wait` (`head.json:3220` vs `:3429`; CHARTER.md:163–167). Lars→Wernher: finish T-379 (`hop.py:892`); retract “No hop_factory” (`:13482`); tests lock blocks. Gus→Lars: 50 km is tanks, not silk. Linus→Gene: bind T-069 only after a real ≥50 km loft. Wernher→Lars: sit clock vs stamp helper; t7-only compose is legal. All→door: a request must survive the next packet (`them=none` last-row kills it).

## 6 Why the current door fails

(1) Empty `good`/`self` raises (`tickets.py:595–599`); CLI all three `required=True` (`:1605–1607`); `--them` stores `"none"` (`:597`). (2) who mortimer/wernher only; T-052/T-128 `"feedback"` is an ops **tag** (`head.json:2078`, `:5222`). (3) `inbox_for` last-row only (`tickets.py:1273–1278`; `test_tickets.py:351`). (4) PROTOCOL forbids Return `good:`/`self:`/`them:` (`:80–82`, `:354–356`) then requires the CLI (`:85–86`, `:359–360`, `:460–471`); job cards copy (`.grok/agents/gene.md:137–139`, `lars.md:125–126`). (5) Skeptics fail-closed on `{real, evidence}` (`.grok/workflows/learn-rsi.rhai:546–569`); create-workflow `SKILL.md` is **MISSING**. Praise+confession+other; rename to praise/me/you keeps the card.

## 7 Skeptic analogue

`learn-rsi.rhai` Verify: `real=true` only against a named overscope/gap; else `real=false` with path evidence (`:546–569`). create-workflow SKILL analogue **MISSING**. Map: a finding is a **claim**. Another desk/Hank may confirm/refute by appending `--real` + evidence they read. Unverified stays visible and is **not** a vote. Kernel refuses `--real` with empty evidence; does not inspect.

## 8 The plan (record, CLI, mandatory-but-free, sharing)

Durable words: **finding**, **claim**, **evidence**, **owner**, **real**. Not praise/me/you. Not keep/change/ask as required slots. **Store:** `payload.findings[]` `{who, claim, evidence, owner, real, at}`. `claim` required one line (free: pitfall/question/request/own-workflow/confirm/refute/code). `evidence` optional `path:line` (empty ⇒ unverified). `owner` optional desk/`none`. `real` default false; `--real` only if evidence nonempty. `at` kernel. **CLI:** `python main.py tickets feedback T-NNN --claim "…" [--evidence "path:line"] [--owner desk|none] [--who desk] [--real]`. Drop `--good --self --them`. Request-only (`--claim` + `--owner lars`) legal. Own-workflow-only (`--claim`, no owner) legal. No praise field. **Mandatory-but-free:** ≥1 finding per hire; content free. **Harvest writes** (Skeptic 1): close copies `close_why` if findings empty; refuse only if **both** empty. `attach-run` copies `learn` once if empty (`who=hank`, `evidence=telem_run`); later hops overwrite `learn:` (T-323) but do not append more Hank findings. Packet prints **all** findings (cap ~8) **and a copy-line** of this CLI. **Migration:** legacy `{who,good,self,them,at}` reads as `claim=self` (fallback `good`), `owner=them_desk(them)`, `evidence=""`, `real=false`. Keep four live rows. **Sharing:** `inbox --feedback` = **all** `owner=you` plus owned zero-finding tickets (kill last-row). Confirm/refute = another finding; `--real` from a **different** `who` with evidence. Same-`who` `--real` display-only. Stumble-during-work stays `ops --tag feedback --fingerprint`. Cheap copies: Lars `tickets feedback T-379 --claim "leftover_wreck_before_light still hop.py:892; retract No hop_factory" --evidence "hop.py:892 hop_factory.py:159" --owner wernher`; Gene `T-081 --claim "go=yes survived rec=no vs FlyingHigh bind" --evidence "head.json:3220,3429,3436" --owner hank`; Gus `T-366 --claim "50 km is t7 tanks" --evidence "docs/crew/log/gus.md:3"`; Linus `T-069 --claim "High unpaid until loft ≥50 km" --evidence "head.json:3429" --owner gene`; Wernher confirm `T-379 --claim "confirm leftover_wreck still hop.py:892" --evidence "hop.py:892" --who wernher --real`. Hank types nothing if harvest copied `learn`. Pad still flies.

## 9 Skeptics on this plan

**Skeptic 0 `real=false`.** Not a three-slot card: only `--claim` required; praise gone; request-only and own-workflow-only legal. Do **not** keep `--good --self --them` or rename to praise/me/you. **Skeptic 1 `real=true`.** Flying desks skip a remembered CLI; DESIGN harvest was nag; T-081 never closes; Lars already `close_why` + `payload: {}` (`head.json:11990`, `:13315`). 15 min novel: **no**. Last-row clobber if inbox lists all `owner=you`: **no**. **Qualify:** harvest must **write** (`close_why` / one `learn`); packet must print the copy-line; cheap examples in §8. Without those writes the door stays unused. Inbox-all-owner stays. **Skeptic 2 CLIPPED** — uninspectable; not `real`. Bus-stay: still `tickets feedback` on the work T-id; `TYPES` 11; no `parse_return` finding key; no child ticket per hire.

## 10 Later patches (do not apply)

`tickets.py` (Wernher): drop trio; append findings; union-read legacy; packet all+copy-line; inbox any-owner; close harvest `close_why`; `attach-run` harvest `learn` once; refuse `--real` w/o evidence; refuse empty claim. `tests/test_tickets.py` (Wernher): lock those. PROTOCOL/BRIEF/GLOSSARY/OPS/world-model (Mortimer): drop “three one-liners”; finding CLI; keep forbid Return `good:`. `.grok/agents/*.md` (Mortimer): one cheap `--claim` after the fence. CHARTER **door sentence only** (Mortimer): quote finding CLI; keep “sharper sit / pitfall / question / code”. `protocol.py` SCHEMAS: **no** finding key. Later tickets (do not open now): `type=systems --fingerprint feedback-return` (Wernher); `type=org` same stem (Mortimer). After door: one finding on T-081 `go: yes` vs rec=no — not a child.

## 11 Do not touch

`hop.py` / `hop_factory.py` / `physics_warp.py` / `pad.py` / `splash.py`. CHARTER **creed**. Return keys / `from-feedback` / `parse_return` `good`. New TYPE. Child ticket per hire. 15 min Gene novels. `needs_learn` / Batch Learn. GameData / `persistent.sfs`. Pad occupancy (harvest, do not nag). `protocol fly` occupancy. T-379 leftover_wreck extract. Practice last-write waits for rsi/org apply.
