# Wernher Grokman — log

- 2026-08-24 — T-323: attach_run stamps payload.learn from envelope (T-081 22-33-35Z); refuse empty fp on control/systems/feedback; alias prefix; sci-unchanged-recovered bump on +0 rec. review uncrewed drops Gene nag. No hop.py.

- 2026-08-23 — T-305: 16-47-21Z envelope burn was cutoff 15/16 (throttle=0). Powered hold 297/65 hz 20. Burn window stops at last throttle>0.05; min-pitch among those. 09-28 209/3 still throttled. No hop.py.

- 2026-08-23 — T-284: 16-47-21Z 26 samples / 380 s (hz 0.07). Fast path no parts.all; expensive sci/broken stay off; grim ticks skip after slow grab; Tape silk recover sit=landed rec=yes. No hop.py.

- 2026-08-23 — T-166: ship.md + landing envelope lat/lon/downrange km/biome. Stream Flight.latitude/longitude; haversine from Cape. jsonl already had biome. No hop.py.

- 2026-08-23 — T-159: 09-28-59Z envelope hid burnout 209/3 (apex was peak alt 297/86). burn: window + skip slow walks after expensive Telem.read; 20 Hz while throttled. No hop.py.

- 2026-08-23 — T-149: 08-04-05Z desk sci was stale sfs after recover (+4.2 RAM, +0.0001 desk). last-flight/jsonl sci_bank; desk prefers kRPC then last-flight; envelope bank=. No hop.py. No leftover-ksc.

- 2026-08-23 — T-147: 07-21-05Z thin tape. Apex is peak alt not max apo; descent window + skim line. Telem.read skip .fields after field_list, cache sci/broken/debris 1 s, bind by Vessel.id, 20 Hz below 8 km. No hop.py.

- 2026-08-20 — Desk briefing `docs/program/krpc.md` from disk (plugin 0.6
  CHANGELOG + xml/json, settings.cfg, Kerbalism MM cache, wrappers). No
  Session. `autoStartServers=False` on disk. No trap this pass.
- 2026-08-20 — letsgrok. No trap this campaign. Standing by.
- 2026-08-21 — T-002 Hangar refuse exact basename (not geiger-pbc substring). T-003 desk leftover is disk ships; FLYING Debris is not a hangar job. hangar.py, desk.py, world.py. No Session (lock live).
- 2026-08-22 — T-029 leftover/KSC is Hank: hop unmatched/wreck leftover aborts `ksc leftover` with recover-probe CLI (no recover-then-Hangar). ops next hires hank. protocol fly waits leftover n>0. hop.py, ops.py, protocol.py, desk.py.
- 2026-08-22 — T-083 OKTO Module.fields duplicate gui Reaction Wheels: telem._module_flag uses field_list; first telem.read no longer aborts. PRELAUNCH leftover stays. Do not Hangar. Do not recover.
- 2026-08-23 — T-088/T-087: ksc_ready false whenever can_revert (n=0 overlay is Revert). go_ksc leftover-ksc save/load. T-053 leftover_sit overlay.last. T-051 format_landing horiz+pitch; hop-exit attach-run. Do not fly. Do not Hangar.
- 2026-08-23 — T-102 tape.Tape envelope/windows; tickets landing + packet skim are eyes; jsonl stays disk (telem CLI). No hop retune. Do not fly.
- 2026-08-23 — T-104 python main.py ship: heading/wreck/ec/alt/as_of from ship.md. Disk only. No Session. No jsonl.
- 2026-08-23 — T-107–T-110: state rows recoverable/chute/sci rem-run/g_force/mass; tape skim q/EC/g/stage/broken; landing+recoverable kinds (close synthesizes if still flying). No hop retune.
- 2026-08-23 — T-116 hung-preflight-ksc: launch_vessel NRE after pre-flight PASS poisons Session; Hangar raises, no retry on that conn. ship.md hangar sit + stale vs lock. No hop.py. Do not fly.
- 2026-08-23 — T-137: 25 s abort-to-KSC yanked a live Flight load (Parallax/Kopernicus). Side-client launch_vessel; abort only at KSC; Session.close 5 s cap. No hop.py. Do not fly.
- 2026-08-23 — T-139: broken≠shear. parts_n/root/debris_n + mass drop event; tape stack line + ship.md mass. No hop.py (Lars T-140).
- 2026-08-23 — T-142: leftover-ksc RIP. walk_home recover()+Close reload_save=False. kRPC UI cannot click Flight Results. Never revert. Never recover Ast. XRL-564.
- 2026-08-23 — T-128: fly payload.science_ids unions bound tickets (cannot hide T-071 TELEMETRY / T-112 goo). card_science_ids; protocol/desk/hop science card. No hop gates.
- 2026-08-23 — T-145: overlay_painted false on Space Center + leftover ships n=0; leftover can_revert is not Flight Results (07-50 KSC overview). Never revert. Never leftover-ksc.
