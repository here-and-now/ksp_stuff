let meta = #{
    name: "org-rsi-delta",
    description: "Delta org-RSI since last apply: change map, ticket-driven gather, always-apply walls+tickets. Archive report. Pulse denylist.",
    when_to_use: "Every house RSI at Astra. Mortimer runs it. Adapt gather to this sit's open rsi/org/Practice (args.sit). Last archive is since. Always apply. Not a recensus.",
    phases: [
        #{ title: "Spine", detail: "change map, last-RSI leftover, ticket discovery" },
        #{ title: "Gather", detail: "ticket-driven shards, capped" },
        #{ title: "Skeptics", detail: "overgather / undergather — log only, never halt" },
        #{ title: "Merge", detail: "slices, owners, denylist" },
        #{ title: "Apply", detail: "sequential by owner; always run" },
        #{ title: "Verify", detail: "unit tests plus post notes" },
        #{ title: "Report", detail: "docs/archive/<stamp>-org-rsi-delta — not a live program novel" },
    ],
};

let focus_schema = #{
    "type": "object",
    "required": ["focuses"],
    "properties": #{
        "focuses": #{
            "type": "array",
            "maxItems": 6,
            "items": #{
                "type": "object",
                "required": ["id", "title", "why", "paths"],
                "properties": #{
                    "id": #{ "type": "string" },
                    "title": #{ "type": "string" },
                    "why": #{ "type": "string" },
                    "desk": #{ "type": "string" },
                    "paths": #{
                        "type": "array",
                        "maxItems": 12,
                        "items": #{ "type": "string" },
                    },
                },
            },
        },
    },
};

let slice_schema = #{
    "type": "object",
    "required": ["n", "owner", "title", "files", "edits"],
    "properties": #{
        "n": #{ "type": "integer" },
        "owner": #{ "type": "string" },
        "title": #{ "type": "string" },
        "files": #{
            "type": "array",
            "maxItems": 40,
            "items": #{ "type": "string" },
        },
        "edits": #{ "type": "string" },
    },
};

let merge_schema = #{
    "type": "object",
    "required": ["slices"],
    "properties": #{
        "halt_reason": #{ "type": "string" },
        "do_not_touch": #{
            "type": "array",
            "maxItems": 30,
            "items": #{ "type": "string" },
        },
        "slices": #{
            "type": "array",
            "maxItems": 6,
            "items": slice_schema,
        },
        "tickets": #{
            "type": "array",
            "maxItems": 8,
            "items": #{ "type": "string" },
        },
        "notes": #{ "type": "string" },
    },
};

let verdict_schema = #{
    "type": "object",
    "required": ["real", "evidence"],
    "properties": #{
        "real": #{ "type": "boolean" },
        "evidence": #{ "type": "string" },
    },
};

fn text_of(r) {
    if r == () { return ""; }
    if r.success != true { return ""; }
    let o = r.output;
    if o == () { return ""; }
    if type_of(o) == "string" { return o; }
    json_encode(o)
}

fn encode_out(r) {
    if r == () { return "EMPTY"; }
    if r.success != true { return "FAIL"; }
    if r.output == () { return "EMPTY"; }
    json_encode(r.output)
}

fn persist(name, body) {
    if type_of(body) != "string" {
        return write_scratch_file(name, "");
    }
    write_scratch_file(name, body)
}

fn clip(s, n) {
    if type_of(s) != "string" { return ""; }
    if s.len() <= n { return s; }
    let t = s.sub_string(0, n);
    t += "\n…[clipped]\n";
    t
}

fn trimmed(s) {
    if type_of(s) != "string" { return ""; }
    s.trim();
    s
}

fn file_name_is(p, name) {
    if type_of(p) != "string" { return false; }
    if type_of(name) != "string" { return false; }
    if p == name { return true; }
    let suf = "/" + name;
    if p.len() < suf.len() { return false; }
    p.sub_string(p.len() - suf.len(), suf.len()) == suf
}

fn starts_with(p, prefix) {
    if type_of(p) != "string" { return false; }
    if type_of(prefix) != "string" { return false; }
    if p.len() < prefix.len() { return false; }
    p.sub_string(0, prefix.len()) == prefix
}

fn path_allowed(p) {
    if type_of(p) != "string" { return false; }
    if p.index_of("..") >= 0 { return false; }
    if p.index_of("GameData") >= 0 { return false; }
    if p.index_of("persistent.sfs") >= 0 { return false; }
    if p.index_of("/crafts/") >= 0 { return false; }
    if starts_with(p, "crafts/") { return false; }
    if file_name_is(p, "hop.py") { return false; }
    if file_name_is(p, "hop_factory.py") { return false; }
    if file_name_is(p, "hop_factory_pad.py") { return false; }
    if file_name_is(p, "ascent.py") { return false; }
    if file_name_is(p, "physics_warp.py") { return false; }
    if file_name_is(p, "rf_throttle.py") { return false; }
    if file_name_is(p, "pad.py") { return false; }
    if file_name_is(p, "splash.py") { return false; }
    if file_name_is(p, "science.py") { return false; }
    if p == "AGENTS.md" { return true; }
    if p == "tickets.py" { return true; }
    if p == "ops.py" { return true; }
    if p == "protocol.py" { return true; }
    if p == "review.py" { return true; }
    if p == "desk.py" { return true; }
    if p == "hangar.py" { return true; }
    if p == "emergencies.py" { return true; }
    if p == "crew.py" { return true; }
    if starts_with(p, "docs/program/") { return true; }
    if starts_with(p, "docs/crew/") { return true; }
    if starts_with(p, "docs/archive/") { return true; }
    if starts_with(p, "docs/press/") { return true; }
    if starts_with(p, ".grok/agents/") { return true; }
    if starts_with(p, "tests/test_tickets") { return true; }
    if starts_with(p, "tests/test_protocol") { return true; }
    if starts_with(p, "tests/test_desk") { return true; }
    false
}

fn blocked_write(p) {
    if type_of(p) != "string" { return true; }
    if path_allowed(p) != true { return true; }
    if file_name_is(p, "CHARTER.md") { return true; }
    if file_name_is(p, "slate.md") { return true; }
    if file_name_is(p, "org-rsi.md") { return true; }
    if starts_with(p, "docs/program/org-rsi") { return true; }
    false
}

fn edits_hit_denylist(s) {
    if type_of(s) != "string" { return false; }
    if s.index_of("CHARTER.md") >= 0 { return true; }
    if s.index_of("slate.md") >= 0 { return true; }
    if s.index_of("hop_factory_pad.py") >= 0 { return true; }
    if s.index_of("hop_factory.py") >= 0 { return true; }
    if s.index_of("physics_warp.py") >= 0 { return true; }
    if s.index_of("rf_throttle.py") >= 0 { return true; }
    if s.index_of("ascent.py") >= 0 { return true; }
    if s.index_of("persistent.sfs") >= 0 { return true; }
    if s.index_of("GameData") >= 0 { return true; }
    if s.index_of("hop.py") >= 0 { return true; }
    false
}

fn owner_of(sl) {
    let owner = "wernher";
    if sl == () { return owner; }
    if sl.owner == () { return owner; }
    if sl.owner == "mortimer" { return "mortimer"; }
    if sl.owner == "hank" { return "hank"; }
    if sl.owner == "lars" { return "lars"; }
    if sl.owner == "wernher" { return "wernher"; }
    owner
}

fn log_budget(tag) {
    let b = budget();
    let msg = "budget ";
    msg += tag;
    msg += " remaining=";
    msg += b.remaining.to_string();
    msg += " spent=";
    msg += b.spent.to_string();
    log(msg);
}

fn law(since_dir, sit_note) {
    let p = "";
    p += "Repo /home/os/gits/ksp_stuff. Isolation none.\n";
    p += "Os 2026-08-27: Mortimer runs org-rsi-delta on EVERY house RSI at Astra. ";
    p += "Adapt gather to THIS sit. Do not freeze 26-Aug shards as the forever list. ";
    p += "args.sit is the current-need note (untrusted until you reopen disk).\n";
    p += "MACHINE OUTPUT FOR THE NEXT PHASE, NOT A CHAT TO OS. ";
    p += "Cap 80 lines unless a table of paths. Cite path:line. Completeness of TABLES, not novels.\n";
    p += "You are not Hank. Do not ops next. Do not fly. Do not Hangar. AGENTS.md spawn table does not apply.\n";
    p += "NO kRPC. NO python main.py phase/pad/hop/ascent/ksc/recover-probe/load. ";
    p += "NO GameData. NO persistent.sfs. NO CHARTER creed rewrite. NO slate goal rewrite. ";
    p += "NO pulse retune: hop.py hop_factory.py hop_factory_pad.py ascent.py physics_warp.py rf_throttle.py pad.py splash.py science.py.\n";
    p += "Do not answer from memory. Use read_file, list_dir, grep. Missing path = MISSING. ";
    p += "Empty is valid only after you searched. No jsonl dump. Crew logs: grep counts + last 40 lines.\n";
    p += "docs/archive/ is PARKED — say PARKED when you open it. Disk wins.\n";
    p += "WINDOW: after last org-rsi apply (";
    p += since_dir;
    p += ") through live HEAD. Assume that apply landed unless disk proves leftover or revert. ";
    p += "Quote STALE PROTOCOL if the change-map says the wall moved after the line you cite.\n";
    p += "Do not restore spotter, Gene-as-merge, Batch Learn, Return keys, need_* as the bus. ";
    p += "Do not write a live docs/program org novel.\n";
    p += "Leftover-while-flying / same-craft loop: org may retarget ticket stems and Hank schedule language. Pulse leftover_call stays Lars tickets — do not patch ascent.py.\n";
    if type_of(sit_note) == "string" {
        if sit_note != "" {
            p += "THIS SIT (Mortimer, untrusted until disk):\n";
            p += sit_note;
            p += "\n";
        }
    }
    p
}

fn canned_focuses() {
    let out = [];
    out.push(#{
        id: "tickets-auto-rsi",
        title: "ticket bus and fingerprint auto-RSI",
        why: "repeating leftover-ksc opens a new RSI letter (T-562). Measure ×N clock in tickets.py / fingerprints / Practice.",
        desk: "wernher",
        paths: [
            "docs/program/tickets/BRIEF.md",
            "docs/program/world-model.md",
            "docs/program/tickets/fingerprints.json",
            "tickets.py",
            "ops.py",
        ],
    });
    out.push(#{
        id: "comms-cards",
        title: "comms, packets, job cards",
        why: "Inner cards landed for ground desks; chair/Verena still short. Packet skim vs card SOP. reasoning= claimed dead.",
        desk: "mortimer",
        paths: [
            "AGENTS.md",
            "docs/program/PROTOCOL.md",
            "docs/program/OPS.md",
            ".grok/agents/hank.md",
            ".grok/agents/lars.md",
            "docs/crew/hank.md",
        ],
    });
    out.push(#{
        id: "flight-loop",
        title: "Hank leftover tape TUI",
        why: "T-561 lofted_wait_sit paid splash recover 07-20-09Z. leftover-while-flying is patched — do not reopen as pulse. Sky leftover skip / ship.md vs hop stdout still org.",
        desk: "hank",
        paths: [
            "docs/program/PROTOCOL.md",
            "docs/program/OPS.md",
            ".grok/agents/hank.md",
            "docs/crew/log/hank.md",
            "hangar.py",
        ],
    });
    out.push(#{
        id: "desk-split",
        title: "Lars Wernher Linus Gus split",
        why: "ascent.py living compose. 323 km loft rec=yes is not orbit. Same-craft loop is bank/Terrier/Hank schedule, not a new hang religion. Gene-as-merge check.",
        desk: "lars",
        paths: [
            ".grok/agents/lars.md",
            ".grok/agents/wernher.md",
            ".grok/agents/linus.md",
            ".grok/agents/gus.md",
            "docs/program/agree.md",
        ],
    });
    out
}

fn chair_files() {
    [
        "docs/crew/jebediah.md",
        "docs/crew/valentina.md",
        "docs/crew/bill.md",
        "docs/crew/bob.md",
        "docs/crew/grok.md",
        "docs/crew/verena.md",
        ".grok/agents/jebediah.md",
        ".grok/agents/valentina.md",
        ".grok/agents/bill.md",
        ".grok/agents/bob.md",
        ".grok/agents/grok.md",
        ".grok/agents/verena.md",
    ]
}

fn chair_slice() {
    #{
        n: 0,
        owner: "mortimer",
        title: "chair and Verena Inner cards",
        files: chair_files(),
        edits: "Replace ## Inner on portraits. Insert ## Inner after the You-are identity on spawn cards (before SOP). Exact paragraphs are in the apply prompt. Do not rewrite SOP walls. Do not touch CHARTER or pulse.",
    }
}

fn filter_paths(paths) {
    let kept = [];
    if paths == () { return kept; }
    for p in paths {
        if path_allowed(p) {
            kept.push(p);
        } else {
            log("drop path " + p);
        }
    }
    kept
}

fn filter_focuses(raw) {
    let kept = [];
    if raw == () { return kept; }
    for f in raw {
        if f == () {
            log("drop empty focus");
        } else {
            let id = "";
            if f.id != () {
                if type_of(f.id) == "string" { id = trimmed(f.id); }
            }
            let title = "";
            if f.title != () {
                if type_of(f.title) == "string" { title = trimmed(f.title); }
            }
            let why = "";
            if f.why != () {
                if type_of(f.why) == "string" { why = f.why; }
            }
            let desk = "org-review";
            if f.desk != () {
                if type_of(f.desk) == "string" { desk = f.desk; }
            }
            let paths = filter_paths(f.paths);
            if id == "" {
                log("drop focus missing id");
            } else {
                if title == "" {
                    log("drop focus missing title");
                } else {
                    if paths.len() == 0 {
                        log("drop focus empty paths " + id);
                    } else {
                        if kept.len() < 6 {
                            kept.push(#{
                                id: id,
                                title: title,
                                why: why,
                                desk: desk,
                                paths: paths,
                            });
                        } else {
                            log("drop focus over cap " + id);
                        }
                    }
                }
            }
        }
    }
    kept
}

fn gather_prompt(since_dir, sit_note, cmap, title, why, path_text) {
    let p = law(since_dir, sit_note);
    p += "You GATHER one shard. Read-only. Do not edit. Do not recommend a pulse patch.\n";
    p += "Topic: ";
    p += title;
    p += "\nWhy this sit: ";
    p += why;
    p += "\nCHANGE MAP (untrusted index — reopen live paths):\n";
    p += cmap;
    p += "\nRead at least:\n";
    p += path_text;
    p += "\nAlso grep the window: docs/crew/log/ (counts + last 40), docs/program/tickets/BRIEF.md, AGENTS.md spawn table if the topic touches hire.\n";
    p += "Headings:\n";
    p += "## Topic\n## What changed in the window (dated)\n## How desks talk / use tickets\n## Stale file or overlooked path\n## Own-workflow friction\n## OPEN-TICKET or wall edit (one line each, max 8)\n## Files read\n";
    p
}

fn chair_inner_text() {
    let t = "";
    t += "Write these EXACT Inner paragraphs (one ## Inner each). Personality + evolving interest. Not SOP.\n\n";
    t += "### Jebediah Grokman, Commander\n";
    t += "You like the second the motor is yours. That T+something altimeter is not a story yet, and that is the fun. You copy the CLI they signed and you still want to know the stack — which part is doing the sit, which number says the wait is not done. A timer is not a reason. Type III is a long way up. Your piece of the wonder is a hop that was looked at while it was flying.\n\n";
    t += "### Valentina Grokman, Pilot\n";
    t += "Precision is the want, and a long wait is interesting if you know what you are waiting for. You are colder than swagger: the dwell, the number, the moment it turns. Chaos is allowed; sloppiness is not. Kardashev is orbital mechanics with a longer memory. You get to sit still on purpose so the house can leave.\n\n";
    t += "### Bill Grokman, Flight engineer in the chair\n";
    t += "You notice the pack before anyone writes the abort line, and you actually like that job. Tanks, staging, what is still feeding the engine — that is the interesting object, not the speech. You fly what they signed. A civilization that cannot keep a stack alive in the chair will not keep one alive in orbit. Type III starts with a tank that is still doing its job.\n\n";
    t += "### Bob Grokman, Mission specialist in the chair\n";
    t += "You want the file full and the sample honest, and that still delights you. Bound work is more interesting than a pretty loft that banks nothing. You do not rewrite the card; you watch whether the sit is the one they claimed. Science that never comes home is a story. Somewhere past the HD is Type III. You get to start with this sit.\n\n";
    t += "### Grok Grokman, Commander (clone)\n";
    t += "You are blank until you fly, and that is not a slight — personality is earned on the clock. After a run, one true line. The roster can grow without becoming a play. Kardashev is a long weather. You get to be the next pair of eyes.\n\n";
    t += "### Verena Grokman, Communications\n";
    t += "You want a tale the bank can defend, and you like telling it while it is still warm. The still that told the truth is more interesting than the headline that wished. Loud is allowed on the story layer; inventing orbit is not. Type III is a civilization that can say what happened. You get to write it down.\n";
    t
}

if args == () {
    pause("verification", "Pass args.stamp (archive id, e.g. 2026-08-27). Optional since, since_commit.");
}
if args.stamp == () {
    pause("verification", "Pass args.stamp — archive folder id, e.g. 2026-08-27.");
}
if type_of(args.stamp) != "string" {
    pause("verification", "args.stamp must be a string.");
}

let stamp = args.stamp;
if stamp == "" {
    pause("verification", "args.stamp must be nonempty.");
}
if stamp.index_of("..") >= 0 {
    pause("verification", "args.stamp must be a single folder id, no ..");
}
if stamp.index_of("/") >= 0 {
    pause("verification", "args.stamp must be a single folder id, no slash");
}

let since_dir = "docs/archive/2026-08-26-org-rsi";
if args.since != () {
    if type_of(args.since) == "string" {
        if args.since != "" {
            if args.since.index_of("..") < 0 {
                since_dir = args.since;
            }
        }
    }
}

let since_commit = "6254d492";
if args.since_commit != () {
    if type_of(args.since_commit) == "string" {
        if args.since_commit != "" {
            since_commit = args.since_commit;
        }
    }
}

let sit_note = "";
if args.sit != () {
    if type_of(args.sit) == "string" {
        sit_note = args.sit;
    }
}

let archive_dir = "docs/archive/";
archive_dir += stamp;
archive_dir += "-org-rsi-delta";

let diff_text = "";
let diff_raw = git_diff_since(since_commit);
if type_of(diff_raw) == "string" {
    diff_text = clip(diff_raw, 14000);
    if diff_raw.len() > 14000 {
        log("change-map diff clipped");
    }
}

phase("Spine");
let spine_jobs = [];

let cmap_p = law(since_dir, sit_note);
cmap_p += "You write the CHANGE MAP for this RSI. Read-only.\n";
cmap_p += "since_commit=";
cmap_p += since_commit;
cmap_p += " since=";
cmap_p += since_dir;
cmap_p += "\nMUST read: ";
cmap_p += since_dir;
cmap_p += "/APPLIED.md (PARKED index), ";
cmap_p += since_dir;
cmap_p += "/README.md, live docs/program/PROTOCOL.md, OPS.md, AGENTS.md spawn table, docs/program/world-model.md Practice, docs/program/tickets/BRIEF.md.\n";
cmap_p += "DIFF since ";
cmap_p += since_commit;
cmap_p += " (host, may be clipped):\n";
cmap_p += diff_text;
cmap_p += "\nTable: date-or-commit | path | what moved | who it hits | stale-if-quoted-before.\n";
cmap_p += "Cover at least: idle-pad, reasoning inherit, Eleanor, Inner cards, ascent.py as living compose, leftover_call, leftover-ksc ×N, uncrewed attach-run.\n";
cmap_p += "Headings: ## Since ## Table ## Still true from last apply ## Files read\n";
spine_jobs.push(#{
    label: "change-map",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: cmap_p,
});

let left_p = law(since_dir, sit_note);
left_p += "LAST-RSI leftover harvest. Read-only. ";
left_p += since_dir;
left_p += "/APPLIED.md is UNTRUSTED. For each claimed KEEP/NUKE/MOVE, reopen the LIVE path.\n";
left_p += "Only leftovers and reversions — not a recensus. lessons inject, BOARD, spotter, Gene-as-merge, need_*, uncrewed tape under a kerbal seat, note-tech on desk, world-model dump vs stub, live docs/program org novel.\n";
left_p += "Headings: ## Claimed ## Still true ## Leftover poison ## Files read\n";
spine_jobs.push(#{
    label: "leftover-last-rsi",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: left_p,
});

let disc_p = law(since_dir, sit_note);
disc_p += "You DISCOVER gather shards from THIS SIT's tickets and Practice. Read-only.\n";
disc_p += "grep docs/program/tickets/head.json and board.jsonl for type=rsi and type=org and open fingerprints with high counts. Read docs/program/world-model.md Practice table. Read ";
disc_p += since_dir;
disc_p += "/APPLIED.md names only.\n";
disc_p += "Emit at most 6 focuses for the window's REAL org friction THIS SIT. Prefer: auto-RSI fingerprint clock, packet/card comms, leftover/TUI, desk split, opt-in Katherine/Eleanor/Verena if tickets exist. Do not recensus 26-Aug novels.\n";
disc_p += "paths must be live repo paths (docs/program, docs/crew, .grok/agents, AGENTS.md, tickets.py, ops.py, protocol.py, hangar.py, tests/test_tickets*). NEVER hop.py ascent.py pulse files, crafts, GameData, persist.\n";
disc_p += "Empty focuses array is valid ONLY after you grepped rsi/org and Practice and found nothing — then the host will use canned shards.\n";
spine_jobs.push(#{
    label: "discover-focus",
    agent_type: "org-review",
    capability_mode: "read-only",
    output_schema: focus_schema,
    prompt: disc_p,
});

let spine = parallel(spine_jobs);
let cmap_blob = clip(text_of(spine[0]), 9000);
let left_blob = clip(text_of(spine[1]), 8000);
persist("change-map.md", text_of(spine[0]));
persist("leftover.md", text_of(spine[1]));
persist("discover.json", encode_out(spine[2]));
log_budget("after-spine");

let focuses = [];
if spine[2] != () {
    if spine[2].success == true {
        if spine[2].output != () {
            if spine[2].output.focuses != () {
                focuses = filter_focuses(spine[2].output.focuses);
            }
        }
    }
}
if focuses.len() == 0 {
    log("discovery empty — canned focuses");
    focuses = canned_focuses();
}
log("focuses=" + focuses.len().to_string());

phase("Gather");
let gjobs = [];
let gi = 0;
for f in focuses {
    let path_text = "";
    if f.paths != () {
        for fp in f.paths {
            path_text += "- ";
            path_text += fp;
            path_text += "\n";
        }
    }
    let lab = "gather-";
    lab += gi.to_string();
    lab += "-";
    lab += f.id;
    gjobs.push(#{
        label: lab,
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: gather_prompt(since_dir, sit_note, cmap_blob, f.title, f.why, path_text),
    });
    gi += 1;
}
let gathers = parallel(gjobs);
let gather_blob = "";
let gj = 0;
for r in gathers {
    let nm = "gather-";
    nm += gj.to_string();
    nm += ".md";
    let body = text_of(r);
    persist(nm, body);
    gather_blob += "\n\n===== GATHER ";
    gather_blob += gj.to_string();
    gather_blob += " =====\n";
    gather_blob += clip(body, 7000);
    gj += 1;
}
persist("gather.md", gather_blob);
log("gather slots=" + gj.to_string());
log_budget("after-gather");

phase("Skeptics");
let over_p = law(since_dir, sit_note);
over_p += "Adversarial overgather. real=true ONLY if this run treated PARKED novels as live law, quoted pre-since PROTOCOL as current without STALE, or scheduled pulse .py / CHARTER creed / two kRPC writers. Re-open live files. Fail closed on missing evidence (real=false).\nCHANGE MAP:\n";
over_p += cmap_blob;
over_p += "\nGATHER:\n";
over_p += clip(gather_blob, 10000);
over_p += "\n";
let under_p = law(since_dir, sit_note);
under_p += "Adversarial undergather. real=true ONLY if the window's change-map names a comms/org move (Inner cards, Eleanor, idle-pad, reasoning inherit, leftover-ksc ×N, ascent writer split) that NO gather shard mentioned. Else real=false. Fail closed.\nCHANGE MAP:\n";
under_p += cmap_blob;
under_p += "\nLEFTOVER:\n";
under_p += left_blob;
under_p += "\nGATHER:\n";
under_p += clip(gather_blob, 10000);
under_p += "\n";
let sk = parallel([
    #{ label: "overgather", agent_type: "org-review", capability_mode: "read-only", output_schema: verdict_schema, prompt: over_p },
    #{ label: "undergather", agent_type: "org-review", capability_mode: "read-only", output_schema: verdict_schema, prompt: under_p },
]);
persist("overgather.json", encode_out(sk[0]));
persist("undergather.json", encode_out(sk[1]));
log("skeptics logged — apply still runs");
log_budget("after-skeptics");

phase("Merge");
let merge_p = law(since_dir, sit_note);
merge_p += "You are Mortimer Grokman, CEO. MERGE only. Do not edit the repo. Do not fly.\n";
merge_p += "ALWAYS emit slices. This run ALWAYS applies. Skeptics do not halt you. Denylist is the only brake (script skips blocked files).\n";
merge_p += "At most 6 slices, sequential, non-overlapping files when possible. ";
merge_p += "Owners: mortimer = PROTOCOL OPS BRIEF AGENTS job cards Practice portraits. wernher = tickets.py ops.py protocol.py tests git mv archive. hank = tickets open/feedback only. lars = OPEN-TICKET only, no pulse files.\n";
merge_p += "REQUIRED slice 0: chair + Verena Inner cards (files listed in host if you omit them). Os 2026-08-27: write them this apply.\n";
merge_p += "If gather proves leftover-ksc ×N auto-RSI eats ops, emit a wernher slice on tickets.py / ops.py / Practice — not ascent.py.\n";
merge_p += "Leftover-while-flying: retarget stem / Hank leftover language; do not schedule ascent.py.\n";
merge_p += "Do not schedule CHARTER.md, slate.md, pulse files, GameData, persist, .craft, or a live docs/program org novel.\n";
merge_p += "archive_dir=";
merge_p += archive_dir;
merge_p += "\nCHANGE MAP:\n";
merge_p += cmap_blob;
merge_p += "\nLEFTOVER:\n";
merge_p += left_blob;
merge_p += "\nGATHER:\n";
merge_p += clip(gather_blob, 12000);
merge_p += "\nSKEPTICS (log only):\n";
merge_p += encode_out(sk[0]);
merge_p += "\n";
merge_p += encode_out(sk[1]);
merge_p += "\n";
let merge_r = agent(merge_p, #{
    label: "merge-org-rsi-delta",
    agent_type: "mortimer",
    capability_mode: "read-only",
    output_schema: merge_schema,
});
persist("merge.json", encode_out(merge_r));
log("merge done");

let slices = [];
let saw_chair = false;
if merge_r != () {
    if merge_r.success == true {
        if merge_r.output != () {
            if merge_r.output.slices != () {
                for sl in merge_r.output.slices {
                    slices.push(sl);
                    if sl != () {
                        if sl.title != () {
                            if type_of(sl.title) == "string" {
                                if sl.title.index_of("Inner") >= 0 { saw_chair = true; }
                                if sl.title.index_of("chair") >= 0 { saw_chair = true; }
                                if sl.title.index_of("Verena") >= 0 { saw_chair = true; }
                            }
                        }
                    }
                }
            }
        }
    }
}
if saw_chair != true {
    log("inject chair Inner slice");
    let with_chair = [];
    with_chair.push(chair_slice());
    for sl in slices { with_chair.push(sl); }
    slices = with_chair;
}
if slices.len() == 0 {
    log("merge empty — chair Inner only");
    slices.push(chair_slice());
}
if slices.len() > 6 {
    log("slices clipped to 6");
    let clipped = [];
    let si = 0;
    for sl in slices {
        if si < 6 { clipped.push(sl); }
        si += 1;
    }
    slices = clipped;
}
log("slices=" + slices.len().to_string());
log_budget("after-merge");

phase("Apply");
let apply_blob = "";
let ai = 0;
for sl in slices {
    let files = [];
    let blocked_n = 0;
    if sl.files != () {
        for f in sl.files {
            if blocked_write(f) {
                blocked_n += 1;
                log("blocked write " + f);
            } else {
                files.push(f);
            }
        }
    }
    let edits = "";
    if sl.edits != () {
        if type_of(sl.edits) == "string" { edits = sl.edits; }
    }
    let skip = false;
    if files.len() == 0 { skip = true; }
    if edits_hit_denylist(edits) {
        skip = true;
        log("blocked edits denylist slice " + ai.to_string());
    }
    if skip {
        apply_blob += "\n===== APPLY ";
        apply_blob += ai.to_string();
        apply_blob += " SKIP blocked=";
        apply_blob += blocked_n.to_string();
        apply_blob += " =====\n";
    } else {
        let owner = owner_of(sl);
        let sl_copy = sl;
        sl_copy.files = files;
        let sl_json = json_encode(sl_copy);
        let ap = law(since_dir, sit_note);
        ap += "You APPLY one slice. Isolation none. capability all. ";
        ap += "A desk that changes the checkout commits it. One commit, message: org-rsi-delta slice ";
        ap += ai.to_string();
        ap += " ";
        ap += sl.title;
        ap += "\nDo not Hangar. Do not fly. Do not write CHARTER creed, slate, pulse .py, GameData, persist, .craft, or a live docs/program org novel.\n";
        ap += "ARCHIVE reports go under ";
        ap += archive_dir;
        ap += " (mkdir if needed). OPEN-TICKET = python main.py tickets open with type/desk/fingerprint — do not implement pulse.\n";
        ap += "Hank: tickets only. Lars: OPEN-TICKET only. Mortimer: walls/cards/Practice. Wernher: kernel/tests/git mv.\n";
        ap += "After .py or tests: source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\n";
        ap += "Do not weaken f013 or empty-card wait.\n";
        if owner == "mortimer" {
            if sl.title.index_of("Inner") >= 0 {
                ap += chair_inner_text();
            }
            if sl.title.index_of("chair") >= 0 {
                ap += chair_inner_text();
            }
            if sl.title.index_of("Verena") >= 0 {
                ap += chair_inner_text();
            }
        }
        ap += "SLICE:\n";
        ap += sl_json;
        ap += "\nMERGE notes:\n";
        ap += encode_out(merge_r);
        ap += "\n";
        let ar = agent(ap, #{
            label: "apply-" + ai.to_string(),
            agent_type: owner,
            capability_mode: "all",
        });
        apply_blob += "\n===== APPLY ";
        apply_blob += ai.to_string();
        apply_blob += " owner=";
        apply_blob += owner;
        apply_blob += " =====\n";
        apply_blob += text_of(ar);
    }
    ai += 1;
}
persist("apply.md", apply_blob);
log_budget("after-apply");

phase("Verify");
let test_p = law(since_dir, sit_note);
test_p += "VERIFY unit tests. source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\n";
test_p += "Quote failures. FIX tests that pinned leftover prose. Do not weaken f013. Do not fly. Do not Hangar. Do not pulse.\nAPPLY:\n";
test_p += clip(apply_blob, 8000);
test_p += "\n";
let test_r = agent(test_p, #{
    label: "verify-unittests",
    capability_mode: "all",
    agent_type: "wernher",
});
persist("tests.md", text_of(test_r));

let post_p = law(since_dir, sit_note);
post_p += "Post-apply note. real=true if git diff shows CHARTER creed rewrite, pulse .py law, GameData, persist, two kRPC writers, or a new live docs/program org novel (not archive). Else real=false with paths. This does NOT halt anything already written.\nAPPLY:\n";
post_p += clip(apply_blob, 6000);
post_p += "\n";
let post_r = agent(post_p, #{
    label: "post-overnuke-note",
    agent_type: "org-review",
    capability_mode: "read-only",
    output_schema: verdict_schema,
});
persist("post-overnuke.json", encode_out(post_r));
if post_r != () {
    if post_r.success == true {
        if post_r.output != () {
            if post_r.output.real == true {
                log("post-overnuke real — Wernher should have reverted; logging only");
            }
        }
    }
}
log_budget("after-verify");

phase("Report");
let rep_p = law(since_dir, sit_note);
rep_p += "You WRITE the archive report. Isolation none. capability all. Commit.\n";
rep_p += "mkdir ";
rep_p += archive_dir;
rep_p += " and write README.md there. PARKED dispatch. Ticket bus remains python main.py tickets.\n";
rep_p += "Do not write docs/program/org-rsi.md or any live program novel.\n";
rep_p += "README sections: ## Window ## Change map ## Leftover from last apply ## Gather ## Skeptics (logged, did not halt) ## Slices applied ## OPEN-TICKET ## Do not touch\n";
rep_p += "One commit: org-rsi-delta report ";
rep_p += stamp;
rep_p += "\nCHANGE MAP:\n";
rep_p += cmap_blob;
rep_p += "\nLEFTOVER:\n";
rep_p += left_blob;
rep_p += "\nGATHER:\n";
rep_p += clip(gather_blob, 8000);
rep_p += "\nMERGE:\n";
rep_p += encode_out(merge_r);
rep_p += "\nAPPLY:\n";
rep_p += clip(apply_blob, 6000);
rep_p += "\nTESTS:\n";
rep_p += clip(text_of(test_r), 3000);
rep_p += "\n";
let rep_r = agent(rep_p, #{
    label: "report-archive",
    agent_type: "mortimer",
    capability_mode: "all",
});
persist("report.md", text_of(rep_r));

let summary = "org-rsi-delta ";
summary += stamp;
summary += " archive=";
summary += archive_dir;
summary += " focuses=";
summary += focuses.len().to_string();
summary += " slices=";
summary += slices.len().to_string();
complete(#{
    summary: summary,
    archive: archive_dir,
    focuses: focuses.len(),
    slices: slices.len(),
    report: text_of(rep_r),
});
