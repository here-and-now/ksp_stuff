let meta = #{
    name: "learn-rsi",
    description: "Compile current-org comms and pain, diagnose why the learning/RSI loop went quiet, pause for Os, then apply bounded patches",
    when_to_use: "When desks still fly but do not learn, feedback is only a ticket body nobody opens, fingerprints never hit x3, or Os wants a confirmation-gated RSI pass after uncrewed campaign",
    phases: [
        #{ title: "Compile", detail: "current desks, tickets, last-day hops vs earlier Learns" },
        #{ title: "Friction", detail: "learning loop, RSI clocks, feedback door, pad vs CHARTER" },
        #{ title: "Interview", detail: "desks on why they did not learn" },
        #{ title: "Design", detail: "bounded learn/RSI patches" },
        #{ title: "Apply", detail: "kernel, job cards, Practice — after Os resume" },
        #{ title: "Verify", detail: "tests plus skeptics" },
        #{ title: "Report", detail: "scratch learn-rsi.md — not live docs/program/" },
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
    p += "Do not answer from memory. Use read_file, list_dir, grep. Missing path = MISSING. ";
    p += "Empty is valid only after you searched. Token cap: MAX 50 lines. Cite path:line. ";
    p += "No jsonl dump. No docs/archive/ Mun novels. Crew logs: grep counts + last 80 lines, not the whole file. ";
    p += "Prior rsi-jump (2026-08-22) already moved Learn onto payload.learn and skipped Gene between uncrewed hops — treat that as live law to audit, not as vapor.\n";
    p
}

fn compile_prompt(title, focus, paths, since, worked) {
    let p = walls();
    p += "You are a read-only historian of the CURRENT house. Desk/topic: ";
    p += title;
    p += "\nWindow that Os says learned worse: ";
    p += since;
    p += " through today (2026-08-24). Window that learned better: ";
    p += worked;
    p += " through 2026-08-22 (Gene Batch Learn on hop-to-water).\nFocus: ";
    p += focus;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nHeadings only:\n";
    p += "## Desk\n## What they actually wrote (dated, sourced)\n";
    p += "## Comms (who they talk to, tickets vs md, ask/feedback opened)\n";
    p += "## Pain (quoted)\n## Learning (Learn stamp, lessons.md, Practice, fingerprints)\n";
    p += "## Then vs now (";
    p += worked;
    p += " vs ";
    p += since;
    p += ")\n## Files read\n";
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
    p += "\nHeadings: ## Topic ## Evidence (path:line) ## Why it happens ## What a patch would make the NEXT hire do ## Files read\n";
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
    p += "task: interview only — why this desk did not learn / feedback / RSI on the last uncrewed string\n";
    p += "read: docs/program/desk.md ; docs/program/tickets/BRIEF.md ; docs/program/slate.md\n";
    p += "ticket: ";
    p += ticket;
    p += "\nlive_run: 2026-08-23T22-33-35Z-hop\n";
    p += "Situation (verify on disk, do not invent): ";
    p += sim;
    p += "\nRead your job card .grok/agents/ matching your slug, your crew log last 60 lines, BRIEF.md, desk.md, CHARTER RSI paragraph, OPS.md RSI clocks, gene/hank Learn rules. ";
    p += "Then answer headings only:\n";
    p += "## First command if this were a real hire\n## Why I did not leave a sharper sit last day\n";
    p += "## Feedback I would have given (and why I did not open ops --tag feedback)\n";
    p += "## Fingerprint stem I would reuse (not a new T-id)\n";
    p += "## What I write in markdown that should be a stamp or a ticket\n";
    p += "## One cheap mechanism that would make me actually learn next hop without a 15 min novel\n";
    p += "## Token waste I know I do\n";
    p
}

let apply_edits = true;
let since = "2026-08-23";
let worked = "2026-08-21";
if args != () {
    if args.apply == false {
        apply_edits = false;
    }
    if args.since != () {
        since = args.since;
    }
    if args.worked != () {
        worked = args.worked;
    }
}

phase("Compile");
let cjobs = [];
cjobs.push(#{
    label: "compile-gene",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Gene Grokman, Launch / Flight Director",
        "Compare Batch Learn paragraphs on 2026-08-21/22 (even with campaign: uncrewed) vs 2026-08-23/24 log lines that say Not Learn (uncrewed). Job card Learn section: stamp only when ops next hired you; uncrewed miss is not Learn. T-081 go yes campaign uncrewed. Did he stamp payload.learn on T-081? Count learn: in Return vs tickets stamp.",
        "- .grok/agents/gene.md (Learn + Return)\n- docs/crew/log/gene.md (grep Batch Learn, Not Learn, campaign, payload.learn)\n- docs/program/tickets/BOARD.md T-081\n- docs/program/tickets/head.json T-081 payload (go, campaign, learn, cli)\n- docs/program/OPS.md needs_learn / Learn\n- docs/archive/reviews/ (2026-08-23 *review.md Learn blocks — sample 4)"
    , since, worked),
});
cjobs.push(#{
    label: "compile-lars",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Lars Grokman, Vehicle Systems Engineer",
        "lessons.md dated headings since 2026-08-23 vs unique type=control tickets (T-151..T-322 class). Same miss class (heading 299, Shores +0, inland slew, hop-down) with a NEW fingerprint each time. Job card forbids need_* / feedback in Return. Did he open ops --tag feedback? Named file hop_factory.py / physics_warp.py vs leftover hop.py.",
        "- .grok/agents/lars.md\n- docs/crew/log/lars.md (last 80)\n- docs/lessons.md (headings 2026-08-23)\n- docs/program/tickets/BOARD.md desk=lars\n- docs/program/tickets/fingerprints.json (count>=2 vs unique)\n- docs/program/blocks.md first 40"
    , since, worked),
});
cjobs.push(#{
    label: "compile-wernher",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Wernher Grokman, Chief Systems Engineer",
        "Open type=systems. Thin tape T-284. RSI software loop. Job card feedback door. Hire count vs Lars since 2026-08-23. Kernel files tickets.py maybe_open_rsi, review.py learn_block, ops.py needs_learn. Did systems tickets close into Practice or only code?",
        "- .grok/agents/wernher.md\n- docs/crew/log/wernher.md\n- docs/program/tickets/BOARD.md type=systems\n- tickets.py maybe_open_rsi normalize_fingerprint\n- review.py learn_block\n- ops.py needs_learn / next_actions\n- docs/program/krpc.md first 40"
    , since, worked),
});
cjobs.push(#{
    label: "compile-hank",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Hank Grokman, COO — ticket bus and after-flight tape",
        "ops next hire graph: uncrewed go=yes skips Gene Learn. attach-run + landing after CLI. RSI at count>=3. Pad occupancy vs CHARTER every-hire-leaves-a-sharper-sit. Did Hank stamp learn? Open rsi? File pad-idle? Count ops --tag feedback he opened since 2026-08-23.",
        "- .grok/agents/hank.md\n- docs/crew/log/hank.md (last 80)\n- ops.py next_actions / fly_ready / needing_go / needs_learn\n- docs/program/OPS.md sections 2 and 4.2 and Learn\n- docs/program/tickets/BRIEF.md\n- tests/test_tickets.py needs_learn / stamp_learn"
    , since, worked),
});
cjobs.push(#{
    label: "compile-shelf",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Gus Grokman + Linus Grokman (shelf vs envelope)",
        "T-318 bigger hang. T-069 FlyingHigh Forest leftover unbound while loft +0. This-hop bind last-envelope. Did +0 Forest hops change the next bind, or re-fly the same hang? Science tickets opened vs feedback. vab.md vs vehicle stamps.",
        "- .grok/agents/gus.md\n- .grok/agents/linus.md\n- docs/crew/log/gus.md (last 40)\n- docs/crew/log/linus.md (last 40)\n- docs/program/vab.md first 40\n- docs/program/science.md first 40\n- BOARD.md T-318 T-069 T-077 T-081 T-321"
    , since, worked),
});
cjobs.push(#{
    label: "compile-commander",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Jebediah Grokman, Commander (abort officer) + Katherine Flight Dynamics",
        "CLI exit ends the hop — no after-flight review. note-tech leftover. Uncrewed commander: none so parent flies. What learning the stick used to return (improve/feedback) that job cards now forbid. Katherine T-283 tape windows — did anyone read her into Learn?",
        "- .grok/agents/pilot.md\n- .grok/agents/jebediah.md\n- .grok/agents/katherine.md\n- docs/crew/log/jebediah.md (last 40)\n- docs/crew/log/katherine.md\n- docs/program/note-tech.md (last 30)\n- docs/last-flight.md if present\n- BOARD.md T-283"
    , since, worked),
});
cjobs.push(#{
    label: "compile-mortimer",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Mortimer Grokman, CEO — Practice and org RSI",
        "CHARTER RSI imperative vs OPS three clocks. Practice last-write in world-model.md. T-310 type=rsi org-time-rsi. T-053 leftover-prelaunch-ghost x3. Lock live skips org hire. Did Practice change on 2026-08-23/24 from hop tape, or only from Os letters?",
        "- .grok/agents/mortimer.md\n- docs/crew/log/mortimer.md\n- docs/crew/mortimer.md\n- docs/program/CHARTER.md RSI paragraph\n- docs/program/world-model.md Practice\n- docs/program/slate.md\n- BOARD.md type=rsi type=org T-310 T-053"
    , since, worked),
});
cjobs.push(#{
    label: "compile-learn-surfaces",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "Learning surfaces (tickets, fingerprints, reviews, feedback tags)",
        "COUNT on disk, do not vibe. (1) fly tickets with payload.learn set vs empty (T-081 vs closed T-013). (2) docs/archive/reviews/ 2026-08-23 files whose Learn block is only the template Stamp payload.learn. (3) board.jsonl ops --tag feedback and type=rsi opens since 2026-08-22. (4) fingerprints.json: how many stems have count>=2 vs count==1; any >=3. (5) gene log Not Learn vs Batch Learn counts. (6) lessons.md 2026-08-23 heading count vs unique fingerprints opened that day.",
        "- docs/program/tickets/head.json (grep learn / campaign)\n- docs/program/tickets/fingerprints.json\n- docs/program/tickets/BOARD.md (type=rsi, tag feedback, tag ask)\n- docs/program/tickets/board.jsonl (grep type rsi, tag feedback — sample)\n- review.py learn_block\n- tickets.py needs_learn maybe_open_rsi normalize_fingerprint\n- docs/program/org-flow index note: RSI is a fingerprint count not a paragraph"
    , since, worked),
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
    label: "friction-learn",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Why the learning loop went quiet after 2026-08-22",
        "SPECIAL INTEREST (Os). Verify on disk, drop if false: (1) tickets.needs_learn is false when campaign=uncrewed so ops next never hires Gene for Learn on T-081. (2) review.py learn_block only appends Stamp payload.learn — no auto stamp. (3) gene.md job card Uncrewed miss is not Learn / stamp only when ops next hired you — this is the rsi-jump regression vs 08-21/22 Batch Learn on uncrewed. (4) Commander after-flight banned; Hank landing is numbers not a paragraph. (5) lessons.md grows per miss but does not stamp fly payload.learn or reuse fingerprints. Name the cheapest path that would actually run during uncrewed without a 15 min Gene novel.",
        compile_digest
    ),
});
fjobs.push(#{
    label: "friction-rsi",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "RSI clocks never trip because fingerprints do not reuse",
        "OPS.md: open increments fingerprints.json; count>=3 opens type=rsi. normalize_fingerprint drops abort novels >80 chars. Count how many stems are count==1. heading-never-090 is 2. Unique per-hop stems (T-322, flyinghigh-lid-18km-hop) are the anti-pattern. Job cards say --fingerprint <stem> but desks invent a new stem per ticket. rsi_loop software vs org. Lock live skips Mortimer. T-310 opened by Hank letter, not by x3.",
        compile_digest
    ),
});
fjobs.push(#{
    label: "friction-feedback",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Feedback door is tickets-only and almost unused",
        "PROTOCOL/job cards: do not emit ask/improve/feedback as Return keys; body may tickets open --type ops --tag feedback. Count actual tag=feedback and tag=ask tickets. CHARTER stumble-to-ticket vs two feedback tags in the whole board. Comms pain: desks cannot tell another desk in Return prose; ops --tag ask is the relay — is it used? world-model Open questions vs tickets. note-tech leftover.",
        compile_digest
    ),
});
fjobs.push(#{
    label: "friction-pad",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Pad occupancy doctrine vs CHARTER RSI imperative",
        "CHARTER: every hire leaves a sharper sit, a pitfall, a question, or code. OPS/job cards: an RSI letter does not empty the pad; do not take 15 min after a miss to write a novel; uncrewed miss is leftover + live-file patch + re-fly, not Learn. I-016 pad idle. Result: the fly string runs and the house does not rewrite itself. Quote both. A patch must keep pad occupancy AND leave a sharper sit that the NEXT hop actually reads (desk field, stamp, fingerprint reuse, auto-learn) — not a speech.",
        compile_digest
    ),
});
fjobs.push(#{
    label: "friction-comms",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Current comms pain and hire-graph leftovers",
        "Who still re-reads BOARD.md / jsonl / world-tech-parts despite packet=desk+BRIEF+ticket. Gene still last-writes plan.md/briefing. Dual science.md. Katherine hired? Verena? Parent AGENTS still from-need shim. Wernher vs Lars named-file miss. Token tax per hire. What already works (packet skim, attach-run, landing envelope, systems batch on needing_go) — do not re-fix rsi-jump wins.",
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
sim += "T-081 fly go=yes campaign=uncrewed python main.py hop. T-318 bigger hang capable. ";
sim += "Bank 8.7721, stability 18 needs ~9.23. Last hops 21-46-20Z / 21-53-04Z / 22-33-35Z sci +0. ";
sim += "22-33-35Z FlyingHigh lid abort apo 1.6 km never 50 km. Gene log: Not Learn (uncrewed). ";
sim += "Review Learn blocks say Stamp payload.learn. Fingerprints mostly count=1. ";
sim += "Two ops --tag feedback tickets in the whole board. T-310 rsi org-time-rsi from an Os letter. ";
sim += "Pad occupancy standing. Idle pad is a sin. RSI letter does not empty the pad.";

let ijobs = [];
ijobs.push(#{
    label: "talk-gene",
    agent_type: "gene",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Gene Grokman",
        "Launch / Flight Director",
        "T-081 — why Learn is none on an uncrewed string that has flown a dozen +0 hops",
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
        "lessons.md vs fingerprints — same Shores +0 class, new T-id each miss",
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
        "needs_learn / review learn_block / maybe_open_rsi — kernel that never fires during uncrewed",
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
        "ops next after CLI: attach-run + landing, then re-fly. Where does the house learn?",
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
        "T-069 FlyingHigh leftover unbound while loft +0 — did the envelope change the next bind?",
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
        "CHARTER RSI vs uncrewed skip-Learn. Practice last-write. T-310. How the house RSI itself.",
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
design_p += "You are Mortimer Grokman, CEO, designing a BOUNDED learn/RSI jump for Os. ";
design_p += "Do not edit. Do not fly. Read tickets.py needs_learn stamp_learn maybe_open_rsi normalize_fingerprint, ";
design_p += "review.py learn_block, ops.py next_actions (needs_learn / uncrewed), .grok/agents/gene.md Learn, ";
design_p += "docs/program/OPS.md RSI clocks, CHARTER RSI paragraph, world-model Practice, BRIEF.md.\n";
design_p += "Os (Founder): the last day the agents did not really learn. Feedback that existed went through tickets and was not enough. ";
design_p += "Rethink how the house learns and RSI itself. Keep pad occupancy. Do not restore 15 min Gene novels between uncrewed hops. ";
design_p += "Compile comms pain too — fix real current-org friction, not 2026-08-22 rsi-jump leftovers already applied.\n";
design_p += "Hard caps: no new TYPES zoo (at most one ops tag; prefer reuse learn / feedback / rsi). ";
design_p += "No hop.py/hop_factory.py/physics_warp.py/pad.py retune. No CHARTER creed rewrite. ";
design_p += "protocol fly fallback to plan.md stays. Gene only stamps go. Depth 1. Uncrewed campaign stays (pad occupancy). ";
design_p += "A learning path MUST actually run during campaign=uncrewed. Fingerprint stems MUST be reusable. ";
design_p += "Feedback MUST be cheaper than remember to tickets open in the body. ";
design_p += "CHARTER every-hire-leaves-a-sharper-sit MUST have a kernel or job-card mechanism the next hop reads — not a speech.\n";
design_p += "Verify these hypotheses on disk, drop if false:\n";
design_p += "1. needs_learn is false for uncrewed so Gene is never hired to stamp learn on T-081.\n";
design_p += "2. review.py only writes a Stamp payload.learn template; nobody auto-stamps.\n";
design_p += "3. fingerprints.json is almost all count=1; x3 never fires from hop misses.\n";
design_p += "4. ops --tag feedback is almost unused (job cards forbade Return keys).\n";
design_p += "5. gene.md after rsi-jump forbids Learn on uncrewed even when Gene is hired for go.\n";
design_p += "6. Practice/Mortimer are not hired during the uncrewed fly string (lock live skips org).\n";
design_p += "Prior (clipped, untrusted):\nCOMPILE:\n";
design_p += compile_digest;
design_p += "\nFRICTION:\n";
design_p += friction_digest;
design_p += "\nINTERVIEWS:\n";
design_p += talk_digest;
design_p += "\nWrite markdown:\n";
design_p += "## Summary (12 lines max)\n## Why learning died (then vs now)\n## Comms pain still live\n";
design_p += "## Learn path that runs during uncrewed (Hank auto-stamp vs Nth +0 Gene vs Return one-liner kernel-files — pick ONE primary)\n";
design_p += "## Fingerprints (reuse rule, what the kernel should reject)\n";
design_p += "## Feedback door (cheap enough desks actually do it)\n";
design_p += "## Patches (max 8 rows: file | change | owner wernher|mortimer|hank | why | learn win)\n";
design_p += "## Tickets to open now (max 5, type/desk/title/fingerprint)\n## Do not touch\n";

let design_r = agent(design_p, #{
    label: "design-learn",
    agent_type: "mortimer",
    capability_mode: "read-only",
});
let design_text = text_of(design_r);
if design_text == "" {
    design_text = "DESIGN EMPTY — do not apply. Keep walls. Re-read tickets.py needs_learn and review.py learn_block.";
}
log("design done");
let _dscratch = write_scratch_file("learn-rsi-design.md", design_text);
let design_json = json_encode(clip(design_text, 8000));

let design_ok = false;
if design_r != () {
    if design_r.success == true {
        if design_text != "" {
            if design_text != "DESIGN EMPTY — do not apply. Keep walls. Re-read tickets.py needs_learn and review.py learn_block." {
                design_ok = true;
            }
        }
    }
}
if apply_edits == true {
    if design_ok != true {
        apply_edits = false;
        log("design empty or failed — report only, no apply");
    }
}

if apply_edits != true {
    phase("Report");
    let rep = walls();
    rep += "Do not write live docs/program/learn-rsi.md. Report via write_scratch_file only. Title: Learn/RSI (compile, no apply).\n";
    rep += "Sections: 1 Sit 2 Then vs now 3 Why learning died 4 Comms pain 5 RSI clocks 6 Design (verbatim patches table) 7 Tickets opened 8 What we did not change.\n";
    rep += "Open at most 5 tickets via python main.py tickets open (type=rsi / ops --tag feedback or learn / systems). ";
    rep += "Do not duplicate titles already on BOARD.md. Do not Hangar. Do not edit .py.\n";
    rep += "DESIGN:\n";
    rep += design_json;
    rep += "\nCOMPILE:\n";
    rep += compile_digest;
    rep += "\nFRICTION:\n";
    rep += friction_digest;
    rep += "\nTALKS:\n";
    rep += talk_digest;
    let report_r = agent(rep, #{
        label: "report-audit",
        agent_type: "mortimer",
        capability_mode: "read-write",
    });
    let report = text_of(report_r);
    if report == "" { report = design_text; }
    let scratch = write_scratch_file("learn-rsi.md", report);
    complete(#{
        path: scratch,
        apply: false,
        compile_slots: ci,
        friction_slots: fi,
        interview_slots: ti,
        design_ok: design_ok,
    });
}

await_user(
    "user",
    "Learn/RSI design is in the run scratch (learn-rsi-design.md). Resume to apply bounded patches: uncrewed learn path, fingerprint reuse, cheap feedback door, job cards, Practice. No fly, no CHARTER creed, no hop.py. Stop the run if you only wanted the review."
);

phase("Apply");
let k_p = walls();
k_p += "You implement the KERNEL slice of the learn/RSI jump in /home/os/gits/ksp_stuff. Isolation none. ";
k_p += "Allowlist .py only: tickets.py ops.py protocol.py desk.py review.py and tests/test_tickets.py tests/test_protocol.py tests/test_protocol_gate.py tests/test_desk.py tests/test_review.py if present.\n";
k_p += "DESIGN:\n";
k_p += design_json;
k_p += "\nDO, if the design confirmed them on disk:\n";
k_p += "1. Uncrewed learn path that actually runs: prefer Hank/kernel auto-stamp payload.learn from the review/landing envelope after CLI (does not hire Gene, does not idle the pad). ";
k_p += "Do not hire Gene between uncrewed hops. If you add a Gene Learn hire it must be campaign-stop or Nth sci-unchanged only, and must not steal fly_ready.\n";
k_p += "2. Fingerprints: reject or do not count unique-per-hop novels; prefer short reusable stems. maybe_open_rsi must be able to fire on real repeats. Do not open rsi on every hop.\n";
k_p += "3. Feedback door: one cheap kernel or CLI helper so desks do not have to remember a body sentence (from-feedback or Return key the parent shims). At most one new ops tag. from-need stays as shim.\n";
k_p += "4. Tests for needs_learn / auto-learn / fingerprint reuse / any hire-graph change. source .venv/bin/activate. Match style. Short comments.\n";
k_p += "5. Do not retune vehicle control. Do not brick protocol fly fallback. Do not add a TYPE zoo. Do not restore Gene as merge bus.\n";
k_p += "Return files changed and test result.\n";

let k_r = agent(k_p, #{
    label: "impl-kernel",
    capability_mode: "all",
    agent_type: "wernher",
});
log("kernel implementer done");
let k_text = clip(text_of(k_r), 4000);

let cards_p = walls();
cards_p += "Edit job cards so learning and feedback actually happen. Files: .grok/agents/gene.md wernher.md lars.md hank.md linus.md gus.md mortimer.md pilot.md katherine.md and docs/program/tickets/BRIEF.md.\n";
cards_p += "DESIGN:\n";
cards_p += design_json;
cards_p += "\nKERNEL:\n";
cards_p += k_text;
cards_p += "\nDO: Gene: uncrewed is still not a 15 min novel; a one-line learn stamp (or accept Hank auto-stamp) MUST exist so the next hop reads it. ";
cards_p += "Reuse fingerprint stems (heading-never-090, sci-unchanged-living-recover, flyinghigh-lid) — do not invent a new stem per T-id. ";
cards_p += "Feedback: the cheap door the kernel just grew; still no need_* in Return fences. ";
cards_p += "Hank: after attach-run/landing, the learn path runs; RSI letter still does not empty the pad. ";
cards_p += "Lars: lessons.md heading MUST name the reusable fingerprint. Mortimer: Practice last-write from rsi tickets, not only Os letters. ";
cards_p += "Do not rewrite portraits or CHARTER. Do not edit .py.\n";

let docs_p = walls();
docs_p += "Edit house prose: docs/program/PROTOCOL.md (Learn during uncrewed, fingerprint reuse, feedback door), ";
docs_p += "AGENTS.md When-to-spawn (do not hire Gene as merge; do not skip the uncrewed learn path), ";
docs_p += "docs/program/OPS.md RSI clocks + Learn paragraph if they lie, ";
docs_p += "docs/program/world-model.md Practice (one dated pitfall: uncrewed skip-Learn), BRIEF.md one short note.\n";
docs_p += "DESIGN:\n";
docs_p += design_json;
docs_p += "\nKERNEL:\n";
docs_p += k_text;
docs_p += "\nKeep depth 1, one writer, Gene only go, crash UI honest, desk.md sit object, f013, pad occupancy. ";
docs_p += "Do not paste OPS into AGENTS. Do not edit CHARTER creed. Do not Hangar. Do not edit tickets.py.\n";

let apply_panel = parallel([
    #{
        label: "impl-job-cards",
        capability_mode: "read-write",
        prompt: cards_p,
    },
    #{
        label: "impl-docs",
        agent_type: "mortimer",
        capability_mode: "read-write",
        prompt: docs_p,
    },
]);
log("cards+docs done");

phase("Verify");
let test_p = "";
test_p += "In /home/os/gits/ksp_stuff: source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk tests.test_world -q\n";
test_p += "If tests.test_review exists, include it. If the learn/RSI cutover broke tests, FIX tests or kernel to match the bounded design. ";
test_p += "Do not weaken f013 or empty-card wait. Do not fly. Quote failures then re-run.\n";
let test_r = agent(test_p, #{
    label: "verify-unittests",
    capability_mode: "all",
});

let sk_over = walls();
sk_over += "Adversarial: did this jump overscope? real=true only if we added a TYPE zoo, edited hop.py/hop_factory.py/physics_warp.py, deleted protocol fly fallback, ";
sk_over += "ticketed CHARTER/portraits/lessons, hired Gene between uncrewed hops, or hired two kRPC writers. Else real=false with path evidence. git diff + DESIGN.\n";
sk_over += design_json;
sk_over += "\nKERNEL:\n";
sk_over += k_text;

let sk_gap = walls();
sk_gap += "Adversarial: did we fail the jump? real=true if campaign=uncrewed still has NO learn path that actually runs (Gene not hired AND no auto-stamp AND review still only a template), ";
sk_gap += "OR fingerprints still count unique-per-hop novels equally, OR feedback is still only a job-card body sentence with no kernel/CLI, ";
sk_gap += "OR gene.md still says stamp learn only when ops next hired you with no replacement. Evidence path:line. Else real=false.\n";
sk_gap += design_json;

let skeptics = parallel([
    #{
        label: "skeptic-overscope",
        capability_mode: "read-only",
        prompt: sk_over,
    },
    #{
        label: "skeptic-gap",
        capability_mode: "read-only",
        prompt: sk_gap,
    },
]);

phase("Report");
let rep2 = walls();
rep2 += "Do not write live docs/program/learn-rsi.md. Report via write_scratch_file only. Title: Learn/RSI (applied).\n";
rep2 += "Sections: 1 Sit 2 Then vs now (08-21 Learn vs 08-23 silence) 3 Why it died 4 Design 5 Files changed 6 Tests 7 Skeptics 8 Tickets opened 9 Still markdown and why 10 Open risks.\n";
rep2 += "Open at most 5 tickets for leftover work (rsi/ops/systems). Do not duplicate BOARD titles. Append one line to docs/crew/log/mortimer.md.\n";
rep2 += "DESIGN:\n";
rep2 += design_json;
rep2 += "\nKERNEL:\n";
rep2 += k_text;
rep2 += "\nCARDS:\n";
rep2 += json_encode(clip(text_of(apply_panel[0]), 2500));
rep2 += "\nDOCS:\n";
rep2 += json_encode(clip(text_of(apply_panel[1]), 2500));
rep2 += "\nTESTS:\n";
rep2 += json_encode(clip(text_of(test_r), 2000));
rep2 += "\nSKEPTICS:\n";
rep2 += json_encode(clip(text_of(skeptics[0]), 1500));
rep2 += "\n";
rep2 += json_encode(clip(text_of(skeptics[1]), 1500));
rep2 += "\nCOMPILE:\n";
rep2 += compile_digest;
rep2 += "\nFRICTION:\n";
rep2 += friction_digest;
rep2 += "\nTALKS:\n";
rep2 += talk_digest;

let report2 = agent(rep2, #{
    label: "report-applied",
    agent_type: "mortimer",
    capability_mode: "read-write",
});
let report_t = text_of(report2);
if report_t == "" { report_t = design_text; }
let scratch2 = write_scratch_file("learn-rsi.md", report_t);
let k_ok = false;
if k_r != () { k_ok = k_r.success; }
let t_ok = false;
if test_r != () { t_ok = test_r.success; }
complete(#{
    path: scratch2,
    apply: true,
    compile_slots: ci,
    friction_slots: fi,
    interview_slots: ti,
    kernel_ok: k_ok,
    tests_ok: t_ok,
});
