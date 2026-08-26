# Wernher Grokman — log

- 2026-08-26 — T-541 DESKS eleanor; format_next/format_packet no reasoning= so Hank inherits TUI. T-539 craft liquid --texture RedstoneStripes, 1500 L legal, girders -n 0 strip. T-501 leftover Debris/GUID wait already on disk. No Hangar. Never leftover-ksc. Never revert.

- 2026-08-26 — T-511 engine-dead vs shear: telem flags + Tape envelope + last-flight classify_abort. 16-05-34Z throttle 1 thrust 0 fuel 2038 parts=30 is engine-dead; parts 30→9 is the funeral. Compact windows carry thrust. No hop.py. Never leftover-ksc. Never revert.

- 2026-08-26 — T-501 leftover_ship walks recoverable ground Debris (pad Goo); wait recover by `_object_id` on vessels, not leftover_pad_ships names. kRPC Recover() is async OnVesselRecoveryRequested + persist; flying rec=0 blobs make it a no-op. No Hangar. Never leftover-ksc. Never revert.

- 2026-08-26 — T-500 HS splice uses collider half max(length/2+0.179, catalog MODEL ±0.5), not node math. insert_inline bumps new_half=0.1. --payload SAS-first tank FED; tank-engine still refused. Hangar 15-14-43Z was 0.191/0.4125. Did not write GameData. No Hangar. Never leftover-ksc. Never revert.

- 2026-08-26 — T-495 `craft fuel` dumps attach tree + fuelCrossFeed path from .craft+cfg (C-477 last tank→HS→Valiant BLOCKED Ablator only). T-497 insert_heatshield refuses fuelCrossFeed=False splice; tank stays on engine. Did not write GameData. No Hangar. Never leftover-ksc. Never revert.

- 2026-08-26 — T-479 Harmony skip-dup Kerbalism VesselData flightID (`kspstuff_kerbalism/`; Os copy, no GameData write). T-483 engine first fire istg=0 sqor=0; T-480 catalog Valiant 0.45; T-482 disc bottomDiameter=0. T-484 drop recommended/lesson/ask. T-491 ship.md thrust/stage/plume. T-493 skip-save Tracking is not Close. T-487 MOVE 442 jebediah/logs. Never leftover-ksc. Never revert.

- 2026-08-26 — org-rsi verify: 136 tests OK; leftover writers stay dead. Opened T-484 feedback-return, T-487 thin-tape, T-491 telem-eyes-library, T-493 leftover-prelaunch-ghost (T-486/T-489 lars, not T-471). No Hangar. No hop. Never revert.

- 2026-08-26 — org-rsi slice 2: drop PRINT / note-tech / program shims; tape jsonl prefers telem_run else existing missions/*/logs; render_plan envelope-only; ship.md live_tape; uncrewed capcom default Walt. No Hangar. No hop. Never revert.

- 2026-08-26 — T-475 loft-only short dud unlatch: High+Low bind + 655 m landed rec=yes sci_run=0 is not sci-unchanged-recovered wait. High cannot pay 655 m and that does not idle the loft or turn High into a Surface card. Forest leftover still waits. No hop_factory. Never revert.

- 2026-08-26 — T-472 pad abort unlatch: sit=pre_launch rec=yes sci_run=0 is control miss, not sci-unchanged-recovered. High cannot pay pad and that does not idle the loft. Wreck rec=no still re-flies. No hop_factory. Never revert.

- 2026-08-26 — T-468 harvest ×19: latch still-true (T-346). Pad abort pre_launch rec=yes sci_run=0 cannot pay PresMat trio; protocol fly wait. Wreck rec=no re-flies. No hop_factory. Never revert.

- 2026-08-26 — org-rsi slice 4: git mv novels to `docs/archive/2026-08-26-org-rsi/`; world-model chair stub; blocks Gene CLI; NUKE sit-card/BOARD; classify archive-first. No Hangar. No hop. Never revert.

- 2026-08-26 — org-rsi slice 5: tape id `uncrewed` (`current.md` flight: uncrewed, pilot: none; capcom stays). Dossier from live t7-wheel / T-081 / T-404 dumps. Historical `jebediah/logs` stay. No Hangar. No hop. Never revert.

- 2026-08-26 — org-rsi slice 2: packet skim desk+BRIEF; fly_gate tickets-only; hangar T-400 capable; kill board writer / lesson mint / sync_shim / note-tech CLI; attach-run who=hank; recover desk=hank. No Hangar. No hop. Never revert.

- 2026-08-26 — org-rsi slice 1: unpin lessons/blocks/note-tech tests; `fly_gate` go is tickets-only (missing ticket waits). No Hangar. No hop. Never revert.

- 2026-08-25 — T-467 id-prefix: `_next_id` prefix-by-type (science S-, fly M-, vehicle C-, else T-). Global N. History keeps T-. landing parse S/M/C. TYPES unchanged. No hop_factory. Never revert.

- 2026-08-25 — T-449 tape helpers closed (sit_mismatch, landing synth, sci rem vs bank, thick-air skip, kind=recover). T-458 harvest ×15: latch already T-346; no hop_factory. No Hangar. No hop. Never revert.

- 2026-08-25 — T-453 thin-tape: jsonl hz is 1/wall-dt, not requested 5–20. T-454 kspstuff-read GET Session (stream.remove; no Control/scene/jsonl/ship.md); kind=recover sit/rec at recover(). status/leftover_ships while lock live are readers. No Hangar. No hop. Never revert.

- 2026-08-25 — T-450 hop-coast-phys-warp: `thick_air_cross_sit` 1× when 4× this pulse would skip the 18 km lid (09-01Z 55 km q=937 → 6 km q=17510). Quiet 200 km still 4×. No hop_factory. Never revert.

- 2026-08-25 — T-449 telem-eyes-library: Tape last snap sit/alt/q/rec vs recover sit; landing synth; sci rem vs bank +0; 4× thick-air skip. last-flight 40 lines is not the vessel. No Hangar. No hop. Never revert.

- 2026-08-25 — T-445 ra-rate: hop/splash take science+transmit. Kerbalism Experiment TX events, not stock dump/reset/transmit(). Toggle is start/stop. Cape 64 bps. No science.py (T-440). No hop_factory. This pid will not reload. Never revert.

- 2026-08-25 — T-442 hop-coast-phys-warp: `chute_arm_sit` is lofted descent in thick air ≤18 km, not 200 km vacuum. Quiet descent honors uplink. 1× thick air / high q / silk / burn. No hop_factory. Never revert.

- 2026-08-25 — T-427 prove passed: Cape RateToHome 64 is table and path. T-426 want_coast 1× in thick air ≤18 km; unknown q fail-closed. No Hangar. No hop. Never revert.

- 2026-08-25 — T-413..T-420 VAB helpers on `python main.py craft` (clone, tanks FL-T100↔proc Default Kero/LOx, chute Nylon 5/35 or cone 50m, copy-chute, girders Heaviest/rigid, wheel+PresMat, HS disc/adapter). Roundtrip keeps RESOURCE/autostrut/sqor. T-421 latch already living rec=yes+sci_run=0. No Hangar. No hop_factory. Never revert.

- 2026-08-25 — T-399 next CTT from owned tree (`generalRocketry` 20). T-396 Close persist→Tracking→KSC done; rewind is Hangar veto, not leftover-air. T-388/T-389 leftover GUID/crash-UI/wait-land stands. T-346 waste latch living +0 only. No hop.py. Never revert.

- 2026-08-24 — T-396 leftover-ksc: Flight→KSC `save("persistent")` then `game_scene`. Setter loads last SaveGame unless RAM was written first. Save fail stays Flight. Rewind is Close failure, not Hangar. Air leftover is not a veto. Never load_space_center. Never leftover-ksc. Never revert.

- 2026-08-24 — T-388 leftover-prelaunch-ghost: kRPC Vessel has no .id; persist _object_id to unrecoverable.last immediately. leftover_ships reads disk so the next process skips rec=0 crash-UI. No hop.py. Never revert.

- 2026-08-24 — T-388 leftover-prelaunch-ghost: crash-UI rec=0 MET frozen is not pad occupancy. remember vessel.id; leftover_ships skip that GUID after Close lists SUB_ORBITAL. Os will not click Recover. No hop.py. Never revert.

- 2026-08-24 — T-388 leftover-prelaunch-ghost: living SUB_ORBITAL leftover (go_flight parts=20) wait land on MET then recover(). Close while flying does not drop it. Dead GUID still not leftover. No hop.py. Never revert.

- 2026-08-24 — T-388 leftover-prelaunch-ghost: walk_home enters Flight first (rec at KSC is a lie). recover() wait gone before Close; Close during recover left SUB_ORBITAL tracking ghost. Dead GUID not leftover. Desk hangar from leftover_ships (stale sfs SUB_ORBITAL is not leftover). No hop.py. Never revert.

- 2026-08-24 — T-346 unbrick: waste_blocks_refly is living recover (rec=yes + sci_run=0) only. Wreck rec=no re-flies last cli. FlyingHigh apo ≥50 km still on living +0. No hop.py. Never revert.

- 2026-08-24 — T-346 sci-unchanged-recovered: protocol fly waits living recover sci_run=0 until bind sit/biome/apo can pay (FlyingHigh ≥50 km) or hang/bind changed. Wreck rec=no is not this latch (unbrick). fp bump stays living +0. No hop.py. Never revert.

- 2026-08-24 — Findings door: `tickets feedback --claim`; payload.findings; close harvests close_why; attach-run harvests learn once; inbox any owner. Legacy trio still reads. Never revert.
- 2026-08-24 — T-378/T-379: `tickets feedback` appends payload.feedback; close refuses empty; packet last row; inbox --feedback. Leftover abort/chute/want_coast live in physics_warp; hop.py wrappers. No hop_factory. Never revert.

- 2026-08-24 — T-372 flyinghigh-lid: `want_coast` 1× on `chute_arm_sit` / deploy / silk (15-10-47Z 4× silk sheared 28→18). Climbing armed still 4×. Ask Lars to `apply_sit_warp` before Arm. No hop_factory. Never revert.

- 2026-08-24 — T-341 sci-unchanged-recovered: protocol fly waits living recover sci_run=0 until bound sit/biome matches envelope or hang/bind changed. attach_run latches payload.waste. needs_learn uncrewed false. No hop_factory. Never revert.

- 2026-08-24 — T-339 chute-deploy-sit: `chute_arm_sit` lofted vz<0 (not only 2 km); deploy still ≤2 km or semi; 1× high q. 11-11-37Z lithobrake 2.9 km stowed. Ask Lars to Arm on arm sit. No hop_factory. Never revert.

- 2026-08-24 — T-334 control-blocks: sit-named warp/coast/chute/timeout in physics_warp (`apply_sit_warp`, `airborne_cannot_pay`, `chute_deploy_sit`, `timeout_hit`, `leftover_call`). 4× only lofted burnout AND q≤5 kPa. Ask Lars to drop `_after_skip`. No hop_factory. Never revert.

- 2026-08-24 — T-325: Snapshot link/snr/via; ship.md + tape where:; comms dump is TL/LIVE/SILENT tables from ConfigCache. No hop.py. No GameData.

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
