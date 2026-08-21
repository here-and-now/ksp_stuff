let meta = #{
    name: "org-session-audit",
    description: "As-is compile of desk sessions, pain, and org interactions. No recommendations.",
    when_to_use: "When Os wants an as-is report of how house desks worked, pain, and who talked to whom",
    phases: [
        #{ title: "Desk sessions", detail: "one compiler per desk cluster" },
        #{ title: "Interactions", detail: "handoffs, bottlenecks, recurrence, absences" },
        #{ title: "Report", detail: "as-is synthesis only" },
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

fn desk_prompt(title, paths) {
    let p = "";
    p += "You are a read-only historian of the ksp_stuff agent house. ";
    p += "Compile an AS-IS session dossier for: ";
    p += title;
    p += ". Do not recommend. Do not prescribe. State only what the files show.\n\n";
    p += "Use read_file, list_dir, and grep. Do not answer from memory. ";
    p += "If a path is missing, say MISSING. Empty is valid only after you searched.\n\n";
    p += "Read at least:\n";
    p += paths;
    p += "\nAlso grep docs/crew/log, docs/program/world-model.md Open questions, ";
    p += "docs/program/improve, docs/program/note-tech.md, docs/program/feedback.md, ";
    p += "AGENTS.md spawn table, docs/program/PROTOCOL.md, and ";
    p += "docs/missions/jebediah/logs/*-review.md headings for this desk.\n";
    p += "Session transcripts live under /home/os/.grok/sessions/ — list that tree if reachable ";
    p += "and search for this desk name. Crew logs: docs/crew/log/<slug>.md.\n\n";
    p += "Write markdown with these headings only:\n";
    p += "## Desk\n## What they actually did (dated, sourced)\n";
    p += "## Pain points (quoted from files)\n";
    p += "## Recurring patterns observed\n";
    p += "## Files read\n";
    p += "Cite path + short quote or count. No suggestions section.\n";
    p
}

fn ix_prompt(title, focus, prior) {
    let p = "";
    p += "You are a read-only org historian. Topic: ";
    p += title;
    p += "\nAS-IS only. No recommendations.\n";
    p += "Use grep and read_file on /home/os/gits/ksp_stuff. Prior desk notes (may be incomplete):\n";
    p += prior;
    p += "\n\nFocus: ";
    p += focus;
    p += "\n\nRead PROTOCOL.md, AGENTS.md, CHARTER.md, world-model.md Open questions, ";
    p += "crew logs, note-tech.md, improve/I-*.md, gene/gus/linus/lars/jebediah/mortimer logs.\n";
    p += "Count who appears in ask: to: need_*: packets. Who is never in logs.\n";
    p += "Markdown headings: ## Topic ## Observed chains ## Counts/quotes ## Absences ## Files read\n";
    p
}

let root = "/home/os/gits/ksp_stuff";

phase("Desk sessions");
let jobs = [];

jobs.push(#{
    label: "desk-gene",
    capability_mode: "read-only",
    prompt: desk_prompt(
        "Gene Grokman, Flight Director (parent switchboard packets to gene)",
        "- docs/crew/log/gene.md\n- docs/crew/gene.md\n- .grok/agents/gene.md\n- docs/program/plan.md\n- docs/missions/jebediah/plan.md\n- docs/missions/jebediah/briefing.md\n- docs/crew/niche/gene.md"
    ),
});
jobs.push(#{
    label: "desk-gus",
    capability_mode: "read-only",
    prompt: desk_prompt(
        "Gus Grokman, VP Build",
        "- docs/crew/log/gus.md\n- docs/crew/gus.md\n- .grok/agents/gus.md\n- docs/program/vab.md\n- crafts/\n- docs/crew/niche/gus.md"
    ),
});
jobs.push(#{
    label: "desk-linus",
    capability_mode: "read-only",
    prompt: desk_prompt(
        "Linus Grokman, Director of Research",
        "- docs/crew/log/linus.md\n- docs/crew/linus.md\n- .grok/agents/linus.md\n- docs/program/science.md\n- docs/missions/jebediah/science.md"
    ),
});
jobs.push(#{
    label: "desk-lars",
    capability_mode: "read-only",
    prompt: desk_prompt(
        "Lars Grokman, Vehicle Engineering (and Wernher if present)",
        "- docs/crew/log/lars.md\n- docs/crew/log/wernher.md\n- docs/crew/lars.md\n- docs/lessons.md (dated headings)\n- docs/program/blocks.md\n- docs/program/note-tech.md"
    ),
});
jobs.push(#{
    label: "desk-jeb",
    capability_mode: "read-only",
    prompt: desk_prompt(
        "Jebediah Grokman and other Commanders (Valentina, Bill, Bob, Grok)",
        "- docs/crew/log/jebediah.md\n- docs/crew/log/valentina.md\n- docs/crew/log/bill.md\n- docs/crew/log/bob.md\n- docs/crew/log/grok.md\n- .grok/agents/pilot.md\n- docs/program/note-tech.md\n- docs/last-flight.md if present\n- docs/missions/jebediah/logs/"
    ),
});
jobs.push(#{
    label: "desk-mortimer",
    capability_mode: "read-only",
    prompt: desk_prompt(
        "Mortimer Grokman, CEO (and Os packets to him)",
        "- docs/crew/log/mortimer.md\n- docs/crew/mortimer.md\n- .grok/agents/mortimer.md\n- docs/program/slate.md\n- docs/program/CHARTER.md\n- docs/program/PROTOCOL.md"
    ),
});
jobs.push(#{
    label: "desk-others",
    capability_mode: "read-only",
    prompt: desk_prompt(
        "Verena, Walt, Wernher, spotter (deprecated), parent switchboard",
        "- docs/crew/log/verena.md\n- docs/crew/log/walt.md\n- docs/crew/verena.md\n- AGENTS.md spawn table\n- docs/program/PROTOCOL.md\n- docs/press/ if present"
    ),
});
jobs.push(#{
    label: "desk-packets",
    capability_mode: "read-only",
    prompt: desk_prompt(
        "Parent packets, improve queue, world-model asks, F-items",
        "- docs/program/improve/\n- docs/program/world-model.md\n- docs/program/feedback.md\n- docs/program/PROTOCOL.md parallel table\n- AGENTS.md When to spawn"
    ),
});

let desks = parallel(jobs);
let desk_blob = "";
let di = 0;
for r in desks {
    desk_blob += "\n\n===== DESK SLOT ";
    desk_blob += di.to_string();
    desk_blob += " =====\n";
    desk_blob += text_of(r);
    di += 1;
}
log("desk compilers done");

phase("Interactions");
let prior = json_encode(desk_blob);
let ijobs = [];
ijobs.push(#{
    label: "ix-handoffs",
    capability_mode: "read-only",
    prompt: ix_prompt(
        "Handoff graph and chain of command",
        "Who spawned whom. Gene go/need_* to parent to Gus/Linus/Lars/Commander. Packet fields to/from/cli. Depth-1 parent only. Count need_builder vs need_stack vs need_science vs need_gene vs need_mortimer in logs and PROTOCOL.",
        prior
    ),
});
ijobs.push(#{
    label: "ix-bottlenecks",
    capability_mode: "read-only",
    prompt: ix_prompt(
        "Bottlenecks and serial waits",
        "What sat idle: pad vs Gene Learn vs Lars patch vs lock vs protocol fly wait vs kRPC Session. Spawn tax mentions. I-016 pad idle. Serial bind-after-capable. Missing go:. Flight.lock.",
        prior
    ),
});
ijobs.push(#{
    label: "ix-pain",
    capability_mode: "read-only",
    prompt: ix_prompt(
        "Pain points and recurrence",
        "note-tech, lessons.md headings, improve I-012..I-020, F-items, recover voodoo, jsonl speed=0, F-013 Stayputnik, empty card, leftover Hangar, crash UI. Quote dates.",
        prior
    ),
});
ijobs.push(#{
    label: "ix-deadends",
    capability_mode: "read-only",
    prompt: ix_prompt(
        "Recurring loops that did not move sci/tree",
        "hop-to-water heading never 090 repeats, lithobrake Shores, science skip no Experiment modules, leftover PRELAUNCH after crash Close, 497 s FlyingLow, Flea hops. Count repeats from logs/reviews.",
        prior
    ),
});
ijobs.push(#{
    label: "ix-absences",
    capability_mode: "read-only",
    prompt: ix_prompt(
        "Who was left out, who talked, how often",
        "Count log file line counts and dated entries per slug. Who never spawned this program (Wernher, Verena, Bill, Bob, Walt, Valentina, Grok). Mortimer vs Gene chair. Parent as unnamed switchboard.",
        prior
    ),
});

let ixs = parallel(ijobs);
let ix_blob = "";
let ii = 0;
for r in ixs {
    ix_blob += "\n\n===== INTERACTION SLOT ";
    ix_blob += ii.to_string();
    ix_blob += " =====\n";
    ix_blob += text_of(r);
    ii += 1;
}
log("interaction compilers done");

phase("Report");
let syn = "";
syn += "Write ONE extensive AS-IS report in GitHub markdown. ";
syn += "NO suggestions, NO should, NO recommend, NO next steps, NO fix list. ";
syn += "Title: House session and interaction audit (as-is).\n";
syn += "Sections: 1 Executive as-is 2 Per-desk session compile 3 Pain and recurrence ";
syn += "4 Interaction graph and chain of command 5 Bottlenecks and waits ";
syn += "6 Absences and frequency 7 Patterns that repeated without moving sci/tree ";
syn += "8 Source map (paths).\n";
syn += "Only state what the child notes and files show. Attribute quotes to paths. ";
syn += "If unknown, write unknown.\n\nDESK NOTES:\n";
syn += json_encode(desk_blob);
syn += "\n\nINTERACTION NOTES:\n";
syn += json_encode(ix_blob);
syn += "\nUse read_file to verify any count you cite from docs/crew/log or improve/ if the notes conflict.";

let report_r = agent(syn, #{
    label: "as-is-report",
    capability_mode: "read-only",
});
let report = text_of(report_r);
if report == "" {
    report = "# House session and interaction audit (as-is)\n\nunknown — synthesizer returned empty.\n";
    report += desk_blob;
    report += ix_blob;
}
let path = write_scratch_file("org-session-audit.md", report);
complete(#{ path: path, desks: di, interaction_slots: ii });
