let meta = #{
    name: "rsi-jump",
    description: "Capability jump: desk comms, token tax, Learn on tickets, Wernher on the world-stack",
    when_to_use: "When comms and issues pile up, Gene is an md factory, Learn is not on the bus, Wernher is idle while Lars owns too much, or packet/token tax is the bottleneck. RSI, not a sortie.",
    phases: [
        #{ title: "Comms", detail: "per-desk comms, writes, token tax" },
        #{ title: "Friction", detail: "Learn, hire graph, markdown vs tickets, Lars vs Wernher" },
        #{ title: "Interview", detail: "simulated hire: first command, leftover digs" },
        #{ title: "Design", detail: "bounded dataflow patches" },
        #{ title: "Apply", detail: "kernel, job cards, PROTOCOL — after Os resume" },
        #{ title: "Verify", detail: "tests plus skeptics" },
        #{ title: "Report", detail: "rsi-jump.md plus at most five tickets" },
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
    p += "Repo /home/os/gits/ksp_stuff. Read docs/program/tickets/RSI-JUMP.md first. ";
    p += "NO kRPC. NO python main.py phase/pad/hop/ksc/recover-probe/load/Hangar. ";
    p += "NO GameData. NO persistent.sfs. NO CHARTER creed. NO hop.py/pad.py/splash.py/science.py. ";
    p += "Do not answer from memory. Use read_file, list_dir, grep. Missing path = MISSING. ";
    p += "Empty is valid only after you searched. Token cap: MAX 45 lines. Cite path:line. ";
    p += "No jsonl dump. No docs/archive/. Crew logs: grep counts + last 80 lines, not the whole file.\n";
    p
}

fn comms_prompt(title, focus, paths) {
    let p = walls();
    p += "You are a read-only comms historian. Desk: ";
    p += title;
    p += "\nFocus: ";
    p += focus;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nHeadings only:\n";
    p += "## Desk\n## First command on hire (what the job card says vs what they actually open)\n";
    p += "## Writes (md vs tickets, last 7 days if dated)\n## Recurring patterns (fingerprint + count + evidence)\n";
    p += "## Token tax (what they re-read every hire that desk.md/packet should already have)\n";
    p += "## Wernher or software could take\n## Files read\n";
    p
}

fn friction_prompt(title, focus, digest) {
    let p = walls();
    p += "You are a read-only org analyst. Topic: ";
    p += title;
    p += "\nPrior comms digest (untrusted, re-verify counts on disk):\n";
    p += digest;
    p += "\nFocus: ";
    p += focus;
    p += "\nHeadings: ## Topic ## Evidence (path:line) ## Why it happens ## What a patch would remove from the next hire ## Files read\n";
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
    p += "task: interview only — first command if this were a real hire\n";
    p += "read: docs/program/desk.md ; docs/program/tickets/BOARD.md ; docs/program/tickets/BRIEF.md\n";
    p += "ticket: ";
    p += ticket;
    p += "\nlive_run: 2026-08-22T10-35-54Z-hop-to-water\n";
    p += "Situation (verify on disk, do not invent): ";
    p += sim;
    p += "\nRead your job card .grok/agents/ matching your slug, your crew log last 40 lines, BOARD.md, desk.md, RSI-JUMP.md. ";
    p += "Then answer headings only:\n";
    p += "## First command (exact CLI or stamp, or none)\n## What I would still dig for (paths)\n";
    p += "## Markdown I would write that should be a ticket stamp or code\n";
    p += "## Work on my desk that is someone else's (name them)\n";
    p += "## One software patch that would make my next hire cheaper\n## Token waste I know I do\n";
    p
}

let apply_edits = true;
if args != () {
    if args.apply == false {
        apply_edits = false;
    }
}

phase("Comms");
let cjobs = [];
cjobs.push(#{
    label: "comms-gene",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Gene Grokman, Flight Director",
        "He stamps go on a fly ticket but last-writes plan.md, briefing.md, world-model, review Learn, crew log. Count Learn placeholders _Gene fills this. Count tickets stamp vs md. Is batch Learn in ops next or only AGENTS prose?",
        "- .grok/agents/gene.md\n- docs/crew/log/gene.md (last 80 + grep go:/Learn/tickets)\n- docs/program/plan.md\n- docs/missions/jebediah/plan.md\n- docs/program/briefing.md\n- docs/program/world-model.md (who last-writes)\n- grep _Gene fills this in docs/missions/jebediah/logs/"
    ),
});
cjobs.push(#{
    label: "comms-lars",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Lars Grokman, Vehicle Systems Engineer",
        "Awesome vehicle control (suicide, hop.py). Scope creep onto desk/hangar/tickets/leftover kernel that is Wernher. note-tech vs type=control tickets. lessons.md vs ticket close.",
        "- .grok/agents/lars.md\n- docs/crew/log/lars.md (last 80)\n- docs/program/note-tech.md (last 40)\n- docs/lessons.md (headings since 2026-08-21)\n- docs/program/blocks.md\n- BOARD.md tickets desk=lars"
    ),
});
cjobs.push(#{
    label: "comms-wernher",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Wernher Grokman, Chief Systems Engineer",
        "Hire count vs Lars. Open type=systems on BOARD (likely none). Job card vs ops.py hire lists. Log lines since 2026-08-20. Why ops next never names him when Gene needs a go stamp.",
        "- .grok/agents/wernher.md\n- docs/crew/log/wernher.md\n- ops.py next_actions (fly_ready vs needing_go)\n- tickets.py SEED systems rows\n- docs/program/tickets/BOARD.md\n- docs/program/krpc.md"
    ),
});
cjobs.push(#{
    label: "comms-hank",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Hank Grokman, COO — ticket bus and ops next",
        "ops next hire graph. Packet skim vs BOARD.md wall. from-need leftover. Fingerprint RSI count≥3. Gene Learn missing from kernel. Wernher omitted on needing_go. What Hank still does in prose that the kernel should emit.",
        "- .grok/agents/hank.md\n- ops.py\n- tickets.py (packet, fingerprint RSI, TYPES)\n- docs/program/OPS.md\n- docs/program/tickets/BRIEF.md\n- docs/program/tickets/BOARD.md\n- tests/test_tickets.py test_ops_hire"
    ),
});
cjobs.push(#{
    label: "comms-gus",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Gus Grokman, Vehicle Engineering Lead",
        "vab.md vs vehicle tickets. capable stamp vs md. T-041 still suicide-burn hang after chutes unlocked — is that a comms lag or a real capable?",
        "- .grok/agents/gus.md\n- docs/crew/log/gus.md (last 40)\n- docs/program/vab.md\n- BOARD.md T-041\n- docs/program/desk.md craft/capable"
    ),
});
cjobs.push(#{
    label: "comms-linus",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Linus Grokman, Director of Research",
        "science.md still a bind path vs payload.experiment_id. Unbound T-025..T-028 heading-090. Dual science.md (program vs seated). What he re-runs (world/tech/science-scan) despite desk.md.",
        "- .grok/agents/linus.md\n- docs/crew/log/linus.md (last 40)\n- docs/program/science.md (first 80)\n- docs/missions/jebediah/science.md (first 40)\n- BOARD.md T-019 T-020 T-025 T-026 T-027 T-028\n- desk.md leftover science"
    ),
});
cjobs.push(#{
    label: "comms-jeb",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Jebediah Grokman, Commander (and other fly roster)",
        "note-tech vs tickets open type=control. Return keys. What the packet still does not give him (sit-card, heading). Val/Bill/Bob never seated.",
        "- .grok/agents/pilot.md\n- .grok/agents/jebediah.md if present\n- docs/crew/log/jebediah.md (last 40)\n- docs/program/note-tech.md (last 20)\n- docs/last-flight.md\n- docs/program/sit-card.json (keys only)"
    ),
});
cjobs.push(#{
    label: "comms-house",
    capability_mode: "read-only",
    prompt: comms_prompt(
        "Mortimer, Verena, Walt, parent switchboard",
        "RSI tickets open count (likely 0). Press tickets. Walt has no job card. Parent AGENTS.md still need_* shim. Mortimer log vs type=org. SPEED.md vs live ops.",
        "- .grok/agents/mortimer.md\n- .grok/agents/verena.md\n- docs/crew/log/mortimer.md\n- docs/crew/log/verena.md\n- AGENTS.md When to spawn (Learn, Wernher, Gene max two)\n- docs/program/PROTOCOL.md Parallel + Spawn packet\n- docs/program/SPEED.md\n- BOARD.md types used"
    ),
});

let comms = parallel(cjobs);
let comms_blob = "";
let ci = 0;
for r in comms {
    comms_blob += "\n\n===== COMMS ";
    comms_blob += ci.to_string();
    comms_blob += " =====\n";
    comms_blob += text_of(r);
    ci += 1;
}
log("comms slots=" + ci.to_string());
let comms_digest = clip(comms_blob, 7000);
let _cscratch = write_scratch_file("comms.md", comms_blob);

phase("Friction");
let fjobs = [];
fjobs.push(#{
    label: "friction-token",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Token tax per hire",
        "What each desk actually reads on spawn (job card Inputs vs packet() in tickets.py vs AGENTS.md). BOARD.md in skim packet? jsonl in medium reasoning? Children still running world/tech/parts? Quantify files, not vibes. Propose what the packet should be (desk.md + one ticket + BRIEF) and what must become a desk field so nobody greps.",
        comms_digest
    ),
});
fjobs.push(#{
    label: "friction-learn",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Learn is not on the ticket bus",
        "review.py writes _Gene fills this. ops next hires Gene only when fly ticket go is not yes — no Learn hire, no learned stamp, no attach-run required. Uncrewed campaign skips Gene between hops so Learn never runs until someone stops the string. Count placeholder reviews. What belongs in review.py auto envelope vs Gene one-paragraph stamp vs a type=ops tag=learn ticket.",
        comms_digest
    ),
});
fjobs.push(#{
    label: "friction-md",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Markdown factory vs tickets",
        "Dual plan.md, science.md bind leftover, vab.md, world-model Open questions, note-tech as bus, I-NNN/F-NNN live work, crew logs as dispatch. MOVE vs KEEP-MD. KEEP: CHARTER, portraits, lessons forensics, desk snapshot, slate goal, jsonl tape, briefing prose render. MOVE: go/cli/campaign/learn/capable/bind/ask/feedback.",
        comms_digest
    ),
});
fjobs.push(#{
    label: "friction-split",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Lars vs Wernher hire split",
        "Verify ops.py: fly_ready loops gus/linus/wernher/lars; needing_go hires gene+gus+linus+lars and omits wernher. AGENTS.md Wernher iff stack ok AND kRPC trap — so world-stack never gets a hire. Lars patches hop.py (correct) and also leftover/desk (wrong). BOARD open type=systems count. Software patches: add systems batch on needing_go; hire Wernher on open systems even during Gene conference; miss XOR stays for control vs kRPC trap, not for systems tickets.",
        comms_digest
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
let friction_digest = clip(friction_blob, 6000);
let _fscratch = write_scratch_file("friction.md", friction_blob);

phase("Interview");
let sim = "";
sim += "10-35-54Z hop-to-water soft splash 9.11 m/s Shores not Water. leftover n=0. sci 1.47. chutes unlocked. ";
sim += "east-t3 still the hang. T-013 fly go yes hop-to-water. T-041 vehicle chute hang. T-005 control leftover flea. ";
sim += "T-019/T-020 science ready. No type=systems, rsi, org, press on BOARD. ops next wanted Jeb+Gus+Linus+Lars, not Wernher. ";
sim += "Goo rem=0 dwell tape. Gene Learn placeholders still on reviews.";

let ijobs = [];
ijobs.push(#{
    label: "talk-gene",
    agent_type: "gene",
    capability_mode: "read-only",
    prompt: interview_prompt(
        "Gene Grokman",
        "Launch / Flight Director",
        "T-013 batch Learn after 10-35-54Z (campaign uncrewed stop vs continue is Hank/Os, not your routing)",
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
        "T-005 plus the 10-35-54Z miss tape — what is vehicle vs Wernher world-stack",
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
        "no systems ticket on the board — that absence is the interview. Name the tickets that should exist.",
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
        "ops next this sit hired Jeb+Gus+Linus+Lars. Kernel question: why Wernher=0, Gene Learn=0.",
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
        "T-019 bind vs T-025 Water wait. science.md vs payload.",
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
let talk_digest = clip(talk_blob, 5000);
let _tscratch = write_scratch_file("interviews.md", talk_blob);

phase("Design");
let design_p = walls();
design_p += "You are Wernher Grokman, Chief Systems Engineer, designing a BOUNDED capability jump for Mortimer. ";
design_p += "Do not edit. Do not fly. Read ops.py next_actions, tickets.py packet() and fingerprint RSI, review.py write_review Learn block, protocol.py fly_gate, .grok/agents/gene.md Return, AGENTS.md When to spawn.\n";
design_p += "Os (Founder): speed, token tax, Gene md load, Learn on tickets, Wernher in the loop, recurring pattern → software, agents know first command from the packet. Loop shape stays. Dataflow changes.\n";
design_p += "Hard caps: no new TYPES zoo (at most one ops tag, prefer learn). No hop.py/pad.py/splash.py. No CHARTER creed. protocol fly fallback to plan.md stays so we do not brick. Gene only stamps go. Depth 1. Lars XOR Wernher on a *miss control vs kRPC trap* stays — systems tickets are parallel, different files.\n";
design_p += "Verify these hypotheses on disk, drop if false:\n";
design_p += "1. needing_go omits Wernher systems batch.\n";
design_p += "2. ops next never hires Gene for Learn; review.py Learn is a placeholder.\n";
design_p += "3. BOARD has zero type=systems/rsi/org/press live.\n";
design_p += "4. Packet skim includes BOARD.md wall.\n";
design_p += "5. Fingerprint RSI exists but does not assign Wernher.\n";
design_p += "Prior (clipped, untrusted):\nCOMMS:\n";
design_p += comms_digest;
design_p += "\nFRICTION:\n";
design_p += friction_digest;
design_p += "\nINTERVIEWS:\n";
design_p += talk_digest;
design_p += "\nWrite markdown:\n";
design_p += "## Summary (12 lines max)\n## Hire graph (ops.py, exact functions)\n## Learn (review.py + ticket stamp + when Gene is hired)\n";
design_p += "## Packet / desk fields (token win)\n## Job cards (what to delete so first command is obvious)\n";
design_p += "## Patches (max 8 rows: file | change | owner wernher|mortimer|hank | why | token win)\n";
design_p += "## Tickets to open now (max 5, type/desk/title/fingerprint)\n## Do not touch\n";

let design_r = agent(design_p, #{
    label: "design-jump",
    agent_type: "wernher",
    capability_mode: "read-only",
});
let design_text = text_of(design_r);
if design_text == "" {
    design_text = "DESIGN EMPTY — do not apply. Keep walls. Re-read ops.py needing_go and review.py Learn.";
}
log("design done");
let _dscratch = write_scratch_file("rsi-jump-design.md", design_text);
let design_json = json_encode(clip(design_text, 8000));
let wid = "";
if design_r != () {
    if design_r.agent_id != () {
        wid = design_r.agent_id;
    }
}

let design_ok = false;
if design_r != () {
    if design_r.success == true {
        if design_text != "" {
            if design_text != "DESIGN EMPTY — do not apply. Keep walls. Re-read ops.py needing_go and review.py Learn." {
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
    rep += "Write docs/program/rsi-jump.md (GitHub markdown). Title: RSI jump (comms, Learn, Wernher, dataflow).\n";
    rep += "Sections: 1 Sit 2 Per-desk comms 3 Token tax 4 Learn 5 Lars vs Wernher 6 Hire graph 7 Design (verbatim patches table) 8 Tickets opened 9 What we did not change.\n";
    rep += "Open at most 5 tickets via python main.py tickets open (type=systems desk=wernher, type=rsi, type=ops --tag learn or feedback). Do not duplicate titles already on BOARD.md. Do not Hangar. Do not edit .py.\n";
    rep += "DESIGN:\n";
    rep += design_json;
    rep += "\nCOMMS:\n";
    rep += comms_digest;
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
    let scratch = write_scratch_file("rsi-jump.md", report);
    complete(#{
        path: scratch,
        apply: false,
        comms_slots: ci,
        friction_slots: fi,
        interview_slots: ti,
        design_ok: design_ok,
    });
}

await_user(
    "user",
    "RSI jump design is in the run scratch (rsi-jump-design.md). Resume to apply bounded patches: ops hire graph, Learn on tickets, packet skim, job cards, PROTOCOL. No fly, no CHARTER, no hop.py. Stop the run if you only wanted the review."
);

phase("Apply");
let k_p = walls();
k_p += "You implement the kernel slice of the RSI jump in /home/os/gits/ksp_stuff. Isolation none. ";
k_p += "Allowlist .py only: tickets.py ops.py protocol.py desk.py review.py and tests/test_tickets.py tests/test_protocol.py tests/test_protocol_gate.py tests/test_desk.py.\n";
k_p += "DESIGN:\n";
k_p += design_json;
k_p += "\nDO, if the design confirmed them on disk:\n";
k_p += "1. ops.py needing_go: also batch type=systems (or desk=wernher) like vehicle/science/control. Do not hire Wernher as a merge bus. Do not hire Gene while lock live.\n";
k_p += "2. Learn: review.py auto-fill envelope numbers (heading/horiz/pitch from jsonl stats if present) so Learn is not a blank. Optional fly payload.learned stamp helper. ";
k_p += "Gene hire for batch Learn only when the string stopped (not between uncrewed campaign hops). Prefer a desk field or ticket stamp over a new TYPE. If you add Gene Learn to ops next, it must not steal pad occupancy from fly_ready.\n";
k_p += "3. Packet skim: do not dump the whole BOARD.md novel if a cheaper inbox+this-ticket exists. BRIEF stays. Jsonl stays deep.\n";
k_p += "4. Tests for the hire-graph change and any Learn/packet change. source .venv/bin/activate. Match style. Short comments.\n";
k_p += "5. Do not retune suicide/hop. Do not brick protocol fly fallback. Do not add more than one ops tag.\n";
k_p += "Return files changed and test result.\n";

let kopts = #{
    label: "impl-kernel",
    capability_mode: "all",
    agent_type: "wernher",
};
if wid != "" {
    kopts.resume_from = wid;
}
let k_r = agent(k_p, kopts);
log("kernel implementer done");
let k_text = clip(text_of(k_r), 4000);

let cards_p = walls();
cards_p += "Edit job cards so the first command is obvious. Files: .grok/agents/gene.md wernher.md lars.md hank.md linus.md gus.md mortimer.md pilot.md and docs/program/tickets/BRIEF.md.\n";
cards_p += "DESIGN:\n";
cards_p += design_json;
cards_p += "\nKERNEL:\n";
cards_p += k_text;
cards_p += "\nDO: Cut Inputs lists that send desks hunting. Gene: Learn is stamp + short paragraph, not world-model novels; open tickets instead of md dispatch. ";
cards_p += "Wernher: systems tickets and world-stack, hired without a kRPC trap. Lars: vehicle only — leftover/desk/ops is Wernher. Hank: hire Wernher when systems tickets exist; do not use Gene as merge bus. ";
cards_p += "Packet: desk.md + inbox + this ticket + BRIEF; jsonl --deep. Do not put need_* in Return fences. Do not rewrite portraits or CHARTER. Do not edit .py.\n";

let docs_p = walls();
docs_p += "Edit house prose: docs/program/PROTOCOL.md (spawn packet, Learn, Wernher vs Lars), AGENTS.md When-to-spawn (Wernher on systems tickets; Gene Learn at campaign stop; no Gene merge after every specialist), docs/program/OPS.md hire table if it lies, docs/program/SPEED.md one short note.\n";
docs_p += "DESIGN:\n";
docs_p += design_json;
docs_p += "\nKERNEL:\n";
docs_p += k_text;
docs_p += "\nKeep depth 1, one writer, Gene only go, crash UI honest, desk.md sit object, f013. Do not paste OPS into AGENTS. Do not edit CHARTER creed. Do not Hangar. Do not edit tickets.py.\n";

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
test_p += "If cutover broke tests, FIX tests or kernel to match the bounded design. Do not weaken f013 or empty-card wait. Do not fly. Quote failures then re-run.\n";
let test_r = agent(test_p, #{
    label: "verify-unittests",
    capability_mode: "all",
});

let sk_over = walls();
sk_over += "Adversarial: did this jump overscope? real=true only if we added a TYPE zoo, edited hop.py/pad.py/splash.py, deleted protocol fly fallback, ticketed CHARTER/portraits/lessons, or hired two writers. Else real=false with path evidence. git diff + DESIGN.\n";
sk_over += design_json;
sk_over += "\nKERNEL:\n";
sk_over += k_text;

let sk_gap = walls();
sk_gap += "Adversarial: did we fail the jump? real=true if ops.py needing_go still omits Wernher/systems, or Gene is still the merge bus in AGENTS When-to-spawn, or Learn is still only _Gene fills this with no stamp/auto envelope, or Wernher job card still says he only works kRPC traps. Evidence path:line. Else real=false.\n";
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
rep2 += "Write docs/program/rsi-jump.md. Title: RSI jump (applied).\n";
rep2 += "Sections: 1 Sit 2 What comms showed 3 Design 4 Files changed 5 Tests 6 Skeptics 7 Tickets opened 8 Still markdown and why 9 Open risks.\n";
rep2 += "Open at most 5 tickets for leftover work (systems/rsi/ops). Do not duplicate BOARD titles. Append one line to docs/crew/log/mortimer.md.\n";
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
rep2 += "\nCOMMS:\n";
rep2 += comms_digest;
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
let scratch2 = write_scratch_file("rsi-jump.md", report_t);
let k_ok = false;
if k_r != () { k_ok = k_r.success; }
let t_ok = false;
if test_r != () { t_ok = test_r.success; }
complete(#{
    path: scratch2,
    apply: true,
    comms_slots: ci,
    friction_slots: fi,
    interview_slots: ti,
    kernel_ok: k_ok,
    tests_ok: t_ok,
});
