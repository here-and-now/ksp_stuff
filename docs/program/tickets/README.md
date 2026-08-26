# Ticket bus

Source of truth for Hank. Schema and dispatch: [`../OPS.md`](../OPS.md).
Spawn how-to: [`BRIEF.md`](BRIEF.md). Sit object is the fly ticket +
`desk.md`. Seated `plan.md` is a Gene **render** (`hop_apo` /
`expect_*` stay there). `python main.py protocol fly` reads the fly
ticket (`go` / `cli` / `campaign`). Missing ticket = wait.

Eleven types: `fly` `science` `vehicle` `control` `systems` `org`
`rsi` `ctt` `recover` `press` `ops`. Ask / itch / friction:
`--type ops --tag ask|feedback|explore`. Inner-circle plan:
`--type ops --tag plan` (Lars + Gus + Linus on that ticket;
`docs/program/agree.md`). Katherine: `--tag dynamics` or
`ops --tag ask --desk katherine`. Eleanor: `--tag constellation` or
`ops --tag ask --desk eleanor`. Paid node: `--type ctt`.
Press: `--type press`. Desks `tickets open --type …`. Do not emit
`need_*` / `card:` / `recommended:` / `ask:` / `feedback:` / `good:` as
return keys. After the hire: `tickets feedback T-NNN --claim "…"`.

```
python main.py tickets list
python main.py tickets list --category bug --tag hard-splash
python main.py tickets inbox --desk lars
python main.py tickets open --type control --category bug --tag hard-splash \
  --title "…" --severity S2 --priority P1 --desk lars
python main.py tickets open --type ops --tag ask --title "…" --desk gene
python main.py tickets packet T-008
python main.py tickets packet T-008 --deep
python main.py tickets attach-run T-013 --path docs/missions/<id>/logs/<run>.jsonl
python main.py tickets landing T-013
python main.py telem docs/missions/<id>/logs/<run>.jsonl
python main.py telem docs/missions/<id>/logs/<run>.jsonl --window impact
python main.py ops next
python main.py protocol fly
```

Skim packet: desk + this ticket + BRIEF + landing envelope (pad/last
heading, apo, hz). No BOARD.md. No jsonl. No `lessons.md`. No
`science.md` / `vab.md` / `blocks.md`. Jsonl stays on disk — query
`telem` / `tickets landing`. `--deep` is PNG / craft / last-flight /
tape CLI, not rows. First command is `tickets packet <Hank-named id>`
(live T- stay; new S-/M-/C-). **Reasoning:** inherit current TUI
reasoning. Hank does **not** copy `reasoning=` into spawn packets.
Never xhigh. Warp law is Wernher. Kernel still printing `reasoning=`
on `ops next` / packet is Wernher.

Categories replace cards: `craft`, `science_opportunity`, `bug`,
`improvement`, plus `flight` / `recover` / `org`. Tags are free.
`ops --tag ask|feedback|explore|plan`. `--tag plan` is inner circle
on `agree.md`. Commander `cli` is fly `payload.cli`.
