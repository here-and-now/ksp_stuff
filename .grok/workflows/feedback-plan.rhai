let meta = #{
    name: "feedback-plan",
    description: "Compile last-loop desk work and friction, interview what desks would actually file, then write a ticket-native skeptic-style feedback plan. No code.",
    when_to_use: "When Os wants a plan for hire feedback on the ticket bus, replacing good/self/them, before any kernel patch",
    phases: [
        #{ title: "Compile", detail: "what each desk did, good, wrong, requests" },
        #{ title: "Friction", detail: "current door, sharing, hop vs org" },
        #{ title: "Interview", detail: "what each desk would file if free to choose" },
        #{ title: "Design", detail: "concrete ticket-native skeptic plan" },
        #{ title: "Skeptics", detail: "refute card-in-disguise and unused-door" },
        #{ title: "Report", detail: "scratch feedback-plan.md — not live docs/program/" },
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
    p += "NO hop.py / hop_factory.py / physics_warp.py / pad.py / splash.py retune. ";
    p += "NO tickets.py kernel patch. NO job-card rewrite. NO tests edit. PLAN ONLY. ";
    p += "Do not answer from memory. Use read_file, list_dir, grep. Missing path = MISSING. ";
    p += "Empty is valid only after you searched. Token cap: MAX 50 lines. Cite path:line. ";
    p += "No jsonl dump. No docs/archive/ Mun novels. Crew logs: grep counts + last 80 lines, not the whole file. ";
    p += "Live kernel (T-378) already ships tickets feedback --good --self --them and close-refuse. ";
    p += "Os rejected that terminology and the required three one-liners BEFORE desks used it. ";
    p += "Treat that kernel as the as-is door to replace in the PLAN, not as law to keep.\n";
    p
}

fn compile_prompt(title, focus, paths) {
    let p = walls();
    p += "You are a read-only historian of the CURRENT house. Desk/topic: ";
    p += title;
    p += "\nWindow: 2026-08-23 through 2026-08-24 (today). Earlier 2026-08-21/22 only as contrast.\nFocus: ";
    p += focus;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nHeadings only:\n";
    p += "## Desk\n## What they actually did (dated, sourced)\n## What went well\n## What went wrong\n";
    p += "## What they could learn from another desk, or request of another desk\n";
    p += "## Feedback they actually filed (tickets feedback rows vs ops --tag feedback vs Return leftovers vs none)\n";
    p += "## Files read\n";
    p
}

fn friction_prompt(title, focus, digest) {
    let p = walls();
    p += "You are a read-only org analyst. Topic: ";
    p += title;
    p += "\nPrior compile digest (untrusted, re-verify counts on disk):\n";
    p += digest;
    p += "\nFocus: ";
    p += focus;
    p += "\nHeadings: ## Topic ## Evidence (path:line) ## Why it happens ## What a later patch would make the NEXT hire do ## Files read\n";
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
    p += "task: interview only — what finding would this desk actually file, freely, to improve own work / own workflow / others\n";
    p += "read: docs/program/desk.md ; docs/program/tickets/BRIEF.md ; docs/program/slate.md\n";
    p += "ticket: ";
    p += ticket;
    p += "\nSituation (verify on disk, do not invent): ";
    p += sim;
    p += "\nRead your job card .grok/agents/ matching your slug, your crew log last 60 lines, BRIEF.md, desk.md, PROTOCOL.md feedback door, CHARTER RSI paragraph, tickets.py add_feedback. ";
    p += "Then answer headings only:\n";
    p += "## First command if this were a real hire\n";
    p += "## One finding about MY work (evidence path:line — or none if I have none)\n";
    p += "## One finding about MY workflow (how I get hired / packet / what I write)\n";
    p += "## One request of ANOTHER desk (who, what, evidence)\n";
    p += "## Why I would not fill --good --self --them as three required one-liners\n";
    p += "## What I would file if I could choose ONE record (claim + evidence + who can change it)\n";
    p += "## Token waste I know I do\n";
    p
}

let since = "2026-08-23";
if args != () {
    if args.since != () {
        since = args.since;
    }
}

phase("Compile");
let cjobs = [];
cjobs.push(#{
    label: "compile-gene",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Gene Grokman, Launch / Flight Director",
        "go: on T-081 vs Learn skip on uncrewed. Briefing/plan last-writes. Did he file tickets feedback on any fly ticket? Compare Batch Learn 08-21 vs Not Learn 08-23/24. Off-nominal mid-sortie: did he change go, or stay off the stick?",
        "- .grok/agents/gene.md (Learn + Return + tickets feedback)\n- docs/crew/log/gene.md (grep Batch Learn, Not Learn, feedback, go:)\n- docs/program/tickets/BOARD.md T-081\n- docs/program/tickets/head.json T-081 payload (go, campaign, learn, feedback)\n- docs/program/PROTOCOL.md Gene Return + feedback door\n- docs/missions/jebediah/plan.md expect_apo_max / hop_apo"
    ),
});
cjobs.push(#{
    label: "compile-lars",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Lars Grokman, Vehicle Systems Engineer",
        "lessons.md dated headings 2026-08-24 vs hop.py / hop_factory.py / physics_warp.py patches. Same miss class, new fingerprint? Os: hop.py unmaintainable, do not overfit. T-379 Wernher extract blocks — did Lars compose or keep patching hop.py? Any tickets feedback row from lars? Requests of Wernher/Gus/Gene?",
        "- .grok/agents/lars.md\n- docs/crew/log/lars.md (last 80)\n- docs/lessons.md (headings 2026-08-24)\n- docs/program/tickets/BOARD.md desk=lars\n- docs/program/tickets/fingerprints.json (sci-unchanged-recovered, flyinghigh-lid, far-shear, hold-ground-card)\n- docs/program/blocks.md first 40\n- hop.py / hop_factory.py / physics_warp.py line counts only (wc via grep def, not dump)"
    ),
});
cjobs.push(#{
    label: "compile-wernher",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Wernher Grokman, Chief Systems Engineer",
        "T-378 kernel tickets feedback good/self/them. T-379 extract blocks. physics_warp leftover abort / chute_deploy_sit / want_coast. Feedback rows he actually wrote. Did systems close into Practice or only code? What he requested of Lars vs what Lars kept in hop.py.",
        "- .grok/agents/wernher.md\n- docs/crew/log/wernher.md\n- docs/program/tickets/BOARD.md T-378 T-379\n- docs/program/tickets/head.json T-378 T-379 payload.feedback\n- tickets.py add_feedback close_ticket inbox_for feedback_rows (line range)\n- docs/program/krpc.md first 40\n- docs/program/blocks.md"
    ),
});
cjobs.push(#{
    label: "compile-hank",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Hank Grokman, COO — ticket bus, leftover, after-flight tape",
        "ops next hire graph. attach-run + landing + leftover recover()+Close. Did Hank nag missing tickets feedback? Count ops --tag feedback vs type=rsi vs tickets feedback rows on the whole board. Pad occupancy vs CHARTER every-hire-leaves-a-sharper-sit. Parent swallowed Return keys then restored them then redirected to CLI.",
        "- .grok/agents/hank.md\n- docs/crew/log/hank.md (last 80)\n- ops.py next_actions / fly_ready / needing_go\n- docs/program/OPS.md feedback + RSI clocks\n- docs/program/tickets/BRIEF.md\n- tickets.py add_feedback / inbox_for / close_ticket\n- tests/test_tickets.py test_feedback_appends"
    ),
});
cjobs.push(#{
    label: "compile-shelf",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Gus Grokman + Linus Grokman (vehicle shelf vs science envelope)",
        "t7 Valiant existence proof vs shear on 4t/dv5/lite. capable: vs bind. T-069 FlyingHigh leftover vs loft +0. Did +0 Forest hops change the next bind? Vehicle tickets vs feedback rows. What Gus needs from Lars (loft without silk/shear) and Linus from Gus (instrument on the hang).",
        "- .grok/agents/gus.md\n- .grok/agents/linus.md\n- docs/crew/log/gus.md (last 40)\n- docs/crew/log/linus.md (last 40)\n- docs/program/vab.md first 40\n- docs/program/science.md first 40\n- BOARD.md T-318 T-069 T-368 T-369 T-081\n- docs/missions/jebediah/craft.md"
    ),
});
cjobs.push(#{
    label: "compile-commander",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Jebediah Grokman, Commander + Katherine Flight Dynamics",
        "CLI exit ends the hop. Uncrewed commander: none so parent flies. What the stick used to return (improve/feedback) that job cards now forbid. Did anyone file tickets feedback on the fly ticket after lithobrake? Katherine tape windows — did anyone read her into a finding? note-tech leftover.",
        "- .grok/agents/pilot.md\n- .grok/agents/jebediah.md\n- .grok/agents/katherine.md\n- docs/crew/log/jebediah.md (last 40)\n- docs/crew/log/katherine.md\n- docs/program/note-tech.md (last 30)\n- docs/last-flight.md if present\n- BOARD.md T-283"
    ),
});
cjobs.push(#{
    label: "compile-mortimer",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Mortimer Grokman, CEO — Practice, org RSI, feedback door",
        "T-375/T-376/T-377/T-378: Return keys then tickets CLI. CHARTER now quotes --good --self --them. Practice last-write. Open type=rsi. Os letters vs hop tape as the source of org mutation. Did Mortimer file the only real feedback rows on the board?",
        "- .grok/agents/mortimer.md\n- docs/crew/log/mortimer.md\n- docs/crew/mortimer.md\n- docs/program/CHARTER.md RSI paragraph (lines 14-30)\n- docs/program/world-model.md Practice\n- docs/program/slate.md\n- BOARD.md type=rsi type=org T-375 T-378\n- docs/program/GLOSSARY.md tickets feedback"
    ),
});
cjobs.push(#{
    label: "compile-kernel",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Feedback surfaces on disk (kernel vs usage)",
        "COUNT, do not vibe. (1) How many tickets in head.json have payload.feedback (grep). Quote the actual rows — who/good/self/them. (2) ops --tag feedback open vs done. (3) type=rsi open. (4) ops --tag ask done vs open. (5) tickets close refused empty — any live miss besides tests? (6) inbox --feedback mentioned in job cards vs anyone running it. (7) Grok Build skeptic analogue in .grok/workflows/learn-rsi.rhai Verify skeptics and create-workflow SKILL example (findings + real=true + evidence).",
        "- docs/program/tickets/head.json (grep payload.feedback / \"good\":)\n- docs/program/tickets/BOARD.md (type=rsi, tag feedback, tag ask)\n- tickets.py add_feedback close_ticket inbox_for CLI --good --self --them\n- tests/test_tickets.py test_feedback_appends_and_close_refuses_empty\n- .grok/workflows/learn-rsi.rhai skeptic-overscope / skeptic-gap\n- docs/program/PROTOCOL.md lines 80-95 and 465-482\n- docs/program/learn-rsi.md section 4 Feedback door"
    ),
});

let compiles = parallel(cjobs);
let compile_blob = "";
let ci = 0;
for r in compiles {
    compile_blob += "\n\n===== COMPILE ";
    compile_blob += ci.to_string();
    compile_blob += " =====\n";
    compile_blob += text_of(r);
    ci += 1;
}
log("compile slots=" + ci.to_string());
let compile_digest = clip(compile_blob, 8000);
let _cscratch = write_scratch_file("compile.md", compile_blob);

phase("Friction");
let fjobs = [];
fjobs.push(#{
    label: "friction-card",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "good/self/them is still a card on a ticket",
        "Os: terminology is bad; required three one-liners; not satisfied with the structure. Verify: add_feedback requires good AND self (them may be none). PROTOCOL forbids those words as Return keys then requires them as CLI flags. CHARTER quotes the three flags. GLOSSARY still says one line each. Count how many non-Mortimer/Wernher desks filed a row. A later patch must drop the three named slots — not rename them praise/me/you.",
        compile_digest
    ),
});
fjobs.push(#{
    label: "friction-unused",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Mandatory door that flying desks have not used",
        "close_ticket refuses empty payload.feedback, but hop tickets (T-081 and the 2026-08-24 control tickets) likely have no row. Parent nag in hank.md vs pad occupancy (do not idle the pad for a novel). rsi-jump already killed Return keys so the allowed body CLI went unused; T-378 replaced it with three required flags — still a remembered CLI. What would make a hire actually leave a finding without a 15 min essay?",
        compile_digest
    ),
});
fjobs.push(#{
    label: "friction-share",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Sharing and cross-desk requests have no real inbox loop",
        "inbox --desk X --feedback is last-row them=X plus owned missing. Last-row only: an earlier them=lars is dropped when a later them=none is appended (test_tickets says so). ops --tag ask is the relay — count used. Desks must not tell another desk in Return prose. Result: Lars cannot cheaply request Wernher blocks; Gus cannot cheaply request loft-without-silk; Linus cannot cheaply request bind-from-envelope. Grok Build skeptics report findings others independently verify (real=true + evidence). Map that onto tickets: finding on the work T-id, owner who can change it, confirm/refute.",
        compile_digest
    ),
});
fjobs.push(#{
    label: "friction-hop",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Vehicle control vs systems vs vehicle shelf — last-loop work",
        "Os: hop.py and hop_factory unmaintainable; Wernher owns generalizable blocks; Lars may compose one living rocket; tests lock blocks not dead hangs. Compile what each actually did 08-24 (skip latch, chute arm vs deploy, lid cut, t7 crafts, T-379). What went well (t7 88 km existence, leftover recover not revert, attach_run learn). What went wrong (lithobrake after loft, silk-while-burn, unique fingerprints, overfitting). What Lars should request of Wernher, Wernher of Lars, Gus of both — as findings, not speeches.",
        compile_digest
    ),
});
fjobs.push(#{
    label: "friction-learn",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Learn stamp vs feedback vs RSI — three channels that do not talk",
        "attach_run overwrites payload.learn (numbers). tickets feedback is hire RSI ore (unused). type=rsi is fingerprint x3 (almost never, unique stems). CHARTER says every hire leaves a sharper sit. The sit the next hop reads is learn: (envelope), not a finding. A plan must keep pad occupancy AND make the next hire actually read a finding when it is addressed to them. Do not restore 15 min Gene novels. Do not make feedback a fourth board.",
        compile_digest
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
sim += "T-081 fly go=yes campaign=uncrewed python main.py hop. t7 Valiant lofted ~88 km then later hangs lithobraked / sheared. ";
sim += "T-378 shipped tickets feedback --good --self --them; close refuses empty. Os rejected that structure before flying desks used it. ";
sim += "T-379 Wernher extract blocks; hop.py still the inland factory. Bank ~9.47, stability 18. ";
sim += "payload.feedback rows on the board are Mortimer/Wernher on T-375/T-378/T-379 — not Lars/Gus/Gene/Jeb. ";
sim += "Open RSI stems exist; unique-per-hop control tickets still mint. Pad occupancy standing. Idle pad is a sin.";

let ijobs = [];
ijobs.push(#{
    label: "talk-gene",
    agent_type: "gene",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Gene Grokman",
        "Launch / Flight Director",
        "T-081 — go: vs what a finding on the fly ticket would have changed",
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
        "hop.py overfit vs Wernher blocks — what finding / request would you file",
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
        "T-378 three flags vs a skeptic finding record — what you would replace them with",
        sim
    ),
});
ijobs.push(#{
    label: "talk-hank",
    agent_type: "hank",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Hank Grokman",
        "COO",
        "after CLI: attach-run + leftover. Where does a finding get read without idling the pad",
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
        "t7 capable vs shear on lighter hangs — request of Lars / Linus",
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
        "FlyingHigh leftover unbound while loft +0 — request of Gus / Gene",
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
        "CHARTER quotes --good --self --them. Os wants skeptic findings. How the house shares improvement.",
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
design_p += "You are Mortimer Grokman, CEO, writing a CONCRETE PLAN for Os. ";
design_p += "Do not edit. Do not fly. Do not open tickets. Do not patch tickets.py. ";
design_p += "Read tickets.py add_feedback close_ticket feedback_rows inbox_for CLI (around 569-627, 1261-1291, 1603-1618), ";
design_p += "tests/test_tickets.py test_feedback_appends, PROTOCOL.md feedback door, CHARTER RSI paragraph, BRIEF.md, GLOSSARY.md tickets feedback, ";
design_p += ".grok/workflows/learn-rsi.rhai Verify skeptics, and the create-workflow example of findings + real=true + evidence.\n";
design_p += "Os (Founder), verbatim intent: compile what agents did, what went good, what went wrong, what one agent could learn from or request of another, frictions. ";
design_p += "Then a concrete plan, ONLY plan, no code. Extend feedback. Like Grok Build skeptics reporting bugs (findings with evidence; real=true only with independently inspected proof). ";
design_p += "Not satisfied with good/self/them terminology or required three one-liners. Each agent MUST give some feedback, FREE to choose what. ";
design_p += "They want to improve own work, own workflow, and others' workflows. Ticket-native. Get away from cards.\n";
design_p += "Hard caps: no new TYPE zoo (keep ops --tag feedback for stumble-during-work; hire ore lives on the work T-id). ";
design_p += "No hop.py retune in this plan's apply (vehicle compose is a different ticket). No CHARTER creed rewrite — wording of the door may change later. ";
design_p += "Pad occupancy stays. Do not restore Return keys. Do not restore 15 min Gene novels. ";
design_p += "Mandatory: at least one finding per hire (close may still refuse empty) but NOT three named slots. ";
design_p += "A finding is a claim + evidence + who can change it (or none). Empty-of-substance is invalid; empty-of-praise is fine. ";
design_p += "Skeptic analogue: another desk or Hank may confirm/refute; real=true only with inspected evidence. Unverified is not a confirming vote. ";
design_p += "Sharing: the addressee must see it on the next packet or inbox without last-row clobber. ";
design_p += "Migration: existing {who,good,self,them,at} rows stay readable.\n";
design_p += "Verify on disk, drop if false:\n";
design_p += "1. add_feedback requires --good and --self; --them is required by CLI even when none.\n";
design_p += "2. Almost no flying-desk rows exist; T-375/T-378/T-379 are the proof of unused.\n";
design_p += "3. inbox --feedback uses last row only (test says earlier them=lars dies).\n";
design_p += "4. PROTOCOL still forbids those words as Return keys.\n";
design_p += "5. Grok Build skeptics already use {real, reason, evidence} fail-closed in learn-rsi.rhai.\n";
design_p += "Prior (clipped, untrusted):\nCOMPILE:\n";
design_p += compile_digest;
design_p += "\nFRICTION:\n";
design_p += friction_digest;
design_p += "\nINTERVIEWS:\n";
design_p += talk_digest;
design_p += "\nWrite markdown (this is the plan body):\n";
design_p += "## Summary (12 lines max)\n";
design_p += "## What the last loop did (per desk, sourced)\n";
design_p += "## What went well\n";
design_p += "## What went wrong\n";
design_p += "## Cross-desk learn / request\n";
design_p += "## Why the current door fails\n";
design_p += "## Grok Build skeptic analogue\n";
design_p += "## Proposed record (schema + CLI flags — drop good/self/them; pick durable words)\n";
design_p += "## Mandatory but free choice (one or more findings; kinds)\n";
design_p += "## Sharing (inbox, packet, confirm/refute, who can change it)\n";
design_p += "## What the next hire actually types (one cheap example per desk class)\n";
design_p += "## Later patches (max 8 rows: file | change | owner | why) — DO NOT APPLY\n";
design_p += "## Tickets to open later (max 5) — DO NOT OPEN\n";
design_p += "## Do not touch\n";

let design_r = agent(design_p, #{
    label: "design-feedback",
    agent_type: "mortimer",
    capability_mode: "read-only",
});
let design_text = text_of(design_r);
if design_text == "" {
    design_text = "DESIGN EMPTY — do not treat as a plan. Re-read tickets.py add_feedback and PROTOCOL.md feedback door.";
}
log("design done");
let _dscratch = write_scratch_file("feedback-design.md", design_text);
let design_json = json_encode(clip(design_text, 8000));

let design_ok = false;
if design_r != () {
    if design_r.success == true {
        if design_text != "" {
            if design_text != "DESIGN EMPTY — do not treat as a plan. Re-read tickets.py add_feedback and PROTOCOL.md feedback door." {
                design_ok = true;
            }
        }
    }
}

phase("Skeptics");
let sk_card = walls();
sk_card += "Adversarial: is the DESIGN still a three-slot card? real=true only if the proposed record requires three named fields that are good/self/them under new labels (praise/me/you, keep/change/ask, etc.), ";
sk_card += "OR still requires a praise line, OR still forbids filing only a request, OR still forbids filing only an own-workflow finding. ";
sk_card += "Else real=false with path evidence from the DESIGN text. Fail closed: missing evidence = real=false.\nDESIGN:\n";
sk_card += design_json;

let sk_unused = walls();
sk_unused += "Adversarial: would flying desks still skip this door? real=true if the DESIGN still depends on remembering a long CLI with no packet/close hook, ";
sk_unused += "OR still nags a 15 min novel, OR still last-row-clobbers them= so requests vanish, OR has no example of one cheap command a Lars hire would actually type after a miss. ";
sk_unused += "Else real=false with evidence. Fail closed.\nDESIGN:\n";
sk_unused += design_json;

let sk_ticket = walls();
sk_ticket += "Adversarial: did the DESIGN leave the ticket bus? real=true if it restores Return keys, adds a new TYPE, opens a child ticket per hire, ";
sk_ticket += "or parks findings only in crew logs / world-model / note-tech. Else real=false with evidence. Fail closed.\nDESIGN:\n";
sk_ticket += design_json;

let skeptics = parallel([
    #{
        label: "skeptic-card",
        capability_mode: "read-only",
        prompt: sk_card,
    },
    #{
        label: "skeptic-unused",
        capability_mode: "read-only",
        prompt: sk_unused,
    },
    #{
        label: "skeptic-ticket",
        capability_mode: "read-only",
        prompt: sk_ticket,
    },
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
let sk_digest = clip(sk_blob, 4000);
let _sscratch = write_scratch_file("skeptics.md", sk_blob);

phase("Report");
let rep = walls();
rep += "Do not write live docs/program/feedback-plan.md. Report via write_scratch_file only. Title: Feedback plan (compile, no apply).\n";
rep += "Do not edit .py, job cards, CHARTER, PROTOCOL, tests. Do not open tickets. Do not Hangar.\n";
rep += "Sections: 1 Sit 2 What the last loop did 3 What went well 4 What went wrong 5 Cross-desk learn/request 6 Why the current door fails 7 Skeptic analogue 8 The plan (record, CLI, mandatory-but-free, sharing) 9 Skeptics on this plan 10 Later patches (do not apply) 11 Do not touch.\n";
rep += "Fold DESIGN in; if a skeptic real=true, call that out in section 9 and qualify the plan (do not silently keep a three-slot card).\n";
rep += "Append one line to docs/crew/log/mortimer.md noting plan-only, no kernel.\n";
rep += "DESIGN:\n";
rep += design_json;
rep += "\nSKEPTICS:\n";
rep += sk_digest;
rep += "\nCOMPILE:\n";
rep += compile_digest;
rep += "\nFRICTION:\n";
rep += friction_digest;
rep += "\nTALKS:\n";
rep += talk_digest;

let report_r = agent(rep, #{
    label: "report-plan",
    agent_type: "mortimer",
    capability_mode: "read-write",
});
let report = text_of(report_r);
if report == "" { report = design_text; }
let scratch = write_scratch_file("feedback-plan.md", report);
complete(#{
    path: scratch,
    apply: false,
    compile_slots: ci,
    friction_slots: fi,
    interview_slots: ti,
    skeptic_slots: si,
    design_ok: design_ok,
});
