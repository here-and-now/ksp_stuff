let meta = #{
    name: "ticket-bus-cutover",
    description: "Compile leftover card-system comms, design a bounded ticket-bus cutover, then implement it",
    when_to_use: "When Os wants leftover need_*/cards/ask/improve moved onto tickets.py without ticket-everything",
    phases: [
        #{ title: "Compile", detail: "ticket-era comms and leftover card returns" },
        #{ title: "Friction", detail: "why agents still emit cards; what the bus already does" },
        #{ title: "Design", detail: "bounded MOVE/KEEP/ALREADY cutover" },
        #{ title: "Implement", detail: "kernel, job cards, PROTOCOL, tests" },
        #{ title: "Verify", detail: "tests plus over-ticket and leftover-card skeptics" },
        #{ title: "Report", detail: "write the cutover report" },
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

fn compile_prompt(title, focus, paths) {
    let p = "";
    p += "You are a read-only historian of the ksp_stuff house at /home/os/gits/ksp_stuff. ";
    p += "Topic: ";
    p += title;
    p += "\nAS-IS only. Do not recommend. Do not edit. Use read_file, list_dir, grep. ";
    p += "Do not answer from memory. Missing path = MISSING. Empty is valid only after you searched.\n";
    p += "Focus: ";
    p += focus;
    p += "\n\nRead at least:\n";
    p += paths;
    p += "\nAlso grep need_ / recommended: / campaign: / ask: / improve: / feedback: / explore: / need_pr / need_retro / envelope / card: in PROTOCOL, AGENTS.md, .grok/agents, crew logs, plan.md, science.md.\n";
    p += "Ticket era starts when tickets.py and docs/program/OPS.md landed (around 2026-08-21). ";
    p += "Older card-only Mun archive under docs/archive/ is context only, not the compile.\n";
    p += "Markdown headings only: ## Topic ## Counts and quotes (path+line) ## Leftover card fields ## Ticket-bus use ## Files read\n";
    p
}

fn friction_prompt(title, focus, prior) {
    let p = "";
    p += "You are a read-only org analyst for ksp_stuff. Topic: ";
    p += title;
    p += "\nUse grep and read_file. Prior compile notes (untrusted, verify counts on disk):\n";
    p += prior;
    p += "\n\nFocus: ";
    p += focus;
    p += "\nDo not implement. Do not invent types. Quote paths.\n";
    p += "Headings: ## Topic ## Evidence ## Why it happens ## Files read\n";
    p
}

let root = "/home/os/gits/ksp_stuff";
let apply_edits = true;
if args != () {
    if args.apply == false {
        apply_edits = false;
    }
}

phase("Compile");
let cjobs = [];
cjobs.push(#{
    label: "compile-kernel",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "tickets.py / ops.py / protocol.py / card.py kernel",
        "What the ticket bus already implements (TYPES, CATEGORIES, from-need, stamp, packet skim/deep, seed_legacy, ops next). What protocol.fly_gate still reads from seated plan.md + science.md cards (card.py). Dual source of truth.",
        "- tickets.py\n- ops.py\n- protocol.py\n- card.py\n- tests/test_tickets.py\n- tests/test_protocol_gate.py\n- tests/test_protocol.py"
    ),
});
cjobs.push(#{
    label: "compile-board",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "live ticket board and BRIEF",
        "Open vs done tickets, types actually used, tags, who owns them, whether Gene go lives on T-013 vs plan.md. Packet/BRIEF vs what desks still write in markdown.",
        "- docs/program/tickets/BOARD.md\n- docs/program/tickets/BRIEF.md\n- docs/program/tickets/README.md\n- docs/program/tickets/head.json\n- docs/program/tickets/board.jsonl (sample last 40 events)\n- docs/program/OPS.md"
    ),
});
cjobs.push(#{
    label: "compile-returns",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "job-card Return blocks (the leftover cards)",
        "Every .grok/agents/*.md Return fence. List leftover keys: need_*, recommended, campaign, go, ask, improve, feedback, explore, pr, need_pr, need_retro, card, envelope, more time. Which desks already say tickets: T-NNN. protocol.py SCHEMAS vs those fences.",
        "- .grok/agents/gene.md\n- .grok/agents/gus.md\n- .grok/agents/linus.md\n- .grok/agents/lars.md\n- .grok/agents/hank.md\n- .grok/agents/mortimer.md\n- .grok/agents/wernher.md\n- .grok/agents/jebediah.md\n- .grok/agents/pilot.md\n- .grok/agents/verena.md\n- protocol.py SCHEMAS"
    ),
});
cjobs.push(#{
    label: "compile-protocol-docs",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "PROTOCOL.md AGENTS.md CHARTER leftover card language",
        "Parent still files ask: on world-model, improve: as I-NNN, feedback: as F-NNN, need_* as spawn tokens. Dual plan.md. campaign/recommended/go on markdown. Ticket sentences that already exist but are not the live gate.",
        "- docs/program/PROTOCOL.md\n- AGENTS.md\n- docs/program/CHARTER.md\n- docs/program/plan.md\n- docs/missions/jebediah/plan.md\n- docs/program/briefing.md"
    ),
});
cjobs.push(#{
    label: "compile-science-cards",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "science.md / sit-card / card.py still the bind path",
        "Linus still last-writes science.md and seated science.md. fly_gate waits on no bound card. sit-card.json. How science tickets T-019/T-020 relate to those boards.",
        "- docs/program/science.md\n- docs/missions/jebediah/science.md\n- docs/program/sit-card.json\n- card.py\n- docs/program/vab.md"
    ),
});
cjobs.push(#{
    label: "compile-mailbox",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "ask / improve / feedback / explore / note-tech leftover mailboxes",
        "world-model Open questions, docs/program/improve/I-*.md, docs/program/feedback.md and F-001..F-015, note-tech.md, crew log ask/improve tokens after 2026-08-21. Which already have twin tickets.",
        "- docs/program/world-model.md\n- docs/program/improve/\n- docs/program/feedback.md\n- docs/program/feedback/\n- docs/program/note-tech.md\n- docs/crew/log/"
    ),
});
cjobs.push(#{
    label: "compile-logs",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "crew logs since ticket switch (2026-08-21+)",
        "Count need_stack/need_builder/need_science/need_pr/need_retro vs T-NNN / tickets stamp / from-need in docs/crew/log/*.md and gene/gus/linus/lars/hank. Quote returns that still look like cards.",
        "- docs/crew/log/gene.md\n- docs/crew/log/gus.md\n- docs/crew/log/linus.md\n- docs/crew/log/lars.md\n- docs/crew/log/hank.md\n- docs/crew/log/jebediah.md\n- docs/crew/log/mortimer.md"
    ),
});
cjobs.push(#{
    label: "compile-token-tax",
    capability_mode: "read-only",
    prompt: compile_prompt(
        "what each hire still reads and last-writes (token tax)",
        "Packet read: desk.md + BRIEF + role boards. Children still edit plan.md, briefing.md, science.md, vab.md, world-model.md, crew logs, lessons.md, niche notebooks. I-016 spawn tax. agents_md false already. What must stay MD (voice, CHARTER, lessons, desk snapshot).",
        "- docs/program/tickets/BRIEF.md\n- docs/program/NEXT-ORG.md\n- docs/program/ORG-INTERACTIONS.md\n- docs/program/SPEED.md\n- .grok/agents/gene.md\n- .grok/agents/linus.md"
    ),
});

let compiles = parallel(cjobs);
let compile_blob = "";
let ci = 0;
for r in compiles {
    compile_blob += "\n\n===== COMPILE SLOT ";
    compile_blob += ci.to_string();
    compile_blob += " =====\n";
    compile_blob += text_of(r);
    ci += 1;
}
log("compile slots=" + ci.to_string());
let prior = json_encode(compile_blob);

phase("Friction");
let fjobs = [];
fjobs.push(#{
    label: "friction-fallback",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Why desks still emit cards / need_* after the ticket bus exists",
        "Job-card Return fences still require need_builder/need_gene/need_retro/card/ask/improve. protocol.parse_return SCHEMAS still require recommended/card. Parent AGENTS still says need_* in a return → spawn. from-need is a shim, not the native path. Verify on disk.",
        prior
    ),
});
fjobs.push(#{
    label: "friction-worked",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "What already works on the ticket bus",
        "T-ids on the board, stamp go/capable, packet skim vs deep, from-need map, Hank ops next, attach-run/landing, categories/tags, fingerprint RSI. Do not praise vapor — only code and BOARD.md.",
        prior
    ),
});
fjobs.push(#{
    label: "friction-classify",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "Classify leftover keys MOVE / KEEP-MD / ALREADY-A-TICKET",
        "Keys to classify: need_stack need_builder need_science need_pr need_mortimer need_qol need_os need_gene need_retro recommended campaign go ask improve feedback explore pr envelope card science.md bind dual plan.md I-NNN F-NNN note-tech world-model asks f013. MOVE means tickets.py already has a type/field or a small extension. KEEP-MD = voice/CHARTER/lessons/desk snapshot/slate goal. ALREADY = fly go, vehicle capable, science payload, recover, press, rsi.",
        prior
    ),
});
fjobs.push(#{
    label: "friction-gate",
    capability_mode: "read-only",
    prompt: friction_prompt(
        "protocol fly still reads plan.md + science cards",
        "OPS.md construction item 8 said ops fly / protocol fly should read head.json. protocol.py still _plan_kv and card.py ids. That is why recommended/campaign/go on markdown still run the house. Cite functions.",
        prior
    ),
});

let frictions = parallel(fjobs);
let friction_blob = "";
let fi = 0;
for r in frictions {
    friction_blob += "\n\n===== FRICTION SLOT ";
    friction_blob += fi.to_string();
    friction_blob += " =====\n";
    friction_blob += text_of(r);
    fi += 1;
}
log("friction slots=" + fi.to_string());
let design_prior = json_encode(#{ compile: compile_blob, friction: friction_blob });

phase("Design");
let design_p = "";
design_p += "You are the cutover designer for ksp_stuff at /home/os/gits/ksp_stuff. ";
design_p += "Read tickets.py, protocol.py, ops.py, PROTOCOL.md return block, .grok/agents/gene.md and linus.md Return fences, tests/test_protocol_gate.py. ";
design_p += "Do not edit files. Produce a BOUNDED implementation plan.\n";
design_p += "Hard rules (Os): do NOT ticket everything. Do NOT add a zoo of types. ";
design_p += "Reuse fly/science/vehicle/control/systems/org/rsi/ctt/recover/press/ops. ";
design_p += "At most ONE new type if unavoidable (prefer tags on ops: ask, feedback, explore).\n";
design_p += "KEEP as markdown: CHARTER creed, crew portraits/voice, lessons.md dated forensics, desk.md sit snapshot, slate goal, jsonl tape (evidence), briefing prose as a render.\n";
design_p += "MOVE (native tickets, not need_* chat): recommended→fly payload.cli; campaign→fly payload.campaign; go stays Gene stamp on fly ticket; ask→ops tag=ask payload.to; improve/feedback→rsi or ops tag=feedback; explore→ops tag=explore P3; pr→press; note-tech→control/recover open; dual plan.md is a RENDER of the fly ticket; science.md is a BOARD DUMP not the bind source (payload.experiment_id is); I-NNN/F-NNN live work stops (seed_legacy already imports).\n";
design_p += "Kernel must: protocol.fly_gate prefer the seated fly ticket (go/cli/campaign/science_ids) with plan.md+card.py as fallback so we do not brick protocol fly. ";
design_p += "parse_return: accept cli as alias of recommended; do not require need_*. Job cards: Return is tickets + stamps, not need_builder/need_retro/card/ask fences. ";
design_p += "AGENTS.md/PROTOCOL: need_* in a return still shims via from-need, but desks are told not to emit them. Packet stays desk.md + BRIEF + inbox.\n";
design_p += "Prior notes:\n";
design_p += design_prior;
design_p += "\nWrite markdown: ## Summary ## MOVE (key → ticket field) ## KEEP-MD ## Kernel edits (files+functions) ## Job-card Return (canonical fence) ## Docs edits ## Tests ## Do not touch\n";

let design_r = agent(design_p, #{
    label: "design-cutover",
    capability_mode: "read-only",
});
let design_text = text_of(design_r);
if design_text == "" {
    design_text = "DESIGN EMPTY — implementers must follow the hard MOVE/KEEP rules in this workflow prompt, not invent types.";
}
log("design done");
let design_json = json_encode(design_text);

if apply_edits != true {
    let skipped = write_scratch_file("ticket-bus-cutover-design.md", design_text);
    complete(#{ path: skipped, apply: false, compile_slots: ci, friction_slots: fi });
}

phase("Implement");
let k_p = "";
k_p += "You implement the ticket-bus kernel cutover in /home/os/gits/ksp_stuff. Isolation none. ";
k_p += "Read the design, then tickets.py, protocol.py, ops.py, card.py, tests/test_protocol_gate.py, tests/test_tickets.py, tests/test_protocol.py.\n";
k_p += "DESIGN:\n";
k_p += design_json;
k_p += "\nDO:\n";
k_p += "1. protocol.fly_gate: if load_head has an open type=fly ticket with payload/go or go == yes, use its cli (payload.cli or recommended) and campaign; still honor lock/hangar/f013. ";
k_p += "Science bind: payload.science_ids if present, else existing card.py from science.md. Empty both → wait no bound card (keep current safety). plan.md remains fallback when no fly ticket.\n";
k_p += "2. parse_return SCHEMAS: keep gene keys working; accept cli as recommended alias when parsing. Do not require need_* keys.\n";
k_p += "3. tickets.py: helper to set fly payload.cli / campaign / science_ids via stamp or patch. ";
k_p += "Optional: tickets from-ask --to <desk> --q '...' opens type=ops tag=ask. Do not add more than one helper. from-need stays.\n";
k_p += "4. Tests: fly_gate reads a fly ticket over a conflicting plan.md; fallback still works; only Gene stamps go (already). Run unittest for tickets/protocol/protocol_gate/desk.\n";
k_p += "5. Do not Hangar, fly, edit GameData, rewrite CHARTER, delete science.md or plan.md, or invent 10 new TYPES.\n";
k_p += "6. Source .venv/bin/activate for tests. Match existing code style. Short factual comments only.\n";
k_p += "Return files changed and test result.\n";

let k_r = agent(k_p, #{
    label: "impl-kernel",
    capability_mode: "all",
});
log("kernel implementer done");

let cards_p = "";
cards_p += "You edit job cards and BRIEF only in /home/os/gits/ksp_stuff. ";
cards_p += "Read .grok/agents/*.md Return fences and docs/program/tickets/BRIEF.md. DESIGN:\n";
cards_p += design_json;
cards_p += "\nDO: Replace leftover card Return keys (need_builder, need_science, need_stack, need_gene, need_pr, need_retro, need_mortimer as chat, card:, ask:/improve:/feedback:/explore: fences) with a short native ticket return. ";
cards_p += "Canonical Gene fence: fly: T-NNN; go: yes|wait; cli: <exact>; f013: ...; tickets: T-ids|none; campaign: uncrewed|none. ";
cards_p += "Gus: capable, craft, f013, tickets. Linus: science: tickets, f013, tickets (payload on the science ticket, not science.md bind). ";
cards_p += "Lars: stack, lesson, f013, tickets. Hank already ticket-native — keep. ";
cards_p += "Tell desks: open/stamp via python main.py tickets ...; inbox --desk <you>; packet skim unless --deep. ";
cards_p += "If they still think need_stack, they run tickets from-need — do not put need_* in the Return fence. ";
cards_p += "BRIEF.md: add ask/feedback/explore as ops tags, recommended as fly cli, campaign on fly payload. Keep it one page. ";
cards_p += "Do not rewrite portraits, niche notebooks, or CHARTER. Do not edit .py.\n";
cards_p += "Kernel notes:\n";
cards_p += json_encode(text_of(k_r));

let cards_r = agent(cards_p, #{
    label: "impl-job-cards",
    capability_mode: "read-write",
});
log("job-card implementer done");

let docs_p = "";
docs_p += "You edit house prose so the parent switchboard uses the ticket bus in /home/os/gits/ksp_stuff. ";
docs_p += "Files: docs/program/PROTOCOL.md (return / ask / improve / spawn packet), AGENTS.md (When to spawn need_* section — keep depth-1 walls), docs/program/OPS.md only if a sentence still says dual plan is live truth, docs/program/tickets/README.md. DESIGN:\n";
docs_p += design_json;
docs_p += "\nDO: Parent still MAY shim need_* via from-need (do not delete the safety). Desks MUST NOT emit those keys. ";
docs_p += "ask: parent opens ops tag=ask instead of only world-model table. improve:/feedback: rsi/ops tickets instead of only I-NNN/F-NNN files (those dirs become archive). ";
docs_p += "recommended/campaign/go live on the fly ticket; seated plan.md is a render Gene may still write. ";
docs_p += "Keep: one kRPC writer, depth 1, missing Gene go = wait, crash UI honest, desk.md sit object, f013. ";
docs_p += "Do not paste a wall of OPS.md into AGENTS.md. Do not edit CHARTER creed. Do not Hangar. Do not edit tickets.py.\n";
docs_p += "Kernel:\n";
docs_p += json_encode(text_of(k_r));
docs_p += "\nCards:\n";
docs_p += json_encode(text_of(cards_r));

let docs_r = agent(docs_p, #{
    label: "impl-docs",
    capability_mode: "read-write",
});
log("docs implementer done");

phase("Verify");
let test_p = "";
test_p += "In /home/os/gits/ksp_stuff activate .venv and run:\n";
test_p += "python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk tests.test_world -q\n";
test_p += "If failures are from the cutover, FIX tests or kernel to match the bounded design (fly ticket preferred, plan.md fallback). ";
test_p += "Do not weaken f013 or empty-card wait. Do not fly KSP. Quote failing tests then re-run.\n";
let test_r = agent(test_p, #{
    label: "verify-unittests",
    capability_mode: "all",
});

let sk_over = "";
sk_over += "Adversarial: did this cutover ticket too much? Read git diff and DESIGN. ";
sk_over += "real=true only if we created a type zoo, ticketed portraits/CHARTER/lessons/desk.md, or deleted card.py fallback so protocol fly bricks. ";
sk_over += "Otherwise real=false with evidence. Use grep/read_file/git diff. DESIGN:\n";
sk_over += design_json;
sk_over += "\nKernel return:\n";
sk_over += json_encode(text_of(k_r));
sk_over += "\nDocs return:\n";
sk_over += json_encode(text_of(docs_r));

let sk_left = "";
sk_left += "Adversarial: leftover card Return keys still required? Grep .grok/agents/*.md and protocol.py SCHEMAS and AGENTS.md When to spawn for need_builder, need_retro, card:, ask: fences, recommended as the only cli. ";
sk_left += "real=true if a spawned desk is STILL told to return need_* as the bus (not as a from-need shim). Evidence = path+quote. DESIGN:\n";
sk_left += design_json;

let skeptics = parallel([
    #{
        label: "skeptic-overticket",
        capability_mode: "read-only",
        prompt: sk_over,
    },
    #{
        label: "skeptic-leftover",
        capability_mode: "read-only",
        prompt: sk_left,
    },
]);

phase("Report");
let rep = "";
rep += "Write docs/program/ticket-bus-cutover.md in GitHub markdown. ";
rep += "Title: Ticket-bus cutover (compile, leftover cards, implementation).\n";
rep += "Sections: 1 What the ticket era already did 2 Leftover card returns (quoted) 3 Why fallback happened 4 MOVE vs KEEP 5 What we changed (files) 6 Tests 7 What is still markdown and why 8 Open risks.\n";
rep += "Use the notes. Verify file quotes with read_file if counts conflict. No Hangar.\n";
rep += "COMPILE:\n";
rep += prior;
rep += "\nFRICTION:\n";
rep += json_encode(friction_blob);
rep += "\nDESIGN:\n";
rep += design_json;
rep += "\nKERNEL:\n";
rep += json_encode(text_of(k_r));
rep += "\nCARDS:\n";
rep += json_encode(text_of(cards_r));
rep += "\nDOCS:\n";
rep += json_encode(text_of(docs_r));
rep += "\nTESTS:\n";
rep += json_encode(text_of(test_r));
rep += "\nSKEPTICS:\n";
rep += json_encode(text_of(skeptics[0]));
rep += "\n";
rep += json_encode(text_of(skeptics[1]));

let report_r = agent(rep, #{
    label: "cutover-report",
    capability_mode: "read-write",
});
let report = text_of(report_r);
if report == "" {
    report = design_text;
}
let scratch = write_scratch_file("ticket-bus-cutover.md", report);
complete(#{
    path: scratch,
    apply: true,
    compile_slots: ci,
    friction_slots: fi,
    kernel_ok: k_r.success,
    tests_ok: test_r.success,
});
