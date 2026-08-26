# Building blocks — Gene may only name `pad` `hop` `splash` `tech-unlock`

Owned by **Lars Grokman, Vehicle Systems Engineer**. If Gene needs a
name that is not here, parent spawns Lars first. No heredocs. Missing
name means Lars writes it.

| Phase | CLI | Expect |
|---|---|---|
| pad | `python main.py pad` / `phase pad` | Hangar seated/VAB craft file uncrewed. Dry-launch only if current stage is 0. Physics warp 2–4× on pad/landed; **rails 0**; never WarpTo; 1× after dwell. |
| hop | `python main.py hop` / `phase hop` | Hangar seated hop craft uncrewed. Light the bound flying card. Coast physics 2–4× after burnout (`physics_warp`); **rails 0**; never WarpTo. Uplink `phys-warp` / `no_warp`. |
| splash | `python main.py splash` / `phase splash` | Leftover hop only — no Hangar, no light. Wait splashed. Recover HD. |
| tech-unlock | `python main.py tech-unlock [node]` / `phase tech-unlock` | Ground kRPC try. 0.6 has no UnlockTech RPC — aborts. Paid node is Mortimer. |

Commander `uplink.md` verbs: `hold|cut|no_warp|phys-warp|warp|stage|recover|science|abort_pad`.
