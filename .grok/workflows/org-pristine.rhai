let meta = #{
    name: "org-pristine",
    description: "Status-quo of stale docs and desk comms after the last RSI, then a ticket-bus plan to a pristine org. Plan only.",
    when_to_use: "When the house is drowning in markdown, last RSI applied code but left the pile, or Os wants a report-then-plan to rip stale docs without ticket-everything",
    phases: [
        #{ title: "Census", detail: "live tree, injection, writers, inventory vs disk" },
        #{ title: "Harvest", detail: "last RSI and prior jumps: what stuck, what did not" },
        #{ title: "Comms", detail: "per-desk who talks to whom since last RSI" },
        #{ title: "Classify", detail: "KEEP / TAPE / ARCHIVE / NUKE / TICKET every live md" },
        #{ title: "Friction", detail: "poison reads, dual stores, Lars compose, Hank glue" },
        #{ title: "Interview", detail: "desks on md vs tickets, card rot, hire length" },
        #{ title: "Design", detail: "MOVE / KEEP / NUKE / REROUTE plus comms law" },
        #{ title: "Skeptics", detail: "over-nuke, under-nuke, still-md-bus, Lars gap, Hank novel" },
        #{ title: "Tighten", detail: "fold skeptics into the plan" },
        #{ title: "Report", detail: "status quo then the pristine plan" },
    ],
};

fn text_of(r) {
    if r == () { return ""; }
    if r.success != true { return ""; }
    let o = r.output;
    if o == () { return ""; }
    if type_of(o) == "string" { return o; }
    json_encode(o)
}

fn clip(s, n) {
    if type_of(s) != "string" { return ""; }
    if s.len() <= n { return s; }
    let t = s.sub_string(0, n);
    t += "\n…[clipped]\n";
    t
}

fn walls() {
    let p = "";
    p += "Repo /home/os/gits/ksp_stuff. ";
    p += "NO kRPC. NO python main.py phase/pad/hop/ksc/recover-probe/load/Hangar. ";
    p += "NO GameData. NO persistent.sfs. NO CHARTER creed rewrite. ";
    p += "NO hop.py / hop_factory.py / hop_factory_pad.py / physics_warp.py / pad.py / splash.py retune. ";
    p += "NO tickets.py kernel patch. NO job-card rewrite. NO tests edit. PLAN ONLY. ";
    p += "Do not write any file under docs/ or .grok/agents/. Scratch is the host's job. ";
    p += "Do not answer from memory. Use read_file, list_dir, grep. Missing path = MISSING. ";
    p += "Empty is valid only after you searched. Token cap: MAX 55 lines. Cite path:line. ";
    p += "No jsonl dump. Crew logs: grep counts + last 40 lines, not the whole file. ";
    p += "docs/archive/ is parked context, not live dispatch — say PARKED when you open it. ";
    p += "Last RSI on disk: lars-rsi 2026-08-25 (docs/program/lars-rsi.md, git ea7f60b). ";
    p += "Prior applied jumps: rsi-jump, ticket-bus-cutover, learn-rsi. feedback-plan is plan-only. ";
    p += "Os 2026-08-26: clusterfuck of documents; agents do not know where to write; ";
    p += "rip stale; ticket bus is the comms; MD only when a ticket cannot hold it; ";
    p += "lessons.md does not scale and must not be injected every hire; ";
    p += "uncrewed tape still lands in docs/missions/jebediah/; spotter card still on disk; ";
    p += "Lars still not composing one living rocket from a Wernher catalog.\n";
    p
}

fn census_prompt(title, focus, paths) {
    let p = walls();
    p += "You are a read-only historian of the CURRENT house. Topic: ";
    p += title;
    p += "\nAS-IS only. Do not recommend. Do not edit.\nFocus: ";
    p += focus;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nHeadings only:\n";
    p += "## Topic\n## Counts (path:line or wc)\n## Who writes it\n## Who is told to read it\n";
    p += "## Injected every hire? (job card / AGENTS.md / packet / PROTOCOL)\n";
    p += "## Stale vs live (dated last write)\n## Files read\n";
    p
}

fn harvest_prompt(title, focus, paths) {
    let p = walls();
    p += "You are a read-only RSI historian. Prior jump: ";
    p += title;
    p += "\nDo not praise vapor. On disk only: what the jump claimed vs what is still true.\nFocus: ";
    p += focus;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nHeadings only:\n";
    p += "## Jump\n## Claimed (quote the report)\n## Still true (path:line)\n";
    p += "## Leftover (still poisoning hires)\n## What the jump did NOT touch that Os named today\n## Files read\n";
    p
}

fn comms_prompt(title, focus, paths, since) {
    let p = walls();
    p += "You are a read-only comms historian. Desk: ";
    p += title;
    p += "\nWindow: ";
    p += since;
    p += " through today (2026-08-26). Earlier dates only as contrast.\nFocus: ";
    p += focus;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nHeadings only:\n";
    p += "## Desk\n## Who they respond to (PROTOCOL vs actual log)\n";
    p += "## How Hank sits in between (ops next / packet / leftover / tape)\n";
    p += "## Writes since ";
    p += since;
    p += " (md vs tickets stamp vs tickets feedback)\n";
    p += "## Card format (Return fence vs leftover keys vs first command)\n";
    p += "## Too long? (job-card lines, hire re-reads, pytest house)\n";
    p += "## In the loop? (S/M/C prefixes, named helper, findings, pad occupancy)\n";
    p += "## Files read\n";
    p
}

fn classify_prompt(title, paths, rule) {
    let p = walls();
    p += "You classify live files. Shard: ";
    p += title;
    p += "\nlist_dir the shard, then read headers. Do not dump bodies.\n";
    p += "For EACH md/json that is not under docs/archive/, pick exactly one class:\n";
    p += "KEEP-MD = constitution/voice/sit snapshot the next hire must read as prose.\n";
    p += "TAPE = evidence (jsonl, review envelope, screenshots). Keep on disk, do not inject.\n";
    p += "ARCHIVE = already parked or must move under docs/archive/ and drop from spawn-read.\n";
    p += "NUKE-LIVE = still in the live tree, poisons hires, should vanish or park THIS sit.\n";
    p += "TICKET = content that already is or should be a ticket field/finding, not a board.\n";
    p += "UNKNOWN = you could not tell after search.\n";
    p += "Rule of thumb: ";
    p += rule;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nAlso read docs_inventory.py classes vs this shard — if inventory says leftover_migrated but the file is still live, say so.\n";
    p += "Headings: ## Shard ## Table (path | class | lines | last writer | injected? | evidence) ## Inventory mismatch ## Files read\n";
    p += "Cap the table at 40 rows; if more, group by directory and log the drop.\n";
    p
}

fn friction_prompt(title, focus, digest) {
    let p = walls();
    p += "You are a read-only org analyst. Topic: ";
    p += title;
    p += "\nPrior digest (untrusted, re-verify counts on disk):\n";
    p += digest;
    p += "\nFocus: ";
    p += focus;
    p += "\nHeadings: ## Topic ## Evidence (path:line) ## Why it happens ## Damage to the NEXT hire ## Files read\n";
    p
}

fn interview_prompt(name, title, ticket, sim) {
    let p = walls();
    p += "THIS HIRE IS AN INTERVIEW. Do not stamp. Do not edit. Do not fly. Do not open tickets. ";
    p += "You are ";
    p += name;
    p += ", ";
    p += title;
    p += ".\nSimulated packet:\n";
    p += "to: ";
    p += name;
    p += "\nfrom: Mortimer Grokman, CEO\nlock: free\n";
    p += "task: interview only — what markdown still poisons this desk, who you actually talk to, how Hank sits in between\n";
    p += "read: docs/program/desk.md ; docs/program/tickets/BRIEF.md ; docs/program/slate.md\n";
    p += "ticket: ";
    p += ticket;
    p += "\nSituation (verify on disk, do not invent): ";
    p += sim;
    p += "\nRead your job card .grok/agents/ matching your slug, your crew log last 40 lines, BRIEF.md, PROTOCOL.md handoff table, CHARTER RSI paragraph. ";
    p += "Then answer headings only:\n";
    p += "## First command if this were a real hire\n";
    p += "## Who I actually respond to (name+title)\n";
    p += "## What Hank does in between that I wait on or re-do\n";
    p += "## Markdown I still write that should be a ticket/stamp/finding\n";
    p += "## Markdown I am still told to READ that is stale or wrong\n";
    p += "## Card rot (Return keys, first command, prefixes, named file)\n";
    p += "## Why my last hire was slow (or was not)\n";
    p += "## One cheap cut so the next hire is minutes, ticket-native, no lessons novel\n";
    p
}

let since = "2026-08-25";
if args != () {
    if args.since != () {
        since = args.since;
    }
    if args.apply == true {
        pause("verification", "org-pristine is plan-only. Do not pass apply. Resume with args.since only.");
    }
}

phase("Census");
let cjobs = [];
cjobs.push(#{
    label: "census-program-md",
    capability_mode: "read-only",
    prompt: census_prompt(
        "docs/program live markdown (not tickets/ json)",
        "list_dir docs/program. wc -l every *.md. Flag dual plan.md, science.md dump, note-tech.md, loop.md, briefing.md, sit-card.json, lars-rsi.md, learn-rsi.md, feedback-plan.md, org-flow/, world-model.md, OPS.md, PROTOCOL.md, GLOSSARY.md, krpc.md, blocks.md, slate.md, roster.md, mods.md, RO.md, ra-rate.md, tech.md, vab.md. Which of these a cold hire is told to open.",
        "- docs/program/ (list_dir)\n- docs/program/OPS.md first 80\n- docs/program/PROTOCOL.md Files + Return\n- docs/program/world-model.md first 40 and last 40\n- docs/program/note-tech.md first 20\n- docs/program/loop.md\n- docs/program/plan.md first 20\n- docs/program/science.md first 20\n- docs/program/lars-rsi.md first 20\n- docs/program/learn-rsi.md first 20\n- docs/program/feedback-plan.md first 20"
    ),
});
cjobs.push(#{
    label: "census-missions",
    capability_mode: "read-only",
    prompt: census_prompt(
        "docs/missions — Jebediah folder as the only mission",
        "current.md flight: jebediah. INDEX one row. Uncrewed hops still write docs/missions/jebediah/logs (442 files). loop.md still acks Hank abort today. plan.md / science.md / craft.md / briefing.md dual with docs/program. Os: Jeb has not flown as Commander for days; logs still land in his folder. COUNT dated logs 2026-08-25 and 2026-08-26 vs last crewed Jeb log line.",
        "- docs/program/current.md\n- docs/missions/INDEX.md\n- docs/missions/jebediah/ (list_dir)\n- docs/missions/jebediah/loop.md\n- docs/missions/jebediah/plan.md\n- docs/missions/jebediah/science.md\n- docs/missions/jebediah/craft.md\n- docs/crew/log/jebediah.md last 40\n- docs/flights/index.jsonl last 20\n- docs/program/tickets/BRIEF.md attach-run path"
    ),
});
cjobs.push(#{
    label: "census-agents",
    capability_mode: "read-only",
    prompt: census_prompt(
        ".grok/agents job cards and leftover roles",
        "wc -l every card. spotter.md still DEPRECATED on disk. bill/bob/valentina/grok stubs. builder.md pointer under docs/crew. Return fences vs PROTOCOL. Who still lists BOARD.md, lessons.md, world-model, note-tech, science.md bind as Inputs. First-command S/M/C vs T- only. Walt has no card.",
        "- .grok/agents/ (list_dir + wc)\n- .grok/agents/spotter.md\n- .grok/agents/lars.md After a miss + Return\n- .grok/agents/hank.md first 80\n- .grok/agents/gene.md first 40\n- .grok/agents/wernher.md first 40\n- .grok/agents/pilot.md first 40\n- docs/crew/builder.md\n- AGENTS.md spawn table (spotter row)"
    ),
});
cjobs.push(#{
    label: "census-lessons",
    capability_mode: "read-only",
    prompt: census_prompt(
        "lessons.md + agent-notes.md injection",
        "docs/lessons.md is 2871 lines of per-run headings. Os: clusterfuck of single tickets, maybe wrong, still injected. COUNT ## headings. COUNT 2026-08-25 headings vs unique fingerprints. Who is told to APPEND (lars.md After a miss, AGENTS.md R&D contract, PROTOCOL, BRIEF, OPS). Who is told to READ the whole file (AGENTS.md parent: miss physics). Children agents_md false — do they still open it because the card says append? tests/test_protocol.py reads it. docs/archive/kerbin-lessons.md parked.",
        "- docs/lessons.md first 80 + grep ^##\n- docs/agent-notes.md first 40 (wc)\n- AGENTS.md lines that name lessons.md\n- .grok/agents/lars.md After a miss\n- docs/crew/lars.md\n- docs/program/OPS.md lessons line\n- docs/program/PROTOCOL.md lessons line\n- docs/program/tickets/BRIEF.md lessons line\n- tests/test_protocol.py lessons reads\n- docs_inventory.py LESSONS"
    ),
});
cjobs.push(#{
    label: "census-tickets-vs-md",
    capability_mode: "read-only",
    prompt: census_prompt(
        "ticket bus vs leftover markdown boards",
        "What already lives on tickets (go/cli/campaign/learn/capable/bind/findings/fingerprints). What still last-writes a board: plan.md render, science.md dump, vab.md, world-model Practice, briefing.md, BOARD.md novel, note-tech mailbox, crew logs as dispatch, loop.md radio. Packet skim contents in tickets.py packet(). Does anyone still read BOARD.md despite BRIEF.",
        "- docs/program/tickets/BRIEF.md\n- docs/program/tickets/README.md\n- docs/program/tickets/BOARD.md first 40\n- tickets.py packet() / TYPES / ID_PREFIX\n- docs/program/OPS.md Read first\n- protocol.py fly_gate (ticket vs plan fallback)\n- card.py still used?\n- docs/program/sit-card.json keys only"
    ),
});
cjobs.push(#{
    label: "census-writers",
    capability_mode: "read-only",
    prompt: census_prompt(
        "kernel that still WRITES markdown",
        "grep Path write / open( / write_text / append in review.py desk.py tickets.py hop.py hop_factory.py main.py protocol.py ops.py for docs/*.md. last-flight, ship.md, desk.md, lessons.md, crew logs, plan.md, briefing, loop.md, note-tech. attach-run path still missions/jebediah/logs. Who appends lessons (code vs job-card honor system).",
        "- review.py write_review / learn_block\n- desk.py write desk.md\n- tickets.py attach_run path\n- main.py last-flight\n- grep lessons.md in *.py .grok/agents docs/program\n- docs/program/ship.md first 15\n- docs/last-flight.md first 15 if present"
    ),
});
cjobs.push(#{
    label: "census-control-files",
    capability_mode: "read-only",
    prompt: census_prompt(
        "Lars pulse vs Wernher catalog vs immortal hop.py",
        "wc -l hop.py hop_factory.py hop_factory_pad.py physics_warp.py pad.py splash.py science.py blocks.md. Os: Lars should compose one living rocket from Wernher blocks, not grow the factory. lars-rsi extracted pad-RF. Factory inland still run_factory_vessel ~1051 lines. hop.py still ~3300. Is there a per-craft compose file? tests/test_hop.py 231 godfile vs test_hop_factory.py.",
        "- hop_factory.py header + run_factory_vessel\n- hop_factory_pad.py header\n- hop.py first 40 + grep ^def | wc\n- physics_warp.py first 30\n- docs/program/blocks.md first 40\n- .grok/agents/lars.md Where the cause lives\n- .grok/agents/wernher.md control blocks\n- tests/test_hop.py / tests/test_hop_factory.py line counts"
    ),
});
cjobs.push(#{
    label: "census-injection",
    capability_mode: "read-only",
    prompt: census_prompt(
        "what a cold child actually loads",
        "Job cards agents_md: false so children do NOT get AGENTS.md. Parent Hank DOES. Packet = desk.md + BRIEF + tickets packet. PROTOCOL spawn packet read: <=3. Who still tells desks to open lessons.md, world-model, BOARD, science.md, vab.md, note-tech, crew log, jsonl. Reasoning floors. resume_from tax.",
        "- AGENTS.md spawn packet + When to spawn first 80\n- docs/program/PROTOCOL.md Spawn packet\n- tickets.py packet skim fields\n- .grok/agents/lars.md First command + After a miss\n- .grok/agents/gene.md First command\n- .grok/agents/linus.md First command\n- .grok/agents/gus.md First command\n- docs/program/desk.md first 40"
    ),
});
cjobs.push(#{
    label: "census-inventory",
    capability_mode: "read-only",
    prompt: census_prompt(
        "docs_inventory.py vs the live tree",
        "The house already classifies docs into live_kernel / live_tape / parked_archive / leftover_migrated. FORBIDDEN_DISPATCH. _ORG_NOVEL_NAMES. Does live docs/program still contain names the inventory calls leftover (feedback-plan, lars-rsi, learn-rsi, note-tech)? Are spawn prompts still naming forbidden paths?",
        "- docs_inventory.py DOC_CLASSES FORBIDDEN_DISPATCH _ORG_NOVEL_NAMES classify functions\n- tests that import docs_inventory\n- grep FORBIDDEN_DISPATCH and leftover_migrated\n- list_dir docs/archive/2026-08-23-md-cutover/program (PARKED — names only)"
    ),
});
cjobs.push(#{
    label: "census-last-turns",
    capability_mode: "read-only",
    prompt: census_prompt(
        "git and tickets since last RSI (2026-08-25)",
        "git log --oneline since ea7f60b / 2026-08-25. Uncommitted (git status). BOARD/head last events 2026-08-25 and 2026-08-26. Crew log dated lines 08-25/26 per slug. Who wrote lessons headings those days. Who wrote missions/jebediah/logs those days. Os said last RSI was two to three turns ago — verify.",
        "- git log --oneline -30\n- git status --short\n- docs/program/tickets/board.jsonl last 30 lines\n- docs/program/tickets/head.json T-081 payload (go campaign learn cli)\n- docs/crew/log/*.md first 15 each\n- docs/lessons.md first 80 headings 08-25\n- docs/program/lars-rsi.md section 9 Open risks"
    ),
});

let compiles = parallel(cjobs);
let compile_blob = "";
let ci = 0;
for r in compiles {
    compile_blob += "\n\n===== CENSUS ";
    compile_blob += ci.to_string();
    compile_blob += " =====\n";
    compile_blob += text_of(r);
    ci += 1;
}
log("census slots=" + ci.to_string());
let compile_digest = clip(compile_blob, 8000);
let _cscratch = write_scratch_file("census.md", compile_blob);

phase("Harvest");
let hjobs = [];
hjobs.push(#{
    label: "harvest-lars-rsi",
    capability_mode: "read-only",
    prompt: harvest_prompt(
        "lars-rsi (applied 2026-08-25)",
        "Prefixes S/M/C, hop_factory_pad extract, Lars card one pad-RF, packet third path named helper. Open risks: T-465 inbox, test_hop.py 231, inland compose still run_factory_vessel, git commit MISSING. Os today: Lars still not on per-rocket scripts from Wernher catalog. Verify hop_factory.py still 1000+ lines. Did the jump ADD lars-rsi.md to live program/ (another novel)?",
        "- docs/program/lars-rsi.md\n- .grok/workflows/lars-rsi.rhai meta + Design caps\n- hop_factory.py wc / hop_factory_pad.py wc\n- tickets.py ID_PREFIX\n- .grok/agents/lars.md pad-RF + After a miss (still lessons.md)\n- docs/program/tickets/BRIEF.md prefixes"
    ),
});
hjobs.push(#{
    label: "harvest-learn-rsi",
    capability_mode: "read-only",
    prompt: harvest_prompt(
        "learn-rsi (applied)",
        "Uncrewed learn = attach-run overwrite. Fingerprint reuse. Feedback door. lessons.md heading names fingerprint — that KEPT lessons.md as the forensics bus. Os today: that file does not scale and is injected. Did learn-rsi make lessons worse?",
        "- docs/program/learn-rsi.md first 80\n- .grok/workflows/learn-rsi.rhai Design caps\n- tickets.py attach_run learn overwrite\n- ops.py needs_learn\n- .grok/agents/gene.md Learn\n- docs/lessons.md heading count"
    ),
});
hjobs.push(#{
    label: "harvest-ticket-bus",
    capability_mode: "read-only",
    prompt: harvest_prompt(
        "ticket-bus-cutover + rsi-jump",
        "Leftover need_* / cards moved. fly_gate prefers fly ticket. Packet skim. Wernher on systems. Gene not merge. What markdown was KEEP and is now poison (science.md dump, plan.md render, lessons forensics, dual boards). SPEED.md NEXT-ORG.md parked under archive — any live copies?",
        "- docs/program/ticket-bus-cutover.md first 40 if live else MISSING\n- docs/archive/2026-08-23-md-cutover/program/ticket-bus-cutover.md first 20 (PARKED)\n- docs/program/rsi-jump.md if live else archive\n- protocol.py fly_gate\n- ops.py needing_go systems batch\n- AGENTS.md no Gene merge\n- grep need_builder in .grok/agents"
    ),
});
hjobs.push(#{
    label: "harvest-feedback-plan",
    capability_mode: "read-only",
    prompt: harvest_prompt(
        "feedback-plan (plan-only, no apply)",
        "Dropped good/self/them. Findings on work T-id. Was it applied? CHARTER/PROTOCOL still quote what? Count payload.findings vs empty. Did flying desks file --claim since 08-25?",
        "- docs/program/feedback-plan.md first 60\n- .grok/workflows/feedback-plan.rhai meta\n- CHARTER.md RSI paragraph\n- PROTOCOL.md Feedback\n- tickets.py add_feedback / findings\n- grep payload.findings / --claim in head.json (sample, do not dump)"
    ),
});

let harvests = parallel(hjobs);
let harvest_blob = "";
let hi = 0;
for r in harvests {
    harvest_blob += "\n\n===== HARVEST ";
    harvest_blob += hi.to_string();
    harvest_blob += " =====\n";
    harvest_blob += text_of(r);
    hi += 1;
}
log("harvest slots=" + hi.to_string());
let harvest_digest = clip(harvest_blob, 5000);
let _hscratch = write_scratch_file("harvest.md", harvest_blob);

phase("Comms");
let mjobs = [];
mjobs.push(#{
    label: "comms-hank",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Hank Grokman, COO — the in-between",
        "Os: how does Hank handle the in-between. ops next hire graph, leftover recover()+Close, attach-run+landing, packet skim, ship.md watch, nag missing findings. Does he still read BOARD.md / lessons / last-flight 40 as the vessel. Parent IS Hank (AGENTS). Token tax of this TUI session vs children.",
        "- .grok/agents/hank.md\n- docs/crew/log/hank.md\n- docs/crew/hank.md\n- ops.py next_actions / fly_ready / needing_go\n- AGENTS.md Supervisor + When to spawn\n- docs/program/OPS.md split of power\n- docs/program/PROTOCOL.md Hank handoffs",
        since
    ),
});
mjobs.push(#{
    label: "comms-gene",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Gene Grokman, Launch / Flight Director",
        "Stamps go. Still last-writes plan.md / briefing.md / world-model? Learn skip uncrewed. Dual plan. Who he talks to (Linus bind, Gus capable, not Commander radio). Card first command M- vs T-081 live.",
        "- .grok/agents/gene.md\n- docs/crew/log/gene.md last 40\n- docs/program/plan.md first 20\n- docs/missions/jebediah/plan.md\n- docs/program/briefing.md first 20\n- docs/program/world-model.md who chairs",
        since
    ),
});
mjobs.push(#{
    label: "comms-lars",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Lars Grokman, Vehicle Systems Engineer",
        "Os: still not composing per-rocket from Wernher catalog; still lessons.md; still slow. After a miss appends lessons. Packet third path. Four rf-ignition hires then extract. Log since 08-25. Does he talk to Wernher via ops --tag ask or via hop_factory growth.",
        "- .grok/agents/lars.md\n- docs/crew/log/lars.md\n- docs/crew/lars.md\n- docs/lessons.md first 80\n- hop_factory.py / hop_factory_pad.py line counts\n- BOARD / fingerprints rf-ignition-ullage",
        since
    ),
});
mjobs.push(#{
    label: "comms-wernher",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Wernher Grokman, Chief Systems Engineer",
        "Catalog of blocks vs standing systems tickets. Does Lars import a catalog or copy? physics_warp.py owner. Job card vs ops next. Log since 08-25. Prefix kernel T-467.",
        "- .grok/agents/wernher.md\n- docs/crew/log/wernher.md\n- docs/program/krpc.md first 30\n- physics_warp.py first 30\n- docs/program/blocks.md first 30\n- BOARD type=systems open",
        since
    ),
});
mjobs.push(#{
    label: "comms-gus-linus",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Gus Grokman + Linus Grokman (shelf)",
        "vab.md vs vehicle tickets C-. science.md dump vs payload. Dual seated science.md. Capable vs bind. Who they talk to (each other via Hank, not Commander). Logs since 08-25.",
        "- .grok/agents/gus.md\n- .grok/agents/linus.md\n- docs/crew/log/gus.md last 40\n- docs/crew/log/linus.md last 40\n- docs/program/vab.md\n- docs/program/science.md\n- docs/missions/jebediah/science.md first 20",
        since
    ),
});
mjobs.push(#{
    label: "comms-jeb",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Jebediah Grokman, Commander — seat vs uncrewed parent-fly",
        "current.md still seats jebediah. protocol fly commander: none on uncrewed so parent flies. Logs and mission folder still his. loop.md talk. note-tech 08-21 mailbox. Last actual Commander hire vs tape in his folder 08-25/26. Val/Bill/Bob never seated.",
        "- .grok/agents/jebediah.md\n- .grok/agents/pilot.md\n- docs/crew/log/jebediah.md last 40\n- docs/missions/jebediah/loop.md\n- docs/program/note-tech.md first 20\n- docs/program/current.md\n- docs/last-flight.md if present",
        since
    ),
});
mjobs.push(#{
    label: "comms-mortimer",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Mortimer Grokman, CEO — Practice and org RSI",
        "Owns PROTOCOL/job cards/Practice. Last RSI applied via workflow then left live novels (lars-rsi.md). Log since 08-25. CHARTER vs OPS length. Does he last-write world-model Practice from hop tape or only letters.",
        "- .grok/agents/mortimer.md\n- docs/crew/log/mortimer.md\n- docs/crew/mortimer.md\n- docs/program/CHARTER.md RSI paragraph\n- docs/program/world-model.md Practice last heading\n- docs/program/slate.md",
        since
    ),
});
mjobs.push(#{
    label: "comms-others",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Katherine, Verena, Walt, spotter, unused pilots",
        "Katherine ticket/desk. Verena press. Walt CAPCOM no job card. spotter DEPRECATED still a file. bill/bob/valentina/grok stubs. Who is out of the loop. Parent spawn table still lists them.",
        "- .grok/agents/katherine.md\n- .grok/agents/verena.md\n- .grok/agents/spotter.md\n- .grok/agents/bill.md .grok/agents/bob.md .grok/agents/valentina.md .grok/agents/grok.md\n- docs/crew/log/katherine.md verena.md walt.md\n- AGENTS.md spawn table\n- docs/press/INDEX.md first 20",
        since
    ),
});

let comms = parallel(mjobs);
let comms_blob = "";
let mi = 0;
for r in comms {
    comms_blob += "\n\n===== COMMS ";
    comms_blob += mi.to_string();
    comms_blob += " =====\n";
    comms_blob += text_of(r);
    mi += 1;
}
log("comms slots=" + mi.to_string());
let comms_digest = clip(comms_blob, 7000);
let _mscratch = write_scratch_file("comms.md", comms_blob);

phase("Classify");
let kjobs = [];
kjobs.push(#{
    label: "class-program",
    capability_mode: "read-only",
    prompt: classify_prompt(
        "docs/program/*.md and org-flow/",
        "- docs/program/ (list_dir, wc every md)\n- docs/program/org-flow/\n- docs_inventory.py _ORG_NOVEL_NAMES",
        "CHARTER/PROTOCOL/OPS/BRIEF/slate/desk/ship/uplink/GLOSSARY/krpc are likely KEEP or TAPE. RSI report novels (lars-rsi, learn-rsi, feedback-plan) and note-tech/loop dual plan dumps are NUKE-LIVE or ARCHIVE. world-model is the hard call — chair vs poison."
    ),
});
kjobs.push(#{
    label: "class-missions-crew",
    capability_mode: "read-only",
    prompt: classify_prompt(
        "docs/missions + docs/crew + docs/flights",
        "- docs/missions/\n- docs/crew/\n- docs/flights/\n- docs/program/current.md",
        "jsonl is TAPE. Seated plan/science/craft are RENDER or dual-board. Crew portraits KEEP. Crew logs are voice TAPE not dispatch. builder.md pointer NUKE-LIVE. Jebediah-as-the-only-mission is the structural bug — classify the folder, do not dump 442 logs."
    ),
});
kjobs.push(#{
    label: "class-agents-lessons",
    capability_mode: "read-only",
    prompt: classify_prompt(
        ".grok/agents + docs/lessons.md + docs/agent-notes.md + AGENTS.md",
        "- .grok/agents/\n- docs/lessons.md header + heading count\n- docs/agent-notes.md header\n- AGENTS.md first 40",
        "Job cards KEEP but may be too long (REWRITE not a class — mark NUKE-LIVE paragraphs). spotter NUKE-LIVE. lessons.md Os named as poison — default NUKE-LIVE or ARCHIVE unless a kernel still requires the file. agent-notes KEEP only if still-true API; else archive the rest."
    ),
});
kjobs.push(#{
    label: "class-archive-press",
    capability_mode: "read-only",
    prompt: classify_prompt(
        "docs/archive + docs/press + README pointers",
        "- docs/archive/README.md\n- docs/archive/2026-08-23-md-cutover/README.md\n- docs/press/INDEX.md\n- README.md lessons link\n- docs/program/RO.md",
        "archive/ must stay PARKED and uninjected. If a live spawn still names a parked path, that is poison. Press KEEP for Verena. README should not send desks into lessons.md."
    ),
});
kjobs.push(#{
    label: "class-tickets-kernel",
    capability_mode: "read-only",
    prompt: classify_prompt(
        "docs/program/tickets + docs_inventory leftovers",
        "- docs/program/tickets/\n- docs_inventory.py\n- tests/test_protocol.py lessons reads",
        "BOARD.md is a dump not dispatch (BRIEF says so). fingerprints.json KEEP (kernel). head.json TAPE/kernel. Tests that force lessons.md to exist are a blocker on NUKE."
    ),
});

let classes = parallel(kjobs);
let class_blob = "";
let ki = 0;
for r in classes {
    class_blob += "\n\n===== CLASS ";
    class_blob += ki.to_string();
    class_blob += " =====\n";
    class_blob += text_of(r);
    ki += 1;
}
log("classify slots=" + ki.to_string());
let class_digest = clip(class_blob, 6000);
let _kscratch = write_scratch_file("classify.md", class_blob);

phase("Friction");
let prior = "";
prior += "CENSUS:\n";
prior += compile_digest;
prior += "\nHARVEST:\n";
prior += harvest_digest;
prior += "\nCOMMS:\n";
prior += comms_digest;
prior += "\nCLASS:\n";
prior += class_digest;
let prior_clip = clip(prior, 9000);

let fjobs = [];
fjobs.push(#{
    label: "friction-lessons",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "lessons.md does not scale and poisons hires",
        "Os special. Verify: 2871 lines; append-per-miss; AGENTS.md tells parent miss physics lives there; Lars card After a miss appends; BRIEF/OPS/PROTOCOL keep it; tests read it; children agents_md false but still write it so the next Lars re-reads a novel. Many headings may be superseded by later patches of the same fingerprint (rf-ignition-ullage many times). Wrong lessons staying canonical is the failure. Cheapest replacement the NEXT hire actually reads (ticket close_why / findings / named-file docstring / agent-notes API only).",
        prior_clip
    ),
});
fjobs.push(#{
    label: "friction-dual",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Dual boards and leftover mailboxes",
        "plan.md program vs seated. science.md dump vs payload. vab.md vs C- tickets. note-tech 08-21 Commander mailbox. loop.md radio vs uplink.md. world-model Open questions vs ops --tag ask. BOARD.md vs inbox. sit-card.json vs fly ticket. Which of these a hire still opens.",
        prior_clip
    ),
});
fjobs.push(#{
    label: "friction-jeb-folder",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Uncrewed tape still lives under Jebediah",
        "current.md flight: jebediah. attach-run path BRIEF still missions/jebediah/logs. 442 files. loop.md still acking pad aborts. Commander: none on uncrewed. Os: Jeb has not flown in days. Structural: mission id = kerbal seat, so the folder is a lie when the parent flies.",
        prior_clip
    ),
});
fjobs.push(#{
    label: "friction-lars-compose",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Lars still grows a factory instead of composing one rocket from a catalog",
        "lars-rsi extracted pad-RF only. hop_factory.py ~1051 still the inland compose. hop.py ~3300 parked+shared. No per-craft file. Job card says a t7-only file is legal then sends him into hop_factory. Wernher owns blocks; Lars does not have a catalog API besides import physics_warp. Next miss still re-reads the factory. test_hop.py 231.",
        prior_clip
    ),
});
fjobs.push(#{
    label: "friction-cards",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Stale cards, leftover roles, too-long cards",
        "spotter.md live. bill/bob/valentina/grok stubs. builder.md pointer. hank 194 / lars 192 / gene 169 lines of pulse law copied from PROTOCOL. S/M/C on some first commands, T-081 still the fly ticket. Return fences vs findings unused. Who is not in the loop on prefixes, named helper, last-flight is postcard.",
        prior_clip
    ),
});
fjobs.push(#{
    label: "friction-hank",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Hank in-between: glue that is still a novel",
        "Parent switchboard IS Hank. ops next, leftover, attach-run, landing, protocol fly, packet, ship.md, screenshot, commit nag. Children do not spawn. Ground talk is ops --tag ask. Failure: desks write md because they cannot cheaply address another desk; Hank re-derives from last-flight/lessons; RSI jumps add another live report md. What MUST stay Hank (pad, leftover, one writer) vs what should be kernel so he does not re-read six boards.",
        prior_clip
    ),
});
fjobs.push(#{
    label: "friction-inject",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Wrong store / wrong access",
        "Os: data stored where it should not be; accessed where it should not be. Map: jsonl read by desks; BOARD.md; lessons whole file; last-flight as vessel; world/tech/parts re-run despite desk.md; crew log as dispatch; archive paths in spawn. Packet law vs actual first files opened (job card Inputs vs First command vs AGENTS parent).",
        prior_clip
    ),
});
fjobs.push(#{
    label: "friction-rsi-reports",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "RSI reports and org novels in the live program tree",
        "lars-rsi.md learn-rsi.md feedback-plan.md org-flow/ in docs/program. Inventory may call them leftover. Next Mortimer/Hank may open them as law. Archive already has 2026-08-23-md-cutover copies of SPEED/ORG/NEXT-ORG. Pattern: every RSI leaves a new live md. That is the pile.",
        prior_clip
    ),
});

let frictions = parallel(fjobs);
let friction_blob = "";
let fi = 0;
for r in frictions {
    friction_blob += "\n\n===== FRICTION ";
    friction_blob += fi.to_string();
    friction_blob += " =====\n";
    friction_blob += text_of(r);
    fi += 1;
}
log("friction slots=" + fi.to_string());
let friction_digest = clip(friction_blob, 7000);
let _fscratch = write_scratch_file("friction.md", friction_blob);

phase("Interview");
let sim = "";
sim += "Date 2026-08-26. Last RSI lars-rsi applied prefixes + hop_factory_pad. ";
sim += "lessons.md ~2871 lines. missions/jebediah/logs ~442 files. current.md still jebediah. ";
sim += "Uncrewed parent flies. T-081 go yes campaign uncrewed. Bank ~2.29. ";
sim += "spotter.md still on disk. note-tech 08-21. hop.py ~3300 hop_factory ~1051. ";
sim += "Os: clusterfuck; rip stale; ticket bus; Lars compose from Wernher catalog; ";
sim += "do not inject lessons; pad occupancy; no Gene merge; no Return keys.";

let ijobs = [];
ijobs.push(#{
    label: "talk-hank",
    agent_type: "hank",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Hank Grokman",
        "COO",
        "the in-between — leftover, packet, attach-run, ops next, which boards you still open",
        sim
    ),
});
ijobs.push(#{
    label: "talk-lars",
    agent_type: "lars",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Lars Grokman",
        "Vehicle Systems Engineer",
        "why lessons.md + hop_factory instead of one compose file from Wernher blocks",
        sim
    ),
});
ijobs.push(#{
    label: "talk-wernher",
    agent_type: "wernher",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Wernher Grokman",
        "Chief Systems Engineer",
        "where the block catalog actually lives; what Lars should import; what kernel writes md",
        sim
    ),
});
ijobs.push(#{
    label: "talk-gene",
    agent_type: "gene",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Gene Grokman",
        "Launch / Flight Director",
        "plan.md / briefing.md / world-model last-writes vs fly ticket stamps",
        sim
    ),
});
ijobs.push(#{
    label: "talk-gus",
    agent_type: "gus",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Gus Grokman",
        "Vehicle Engineering Lead",
        "vab.md vs C- tickets; who you talk to when Lars shears a hang",
        sim
    ),
});
ijobs.push(#{
    label: "talk-linus",
    agent_type: "linus",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Linus Grokman",
        "Director of Research",
        "science.md dump vs payload; dual seated science.md; Jebediah folder binds",
        sim
    ),
});
ijobs.push(#{
    label: "talk-mortimer",
    agent_type: "mortimer",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Mortimer Grokman",
        "CEO",
        "every RSI left a live md; lessons injection; Practice vs ticket findings",
        sim
    ),
});
ijobs.push(#{
    label: "talk-jeb",
    agent_type: "jebediah",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Jebediah Grokman",
        "Commander",
        "seat id vs uncrewed parent-fly; why tape still lands in your mission folder",
        sim
    ),
});

let talks = parallel(ijobs);
let talk_blob = "";
let ti = 0;
for r in talks {
    talk_blob += "\n\n===== TALK ";
    talk_blob += ti.to_string();
    talk_blob += " =====\n";
    talk_blob += text_of(r);
    ti += 1;
}
log("interview slots=" + ti.to_string());
let talk_digest = clip(talk_blob, 6000);
let _tscratch = write_scratch_file("interviews.md", talk_blob);

phase("Design");
let design_p = walls();
design_p += "You are Mortimer Grokman, CEO. Write a BOUNDED plan for Os. ";
design_p += "Do not edit. Do not fly. Do not open tickets.\n";
design_p += "Read (verify, do not vibe): docs_inventory.py, PROTOCOL.md Files + Spawn packet, ";
design_p += "OPS.md split of power, AGENTS.md spawn table (spotter), .grok/agents/lars.md After a miss, ";
design_p += "tickets.py packet() + ID_PREFIX, docs/lessons.md header, docs/program/current.md, ";
design_p += "docs/missions/INDEX.md, CHARTER.md RSI paragraph.\n";
design_p += "Os (Founder), verbatim intent: extensive status quo of stale docs and comms; ";
design_p += "who responds to whom; how Hank handles the in-between; outdated cards; ";
design_p += "who takes too long / is out of the loop; who still writes md; poison structural docs; ";
design_p += "lessons.md does not scale and is injected; Jebediah folder still takes uncrewed tape; ";
design_p += "Lars not on per-rocket compose from Wernher catalog; spotter leftover; ";
design_p += "rip what should not be there; ticket bus is comms; MD only when a ticket cannot; ";
design_p += "pristine org that can fly to the stars.\n";
design_p += "Hard caps: PLAN ONLY. No TYPE zoo. No CHARTER creed rewrite. No hop pulse-law retune in this plan's first slice. ";
design_p += "Do not ticket portraits, CHARTER, jsonl tape, desk.md snapshot, slate goal. ";
design_p += "Do not restore spotter, Gene merge, Batch Learn, Return keys, need_*. ";
design_p += "Pad occupancy stays. Depth 1. One control writer. protocol fly fallback may stay one release. ";
design_p += "A learning path during uncrewed already exists (attach-run) — do not undo learn-rsi. ";
design_p += "lars-rsi prefixes and pad-RF extract stay — do not undo. ";
design_p += "Every RSI must NOT leave a new live docs/program/*.md novel; reports go to archive or scratch.\n";
design_p += "Prior (clipped, untrusted):\nCENSUS:\n";
design_p += compile_digest;
design_p += "\nHARVEST:\n";
design_p += harvest_digest;
design_p += "\nCOMMS:\n";
design_p += comms_digest;
design_p += "\nCLASS:\n";
design_p += class_digest;
design_p += "\nFRICTION:\n";
design_p += friction_digest;
design_p += "\nTALKS:\n";
design_p += talk_digest;
design_p += "\nWrite markdown:\n";
design_p += "## Summary (16 lines max)\n";
design_p += "## Comms law (who → whom; Hank in-between; what is a ticket vs md)\n";
design_p += "## Injection law (what a cold hire loads; what is forbidden to name in spawn)\n";
design_p += "## KEEP-MD (path | why the next hire reads it)\n";
design_p += "## TAPE (keep on disk, never inject)\n";
design_p += "## ARCHIVE (move under docs/archive/ this sit)\n";
design_p += "## NUKE-LIVE (delete or stub; tests to fix first)\n";
design_p += "## MOVE to tickets (key → field)\n";
design_p += "## lessons.md replacement (the NEXT Lars hire must not open 2871 lines)\n";
design_p += "## Mission identity (stop naming uncrewed tape after Jebediah)\n";
design_p += "## Lars compose (one living rocket file from Wernher catalog — later ticket, not this first slice if it retunes pulse law; still name the ticket)\n";
design_p += "## Job-card cuts (max 8 cards | what to delete)\n";
design_p += "## Hank in-between after cutover (ops next still; which boards die)\n";
design_p += "## Sequence (max 8 slices, owner, pad-safe)\n";
design_p += "## Tickets to open later (max 6, type/desk/title/fingerprint) — DO NOT OPEN\n";
design_p += "## Do not touch\n";

let design_r = agent(design_p, #{
    label: "design-pristine",
    agent_type: "mortimer",
    capability_mode: "read-only",
});
let design_text = text_of(design_r);
if design_text == "" {
    design_text = "DESIGN EMPTY — do not treat as a plan. Re-read docs_inventory.py and docs/lessons.md header.";
}
log("design done");
let _dscratch = write_scratch_file("design.md", design_text);
let design_json = json_encode(clip(design_text, 8000));

phase("Skeptics");
let sk_over = walls();
sk_over += "Adversarial over-nuke. real=true only if the DESIGN tickets CHARTER/portraits/jsonl/desk.md, ";
sk_over += "deletes protocol fly fallback so the house bricks, restores two kRPC writers, ";
sk_over += "idles the pad for a novel, or deletes tape the next Learn/bind needs. ";
sk_over += "Else real=false with path evidence. Fail closed: missing evidence = real=false.\nDESIGN:\n";
sk_over += design_json;

let sk_under = walls();
sk_under += "Adversarial under-nuke. real=true if after the DESIGN a cold hire is STILL told to read ";
sk_under += "docs/lessons.md as miss physics, OR spotter.md remains a spawnable card, ";
sk_under += "OR uncrewed attach-run still hard-codes missions/jebediah/logs, ";
sk_under += "OR lars-rsi.md/learn-rsi.md/feedback-plan.md/note-tech stay live dispatch, ";
sk_under += "OR BOARD.md remains packet skim. Else real=false with evidence. Fail closed.\nDESIGN:\n";
sk_under += design_json;

let sk_md = walls();
sk_md += "Adversarial still-md-bus. real=true if the DESIGN keeps lessons.md append as Lars After a miss, ";
sk_md += "OR keeps need_*/Return keys, OR uses world-model Open questions as the ask bus, ";
sk_md += "OR adds another live docs/program org novel as the deliverable. Else real=false. Fail closed.\nDESIGN:\n";
sk_md += design_json;

let sk_lars = walls();
sk_lars += "Adversarial Lars gap. real=true if the DESIGN has no ticket/slice for ";
sk_lars += "(1) stop appending lessons.md and (2) one living-rocket compose from Wernher blocks ";
sk_lars += "(even if slice 2 is later and must not retune pulse law this paper). ";
sk_lars += "real=true also if it tells Lars to keep hop.py as the factory. Else real=false. Fail closed.\nDESIGN:\n";
sk_lars += design_json;

let sk_hank = walls();
sk_hank += "Adversarial Hank glue. real=true if after cutover Hank still must open BOARD.md + lessons.md + ";
sk_hank += "note-tech + world-model + dual plan to run ops next, OR children still cannot address ";
sk_hank += "another desk except by md. Else real=false (ops next + leftover + packet MAY stay). Fail closed.\nDESIGN:\n";
sk_hank += design_json;

let skeptics = parallel([
    #{ label: "skeptic-overnuke", capability_mode: "read-only", prompt: sk_over },
    #{ label: "skeptic-undernuke", capability_mode: "read-only", prompt: sk_under },
    #{ label: "skeptic-md-bus", capability_mode: "read-only", prompt: sk_md },
    #{ label: "skeptic-lars", capability_mode: "read-only", prompt: sk_lars },
    #{ label: "skeptic-hank", capability_mode: "read-only", prompt: sk_hank },
]);
log("skeptics done");
let sk_blob = "";
let si = 0;
for r in skeptics {
    sk_blob += "\n\n===== SKEPTIC ";
    sk_blob += si.to_string();
    sk_blob += " =====\n";
    sk_blob += text_of(r);
    si += 1;
}
let sk_digest = clip(sk_blob, 5000);
let _sscratch = write_scratch_file("skeptics.md", sk_blob);

phase("Tighten");
let tight_p = walls();
tight_p += "You are Mortimer Grokman, CEO. TIGHTEN the plan. Do not edit the repo. ";
tight_p += "If a skeptic real=true, you MUST change that row of the plan (qualify or replace). ";
tight_p += "If real=false, keep the DESIGN row. Fail closed on missing skeptic evidence — do not 'fix' a false alarm.\n";
tight_p += "DESIGN:\n";
tight_p += design_json;
tight_p += "\nSKEPTICS:\n";
tight_p += sk_digest;
tight_p += "\nWrite the SAME headings as Design, now the final plan. Add ## Skeptics folded (which real=true changed what).\n";

let tight_r = agent(tight_p, #{
    label: "tighten-plan",
    agent_type: "mortimer",
    capability_mode: "read-only",
});
let tight_text = text_of(tight_r);
if tight_text == "" {
    tight_text = design_text;
}
log("tighten done");
let _tightscratch = write_scratch_file("plan-tight.md", tight_text);
let tight_json = json_encode(clip(tight_text, 9000));

phase("Report");
let rep = walls();
rep += "You are Mortimer Grokman, CEO. Write ONE GitHub-markdown report for Os. ";
rep += "Do not edit the repo. Do not open tickets. Do not Hangar.\n";
rep += "Title: Org pristine — status quo and plan (2026-08-26).\n";
rep += "This report is the deliverable. It must stand alone. Verify every count you cite with read_file/grep if the notes conflict.\n";
rep += "PART I is the extensive status quo. PART II is the tightened plan.\n";
rep += "PART I sections:\n";
rep += "1 Sit (lock, last RSI, what Os asked)\n";
rep += "2 Communication graph (who → whom; Hank in-between; ticket vs md vs radio)\n";
rep += "3 What each desk still writes and reads (since ";
rep += since;
rep += ")\n";
rep += "4 Injection (what a cold hire loads; lessons.md; AGENTS vs job cards)\n";
rep += "5 Dual stores and leftover mailboxes (plan/science/vab/note-tech/loop/BOARD/world-model)\n";
rep += "6 Mission identity (Jebediah folder vs uncrewed parent-fly)\n";
rep += "7 Lars vs Wernher catalog (files, line counts, lars-rsi leftover)\n";
rep += "8 Stale cards and out-of-loop desks (spotter, stubs, prefixes, hire length)\n";
rep += "9 Poison live docs (table: path | lines | class | why)\n";
rep += "10 Prior RSI: what stuck, what failed, what the jumps added to the pile\n";
rep += "11 Wrong access (who reads jsonl / last-flight / BOARD / lessons / archive)\n";
rep += "PART II: paste the tightened plan headings in full (comms law through do-not-touch), then ";
rep += "12 How the next hire is cheaper 13 Open risks 14 This workflow did not apply.\n";
rep += "No Hangar. No creed rewrite. Quote paths.\n";
rep += "TIGHT PLAN:\n";
rep += tight_json;
rep += "\nSKEPTICS:\n";
rep += sk_digest;
rep += "\nCENSUS:\n";
rep += compile_digest;
rep += "\nHARVEST:\n";
rep += harvest_digest;
rep += "\nCOMMS:\n";
rep += comms_digest;
rep += "\nCLASS:\n";
rep += class_digest;
rep += "\nFRICTION:\n";
rep += friction_digest;
rep += "\nTALKS:\n";
rep += talk_digest;

let report_r = agent(rep, #{
    label: "report-pristine",
    agent_type: "mortimer",
    capability_mode: "read-only",
});
let report = text_of(report_r);
if report == "" {
    report = "# Org pristine — status quo and plan\n\nEMPTY report agent. Tight plan follows.\n\n";
    report += tight_text;
}
let scratch = write_scratch_file("org-pristine.md", report);
let design_ok = false;
if design_r != () {
    if design_r.success == true {
        if design_text != "DESIGN EMPTY — do not treat as a plan. Re-read docs_inventory.py and docs/lessons.md header." {
            design_ok = true;
        }
    }
}
complete(#{
    path: scratch,
    apply: false,
    since: since,
    census_slots: ci,
    harvest_slots: hi,
    comms_slots: mi,
    classify_slots: ki,
    friction_slots: fi,
    interview_slots: ti,
    skeptic_slots: si,
    design_ok: design_ok,
});
