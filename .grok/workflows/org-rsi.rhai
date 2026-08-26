let meta = #{
    name: "org-rsi",
    description: "Reusable house org-RSI: optional census, sharded design, skeptics, thin merge, optional pad-safe apply. Report in archive, never a live program novel.",
    when_to_use: "Major org overhaul: markdown/card/injection rot, ticket bus supposed to be comms, live radio (parent treats hop stdout as the pad), or Os wants census then optional apply without a live docs/program letter",
    phases: [
        #{ title: "Census", detail: "sharded live tree when no prior (or args.census true)" },
        #{ title: "Coverage", detail: "prior index vs live tree; gaps only" },
        #{ title: "Harvest", detail: "claimed vs still-true; discover novels on disk" },
        #{ title: "Comms", detail: "PROTOCOL vs log, Hank in between" },
        #{ title: "Classify", detail: "KEEP TAPE ARCHIVE NUKE MOVE UNKNOWN" },
        #{ title: "Friction", detail: "dual stores, inject, leftover roles" },
        #{ title: "Design", detail: "one child per standing heading; disk wins" },
        #{ title: "Skeptics", detail: "overnuke / undernuke per shard; fail closed" },
        #{ title: "Merge", detail: "sequence, owners, files, do-not-touch" },
        #{ title: "Apply", detail: "sequential slices; script denylist" },
        #{ title: "Verify", detail: "unit tests plus post-apply skeptics" },
        #{ title: "Fix", detail: "one round if tests or undernuke" },
        #{ title: "Report", detail: "docs/archive/<stamp>-org-rsi — not docs/program" },
    ],
};

let skeptic_schema = #{
    "type": "object",
    "required": ["overnuke", "undernuke", "evidence"],
    "properties": #{
        "overnuke": #{ "type": "boolean" },
        "undernuke": #{ "type": "boolean" },
        "evidence": #{ "type": "string" },
        "must_change": #{
            "type": "array",
            "maxItems": 24,
            "items": #{ "type": "string" },
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
    "required": ["apply", "slices"],
    "properties": #{
        "apply": #{ "type": "boolean" },
        "halt_reason": #{ "type": "string" },
        "do_not_touch": #{
            "type": "array",
            "maxItems": 30,
            "items": #{ "type": "string" },
        },
        "slices": #{
            "type": "array",
            "maxItems": 8,
            "items": slice_schema,
        },
        "tickets": #{
            "type": "array",
            "maxItems": 6,
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

fn file_name_is(p, name) {
    if type_of(p) != "string" { return false; }
    if type_of(name) != "string" { return false; }
    if p == name { return true; }
    let suf = "/" + name;
    if p.len() < suf.len() { return false; }
    p.sub_string(p.len() - suf.len(), suf.len()) == suf
}

fn blocked_write(p) {
    if type_of(p) != "string" { return true; }
    if file_name_is(p, "CHARTER.md") { return true; }
    if file_name_is(p, "slate.md") { return true; }
    if file_name_is(p, "hop.py") { return true; }
    if file_name_is(p, "hop_factory.py") { return true; }
    if file_name_is(p, "hop_factory_pad.py") { return true; }
    if file_name_is(p, "physics_warp.py") { return true; }
    if file_name_is(p, "pad.py") { return true; }
    if file_name_is(p, "splash.py") { return true; }
    if file_name_is(p, "science.py") { return true; }
    if file_name_is(p, "persistent.sfs") { return true; }
    if p.index_of("GameData") >= 0 { return true; }
    if p.index_of("/crafts/") >= 0 { return true; }
    if p.index_of("crafts/") == 0 { return true; }
    false
}

fn edits_hit_denylist(s) {
    if type_of(s) != "string" { return false; }
    if s.index_of("CHARTER.md") >= 0 { return true; }
    if s.index_of("slate.md") >= 0 { return true; }
    if s.index_of("hop_factory_pad.py") >= 0 { return true; }
    if s.index_of("hop_factory.py") >= 0 { return true; }
    if s.index_of("physics_warp.py") >= 0 { return true; }
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

fn law(prior) {
    let p = "";
    p += "Repo /home/os/gits/ksp_stuff. Isolation none.\n";
    p += "THIS IS MACHINE OUTPUT FOR THE NEXT WORKFLOW PHASE, NOT A CHAT TO OS. ";
    p += "NO LINE CAP. NO TOKEN CAP. NO VIEWPORT CAP. NO PORTRAIT FIT. Completeness wins. ";
    p += "You are not Hank. Do not ops next. Do not fly. Do not Hangar. AGENTS.md spawn table does not apply.\n";
    p += "NO kRPC. NO python main.py phase/pad/hop/ksc/recover-probe/load. ";
    p += "NO GameData. NO persistent.sfs. NO CHARTER creed rewrite. NO slate goal rewrite. ";
    p += "NO hop.py / hop_factory.py / hop_factory_pad.py / physics_warp.py / pad.py / splash.py / science.py pulse retune.\n";
    p += "Do not answer from memory. Use read_file, list_dir, grep. Missing path = MISSING. ";
    p += "Empty is valid only after you searched. Write the tables you need. Cite path:line. ";
    p += "No jsonl dump. Crew logs: grep counts + last 40 lines, not the whole file. ";
    p += "docs/archive/ is PARKED — say PARKED when you open it. Discarded letters are not law.\n";
    if type_of(prior) == "string" {
        if prior != "" {
            p += "Prior bibliography (UNTRUSTED index): ";
            p += prior;
            p += " — open README first, then the matching prior file as an index, then list_dir/grep/wc live. Disk wins. Do not copy a class until you opened the live path.\n";
        } else {
            p += "No prior bibliography. Live disk only.\n";
        }
    }
    p += "Standing intent (not proven file classes — verify on disk): ticket bus is comms; MD only when a ticket cannot hold it; ";
    p += "do not inject lessons.md as miss physics; uncrewed tape should not be named after a kerbal seat; spotter is retired; ";
    p += "Lars compose from Wernher blocks is a later OPEN-TICKET, not a pulse retune this apply; pad stays hot; depth 1; one control writer.\n";
    p += "Live radio: hop light is not airborne. Parent mid-hop reads ship.md; one stuck PNG when sit/MET/log disagree; do not wait on hop stdout. ";
    p += "TUI is phase start / phase end / unexpected. Skip-save Tracking is not Close. recover() rec=yes then persist; if persist fails stay Flight.\n";
    p += "Keep unless disk proves otherwise: learn-rsi attach-run, lars-rsi S/M/C prefixes + hop_factory_pad.py as the pad-RF file.\n";
    p += "Do not restore spotter as spawnable, Gene-as-merge, Batch Learn, Return keys, need_* as the bus. ";
    p += "Do not leave a new live docs/program/*.md org novel. Reports go to archive or workflow scratch.\n";
    p
}

fn census_prompt(prior, title, focus, paths) {
    let p = law(prior);
    p += "You are a read-only historian of the CURRENT house. Topic: ";
    p += title;
    p += "\nAS-IS only. Do not recommend. Do not edit.\nFocus: ";
    p += focus;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nHeadings:\n";
    p += "## Topic\n## Counts (path:line or wc — measure, do not recall)\n## Who writes it\n## Who is told to read it\n";
    p += "## Injected every hire? (job card / packet / PROTOCOL)\n## Stale vs live (dated last write)\n## Files read\n";
    p
}

fn harvest_prompt(prior) {
    let p = law(prior);
    p += "You are a read-only RSI historian. Discover prior jumps ON DISK — do not assume which novels exist.\n";
    p += "list_dir docs/program (md). list_dir .grok/workflows. list_dir docs/archive (names only, PARKED).\n";
    p += "For each live org/RSI novel or workflow report you find, quote what it claimed vs what is still true (path:line). ";
    p += "Leftover that still poisons the next hire. What it did not touch.\n";
    p += "Headings: ## Jumps found ## Per jump (claimed / still true / leftover) ## Files read\n";
    p
}

fn comms_prompt(prior) {
    let p = law(prior);
    p += "You are a read-only comms historian for the whole house (one shard).\n";
    p += "Desks: Mortimer, Hank, Gene, Lars, Wernher, Gus, Linus, Commander. ";
    p += "PROTOCOL vs crew log. How Hank sits in between (ops next / packet / leftover / tape). ";
    p += "Writes: md vs tickets stamp vs tickets feedback. Card format. Too long?\n";
    p += "Read at least: docs/program/PROTOCOL.md Handoffs + Spawn packet + Files + Feedback; docs/program/OPS.md; ";
    p += "AGENTS.md spawn table; .grok/agents/ (headers + first command); docs/crew/log/ (counts + last 40 per slug); ";
    p += "docs/program/tickets/BRIEF.md.\n";
    p += "Headings: ## Per desk ## Hank in between ## Ticket vs md ## Files read\n";
    p
}

fn classify_prompt(prior, title, paths, rule) {
    let p = law(prior);
    p += "You classify live files. Shard: ";
    p += title;
    p += "\nlist_dir the shard, then read headers. Do not dump bodies.\n";
    p += "For EACH md/json that is not under docs/archive/, pick exactly one class:\n";
    p += "KEEP = constitution/voice/sit snapshot the next hire must read as prose.\n";
    p += "TAPE = evidence (jsonl, review envelope, screenshots). Keep on disk, do not inject.\n";
    p += "ARCHIVE = already parked or must move under docs/archive/ and drop from spawn-read.\n";
    p += "NUKE = still in the live tree, poisons hires, should vanish or park this sit.\n";
    p += "MOVE = content that already is or should be a ticket field/finding, not a board.\n";
    p += "UNKNOWN = you could not tell after search.\n";
    p += "Rule of thumb: ";
    p += rule;
    p += "\nRead at least:\n";
    p += paths;
    p += "\nHeadings: ## Shard ## Table (path | class | lines | last writer | injected? | evidence) ## Inventory mismatch ## Files read\n";
    p += "Cap the table at 80 rows; if more, group by directory and state the drop in the artifact (do not silently truncate).\n";
    p
}

fn friction_prompt(prior) {
    let p = law(prior);
    p += "You are a read-only org analyst.\n";
    p += "Why dual stores / injection / leftover roles happen. Damage to the NEXT hire. Evidence path:line.\n";
    p += "Read live: AGENTS.md packet, PROTOCOL spawn packet, tickets.py packet(), docs/lessons.md header + grep ^## count, ";
    p += ".grok/agents/lars.md After a miss, .grok/agents/spotter.md, docs/program/ current live md list, docs_inventory.py classes.\n";
    p += "Headings: ## Mechanisms ## Evidence ## Damage to next hire ## Files read\n";
    p
}

fn coverage_prompt(prior) {
    let p = law(prior);
    p += "Coverage only. ";
    if type_of(prior) == "string" {
        if prior != "" {
            p += "Read ";
            p += prior;
            p += "/README.md and list_dir that directory. ";
        }
    }
    p += "list_dir live docs/program (md), .grok/agents, docs/missions (not log bodies), docs/crew (portraits, not whole logs), ";
    p += "docs/press, docs/lessons.md, docs/agent-notes.md, AGENTS.md.\n";
    p += "Gaps = live md the prior notes never mention (path or basename). Test fixtures under tests/ are not gaps. ";
    p += "Do not classify. Do not plan. Write a full table. Headings: ## Prior ## Live ## Gaps ## Files read\n";
    p
}

fn design_prompt(prior, heading, focus, prior_files, live_paths) {
    let p = law(prior);
    p += "You DESIGN one shard. Read-only. Do not edit. Do not fly. Do not open tickets.\n";
    p += "Heading you own: ";
    p += heading;
    p += "\nFocus: ";
    p += focus;
    p += "\n";
    if type_of(prior) == "string" {
        if prior != "" {
            p += "MUST read, in order: ";
            p += prior;
            p += "/README.md then these prior files as an untrusted index:\n";
            p += prior_files;
            p += "\n";
        }
    }
    p += "Then list_dir + read live:\n";
    p += live_paths;
    p += "\nFor each path this heading owns, pick exactly one action: KEEP TAPE ARCHIVE NUKE REWRITE MOVE OPEN-TICKET LEAVE. ";
    p += "Name owner mortimer, wernher, hank, or lars. Name a slice 1-8. ";
    p += "Pad-safe: tests that pin a file must REWRITE before NUKE/ARCHIVE of that file. ";
    p += "OPEN-TICKET for anything that would retune pulse law. ";
    p += "Do not schedule CHARTER creed, slate, pulse .py, GameData, persistent.sfs, portraits-as-voice, jsonl schema, or desk.md snapshot.\n";
    p += "Headings: ## Heading ## Table (path | action | owner | slice | why | evidence) ## do_not_touch ## Files read\n";
    p += "No row cap that silently drops files — group by directory and state the grouping.\n";
    p
}

fn skeptic_prompt(prior, heading, design_text) {
    let p = law(prior);
    p += "Adversarial skeptic. Heading: ";
    p += heading;
    p += "\nRe-open live paths named in the shard. Do not trust the shard text alone.\n";
    p += "overnuke=true ONLY if THIS shard tickets CHARTER creed / portraits-as-voice / jsonl schema / desk.md snapshot, ";
    p += "deletes protocol fly fallback, restores two kRPC writers, idles the pad, deletes Learn/bind tape, ";
    p += "or schedules edits to hop.py / hop_factory.py / hop_factory_pad.py / physics_warp.py / pad.py / splash.py / science.py pulse law.\n";
    p += "undernuke=true ONLY if THIS heading's job is unfinished on disk given its own rows. ";
    p += "A comms shard need not archive lessons.md. A lessons shard MUST stop append and inject. ";
    p += "A cards shard MUST retire spotter as a spawnable card if it claims leftover roles. ";
    p += "Fail closed: missing evidence = both false.\nSHARD (full):\n";
    p += design_text;
    p += "\n";
    p
}

fn apply_prompt(prior, stamp, sl_json, merge_json) {
    let p = law(prior);
    p += "You APPLY one slice. Isolation none. capability all. ";
    p += "A desk that changes the checkout commits it. One commit, message: org-rsi slice <n> <title>.\n";
    p += "Do not Hangar. Do not fly. Do not write CHARTER creed, slate, pulse .py listed in law(), GameData, persistent.sfs, .craft.\n";
    p += "ARCHIVE = git mv into docs/archive/";
    p += stamp;
    p += "-org-rsi/ (mkdir if needed). ";
    p += "NUKE = delete or one-line stub; only after tests that required the body are rewritten. ";
    p += "REWRITE = edit that file as edits says. MOVE = field onto a ticket payload or packet skim, then stop writing the board. ";
    p += "OPEN-TICKET = python main.py tickets open with type/desk/fingerprint from edits — do not implement pulse. ";
    p += "KEEP/TAPE/LEAVE = do not edit that path this slice.\n";
    p += "Hank owner: tickets open only. Lars owner: OPEN-TICKET only, no pulse files. ";
    p += "Mortimer: PROTOCOL / OPS / BRIEF / AGENTS / job cards. Wernher: .py / tests / inventory / git mv.\n";
    p += "After edits, if you touched .py or tests: source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\n";
    p += "Fix tests that pinned leftover prose. Do not weaken f013 or empty-card wait.\n";
    p += "Do not write docs/program/org-rsi.md or any new live org novel.\nSLICE:\n";
    p += sl_json;
    p += "\nMERGE (context only):\n";
    p += merge_json;
    p += "\nReturn files changed, commit, test result.\n";
    p
}

if args == () {
    pause("verification", "Pass args.stamp (archive id). Optional prior, apply, census.");
}
if args.stamp == () {
    pause("verification", "Pass args.stamp — archive folder id, e.g. 2026-08-26.");
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

let prior = "";
if args.prior != () {
    if type_of(args.prior) == "string" {
        prior = args.prior;
    }
}

let apply_wanted = false;
if args.apply == true {
    apply_wanted = true;
}

let do_census = true;
if prior != "" {
    do_census = false;
}
if args.census == true {
    do_census = true;
}
if args.census == false {
    do_census = false;
}

let archive_dir = "docs/archive/";
archive_dir += stamp;
archive_dir += "-org-rsi";

let census_blob = "";
let cov_blob = "";
let harvest_blob = "";
let comms_blob = "";
let classify_blob = "";
let friction_blob = "";

if do_census {
    phase("Census");
    let cjobs = [];
    cjobs.push(#{
        label: "census-program-md",
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: census_prompt(
            prior,
            "docs/program live markdown (not tickets json bodies)",
            "list_dir docs/program. wc every *.md. Dual boards (plan/science/vab/world-model). RSI novels if present. Which a cold hire is told to open. Compare docs_inventory.py classes vs live names.",
            "- docs/program/ (list_dir)\n- docs/program/OPS.md\n- docs/program/PROTOCOL.md Files + Return + Spawn packet\n- docs/program/world-model.md first 40 and last 40\n- docs_inventory.py DOC_CLASSES FORBIDDEN_DISPATCH\n- AGENTS.md packet skim"
        ),
    });
    cjobs.push(#{
        label: "census-missions",
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: census_prompt(
            prior,
            "docs/missions identity and tape dest",
            "current.md flight slug. INDEX. Where uncrewed hops write logs (kerbal-named folder vs campaign). Dual plan/science/craft/briefing with docs/program. Count dated logs vs last crewed log line. Do not dump jsonl.",
            "- docs/program/current.md\n- docs/missions/INDEX.md\n- docs/missions/ (list_dir, not log bodies)\n- docs/flights/README.md\n- tickets.py attach_run / live_run path\n- flightlog.py seated_logs_dir if present"
        ),
    });
    cjobs.push(#{
        label: "census-cards",
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: census_prompt(
            prior,
            ".grok/agents job cards and leftover roles",
            "wc every card. Who is still spawnable vs DEPRECATED. Return fences vs PROTOCOL findings. Who still lists BOARD.md, lessons.md, world-model, note-tech as Inputs. First-command prefixes.",
            "- .grok/agents/ (list_dir + wc)\n- AGENTS.md spawn table\n- docs/program/tickets/BRIEF.md\n- docs/crew/builder.md if present"
        ),
    });
    cjobs.push(#{
        label: "census-lessons-inject",
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: census_prompt(
            prior,
            "lessons.md + what a cold child actually loads",
            "wc and grep ^## on docs/lessons.md. Who APPENDS vs who is told to READ the whole file as miss physics. Packet skim vs job-card Inputs. agents_md false vs still opening lessons. agent-notes.md vs lessons.",
            "- docs/lessons.md header + grep ^##\n- docs/agent-notes.md header\n- AGENTS.md lines that name lessons.md\n- .grok/agents/lars.md After a miss\n- .grok/agents/wernher.md miss heading\n- docs/program/PROTOCOL.md lessons line\n- docs/program/OPS.md lessons line\n- docs/program/tickets/BRIEF.md lessons line\n- tickets.py packet() skim\n- tests that read lessons.md"
        ),
    });
    cjobs.push(#{
        label: "census-tickets-writers",
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: census_prompt(
            prior,
            "ticket bus vs leftover markdown boards + kernel md writers",
            "What already lives on tickets (go/cli/campaign/learn/capable/bind/findings). What still last-writes a board. grep Path write / write_text / append for docs/*.md in review.py desk.py tickets.py protocol.py ops.py main.py. attach-run dest.",
            "- docs/program/tickets/BRIEF.md\n- tickets.py packet() TYPES ID_PREFIX attach_run\n- protocol.py fly_gate\n- review.py write_review\n- desk.py write desk.md\n- docs/program/ship.md first 15\n- docs/program/tickets/BOARD.md first 20"
        ),
    });
    cjobs.push(#{
        label: "census-control-inventory",
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: census_prompt(
            prior,
            "control-file inventory only (do not retune)",
            "wc hop.py hop_factory.py hop_factory_pad.py physics_warp.py pad.py splash.py science.py blocks.md. Who owns pulse vs blocks vs immortal factory. Inventory only — do not recommend a rewrite of pulse law.",
            "- hop_factory.py header\n- hop_factory_pad.py header\n- hop.py first 40\n- physics_warp.py first 30\n- docs/program/blocks.md first 40\n- .grok/agents/lars.md Where the cause lives\n- .grok/agents/wernher.md control blocks"
        ),
    });
    let compiles = parallel(cjobs);
    let ci = 0;
    for r in compiles {
        let nm = "census-";
        nm += ci.to_string();
        nm += ".md";
        let body = text_of(r);
        persist(nm, body);
        census_blob += "\n\n===== CENSUS ";
        census_blob += ci.to_string();
        census_blob += " scratch=";
        census_blob += nm;
        census_blob += " =====\n";
        census_blob += body;
        ci += 1;
    }
    persist("census.md", census_blob);
    log("census slots=" + ci.to_string());
    log_budget("after-census");
} else {
    phase("Coverage");
    let cov_r = agent(coverage_prompt(prior), #{
        label: "coverage-index",
        agent_type: "org-review",
        capability_mode: "read-only",
    });
    cov_blob = text_of(cov_r);
    persist("coverage.md", cov_blob);
    log("coverage done");
    log_budget("after-coverage");
}

phase("Harvest");
let har_r = agent(harvest_prompt(prior), #{
    label: "harvest-disk",
    agent_type: "org-review",
    capability_mode: "read-only",
});
harvest_blob = text_of(har_r);
persist("harvest.md", harvest_blob);
log("harvest done");

if do_census {
    phase("Comms");
    let com_r = agent(comms_prompt(prior), #{
        label: "comms-house",
        agent_type: "org-review",
        capability_mode: "read-only",
    });
    comms_blob = text_of(com_r);
    persist("comms.md", comms_blob);

    phase("Classify");
    let cljobs = [];
    cljobs.push(#{
        label: "classify-program-agents",
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: classify_prompt(
            prior,
            "docs/program + AGENTS.md + .grok/agents",
            "- docs/program/ (list_dir, wc md)\n- AGENTS.md\n- .grok/agents/\n- docs_inventory.py",
            "Constitution and packet skim KEEP; RSI novels ARCHIVE or NUKE; BOARD dump vs its writer."
        ),
    });
    cljobs.push(#{
        label: "classify-missions-lessons",
        agent_type: "org-review",
        capability_mode: "read-only",
        prompt: classify_prompt(
            prior,
            "missions, lessons, crew, press, flights",
            "- docs/missions/ (list_dir, not log bodies)\n- docs/lessons.md header\n- docs/crew/ (portraits vs log/)\n- docs/press/\n- docs/flights/\n- docs/agent-notes.md header",
            "Tape stays TAPE. Portraits KEEP. lessons.md is the injection question — measure before NUKE."
        ),
    });
    let clres = parallel(cljobs);
    let cli = 0;
    for r in clres {
        let nm = "classify-";
        nm += cli.to_string();
        nm += ".md";
        let body = text_of(r);
        persist(nm, body);
        classify_blob += "\n\n===== CLASSIFY ";
        classify_blob += cli.to_string();
        classify_blob += " =====\n";
        classify_blob += body;
        cli += 1;
    }
    persist("classify.md", classify_blob);

    phase("Friction");
    let fr_r = agent(friction_prompt(prior), #{
        label: "friction-next-hire",
        agent_type: "org-review",
        capability_mode: "read-only",
    });
    friction_blob = text_of(fr_r);
    persist("friction.md", friction_blob);
    log_budget("after-census-side");
}

phase("Design");
let djobs = [];
djobs.push(#{
    label: "design-comms-inject",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: design_prompt(
        prior,
        "comms-law + injection-law + hank-in-between",
        "Who talks to whom; what a cold hire loads; what Hank still opens to run ops next. Packet vs parent vs job-card Inputs. TUI vs hop pid vs ship.md vs screenshot.",
        "- comms.md\n- interviews.md\n- census.md\n- friction.md\n",
        "- AGENTS.md When to spawn + packet + TUI 1 Hz / phase edges\n- docs/program/PROTOCOL.md Spawn packet + Handoffs + Files + Feedback\n- docs/program/OPS.md split of power\n- tickets.py packet() skim\n- .grok/agents/hank.md first command\n- docs/program/desk.md first 40\n- docs/program/ship.md first 20\n- docs/program/tickets/BRIEF.md\n"
    ),
});
djobs.push(#{
    label: "design-keep-tape",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: design_prompt(
        prior,
        "KEEP + TAPE",
        "What the next hire must still read as prose, vs evidence that stays on disk and is never injected.",
        "- classify.md\n- census.md\n",
        "- docs/program/ (list_dir, wc every md)\n- docs/program/tickets/\n- docs/crew/log/ (names only)\n- docs/flights/\n- docs/program/ship.md first 15\n- CHARTER.md (read only)\n- docs/program/slate.md (read only)\n"
    ),
});
djobs.push(#{
    label: "design-archive-nuke",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: design_prompt(
        prior,
        "ARCHIVE + NUKE",
        "What must leave the live tree this sit, vs delete/stub. Inventory leftover vs live. RSI novels. leftover roles. sit-card. BOARD dump vs its writer.",
        "- classify.md\n- harvest.md\n- friction.md\n",
        "- docs/program/ (rsi papers, org-flow, leftover md)\n- docs_inventory.py DOC_CLASSES FORBIDDEN_DISPATCH\n- .grok/agents/spotter.md\n- docs/crew/builder.md\n- docs/program/sit-card.json\n- tickets.py board md writer if any\n"
    ),
});
djobs.push(#{
    label: "design-move-tickets",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: design_prompt(
        prior,
        "MOVE to tickets",
        "Content that already is or should be a ticket field/finding, not a board. Dual plan/science/vab/world-model open questions. Packet extras.",
        "- census.md\n- classify.md\n- comms.md\n",
        "- tickets.py packet() infer_links TYPES ID_PREFIX findings close_why\n- protocol.py fly_gate\n- docs/program/plan.md vs seated plan if present\n- docs/program/science.md vs seated science if present\n- docs/program/vab.md\n- docs/program/world-model.md Open questions last heading\n"
    ),
});
djobs.push(#{
    label: "design-lessons",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: design_prompt(
        prior,
        "lessons.md replacement",
        "The next Lars hire must not open the lessons novel as miss physics. Append, inject, tests that pin the file, heading twins. Replacement the next hire actually reads. Do not delete Learn tape.",
        "- census.md\n- friction.md\n- classify.md\n",
        "- docs/lessons.md header + grep ^## count\n- AGENTS.md lines that name lessons.md\n- .grok/agents/lars.md After a miss\n- .grok/agents/wernher.md miss heading\n- docs/program/PROTOCOL.md lessons line\n- docs/program/OPS.md lessons line\n- docs/program/tickets/BRIEF.md lessons line\n- tests that read lessons.md\n- docs/agent-notes.md header\n"
    ),
});
djobs.push(#{
    label: "design-mission-id",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: design_prompt(
        prior,
        "mission identity",
        "Stop naming uncrewed tape after a kerbal seat. attach-run dest, seated logs dir, current.md, INDEX, flights/. Do not ticket jsonl schema.",
        "- census.md\n- friction.md\n- interviews.md\n",
        "- docs/program/current.md\n- docs/missions/INDEX.md\n- docs/missions/ (list_dir, not log bodies)\n- tickets.py attach_run / live_run path\n- docs/flights/README.md\n- docs/program/GLOSSARY.md mission line\n- CHARTER.md logs path (read only — do not schedule a creed rewrite)\n"
    ),
});
djobs.push(#{
    label: "design-cards",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: design_prompt(
        prior,
        "job-card cuts",
        "What to delete from cards so the next hire is minutes. leftover roles. prefixes S/M/C vs T. Return fences vs findings. Do not rewrite portraits-as-voice.",
        "- census.md\n- interviews.md\n- comms.md\n",
        "- .grok/agents/ (list_dir + wc every card)\n- AGENTS.md spawn table\n- docs/program/tickets/BRIEF.md first command\n- .grok/agents/lars.md .grok/agents/hank.md .grok/agents/gene.md .grok/agents/wernher.md first command + Return\n- docs/crew/builder.md\n"
    ),
});
djobs.push(#{
    label: "design-live-radio",
    agent_type: "org-review",
    capability_mode: "read-only",
    prompt: design_prompt(
        prior,
        "live radio + pad occupancy + hop-light vs airborne",
        "How the parent knows the rocket is flying. ship.md is radio. One stuck PNG when sit/MET/log disagree. hop light is not airborne. Do not wait on hop stdout. TUI phase start/end/unexpected. Do not retune pulse this run — OPEN-TICKET if the helper must print plume. Sequence leftover slices in Merge.",
        "- harvest.md\n- friction.md\n- comms.md\n",
        "- AGENTS.md TUI / screenshot stuck / ship.md / lock-live status GET\n- .grok/agents/hank.md first command + radio\n- docs/program/ship.md first 20\n- docs/program/PROTOCOL.md Handoffs + Files\n- hop_factory_pad.py hop light / _pad_plume header (read, do not edit)\n- screenshots/ (list_dir names only)\n- docs/last-flight.md if present (gitignored — MISSING is valid)\n"
    ),
});

let designs = parallel(djobs);
log("design slots=8");
log_budget("after-design");

let headings = [
    "comms-law + injection-law + hank-in-between",
    "KEEP + TAPE",
    "ARCHIVE + NUKE",
    "MOVE to tickets",
    "lessons.md replacement",
    "mission identity",
    "job-card cuts",
    "live radio + pad occupancy + hop-light vs airborne",
];

let design_texts = [];
let design_blob = "";
let di = 0;
for r in designs {
    let body = text_of(r);
    let nm = "design-";
    nm += di.to_string();
    nm += ".md";
    persist(nm, body);
    design_texts.push(body);
    design_blob += "\n\n===== DESIGN ";
    design_blob += di.to_string();
    design_blob += " scratch=";
    design_blob += nm;
    design_blob += " =====\n";
    design_blob += body;
    di += 1;
}
persist("design-shards.md", design_blob);

phase("Skeptics");
let sjobs = [];
let hi = 0;
for r in designs {
    let h = headings[hi];
    let shard = "";
    if hi < design_texts.len() {
        shard = design_texts[hi];
    } else {
        shard = text_of(r);
    }
    sjobs.push(#{
        label: "skeptic-" + hi.to_string(),
        agent_type: "org-review",
        capability_mode: "read-only",
        output_schema: skeptic_schema,
        prompt: skeptic_prompt(prior, h, shard),
    });
    hi += 1;
}
let skeptics = parallel(sjobs);
log("skeptics done");
log_budget("after-skeptics");

let sk_blob = "";
let overnuke = false;
let skeptics_ok = true;
let si = 0;
for v in skeptics {
    let nm = "skeptic-";
    nm += si.to_string();
    nm += ".json";
    persist(nm, encode_out(v));
    sk_blob += "\n\n===== SKEPTIC ";
    sk_blob += si.to_string();
    sk_blob += " =====\n";
    sk_blob += encode_out(v);
    if v == () {
        skeptics_ok = false;
        log("skeptic slot empty — fail closed");
    } else {
        if v.success != true {
            skeptics_ok = false;
            log("skeptic slot fail — fail closed");
        } else {
            if v.output == () {
                skeptics_ok = false;
            } else {
                if v.output.overnuke == true {
                    overnuke = true;
                }
            }
        }
    }
    si += 1;
}
persist("skeptics.json", sk_blob);
if overnuke {
    log("overnuke true — apply will halt");
}
if skeptics_ok != true {
    log("skeptics incomplete — apply will halt");
}

phase("Merge");
let merge_p = law(prior);
merge_p += "You are Mortimer Grokman, CEO. MERGE only. Do not edit the repo. Do not fly.\n";
merge_p += "Thin merge: sequence, owners, file lists, do-not-touch, apply flag. FORBIDDEN to rewrite shard tables.\n";
merge_p += "Read live: docs_inventory.py classify, PROTOCOL.md Spawn packet, OPS.md split of power, AGENTS.md spawn table, ";
merge_p += "tickets.py packet() + ID_PREFIX, docs/lessons.md header, docs/program/current.md, CHARTER.md RSI paragraph (read only).\n";
merge_p += "If any skeptic overnuke=true OR a skeptic slot is EMPTY/FAIL, set apply=false and halt_reason. ";
merge_p += "Do not schedule blocked pulse files or CHARTER.md or slate.md.\n";
merge_p += "If apply is allowed, emit at most 8 slices, pad-safe, non-overlapping files when possible. ";
merge_p += "Slice 1 must unpin tests that would fail when lessons/novels move. ";
merge_p += "Wernher owns .py / tests / inventory / git mv of docs. Mortimer owns PROTOCOL OPS BRIEF AGENTS job cards. ";
merge_p += "Hank may open tickets only. Lars OPEN-TICKET compose only — no pulse files.\n";
merge_p += "Drop a row rather than write hop.py. Tickets array: at most 6 later opens, do not open them here.\n";
merge_p += "skeptics_ok=";
merge_p += skeptics_ok.to_string();
merge_p += " overnuke=";
merge_p += overnuke.to_string();
merge_p += " apply_wanted=";
merge_p += apply_wanted.to_string();
merge_p += " archive_dir=";
merge_p += archive_dir;
merge_p += "\nCOVERAGE:\n";
merge_p += cov_blob;
merge_p += "\nCENSUS:\n";
merge_p += census_blob;
merge_p += "\nHARVEST:\n";
merge_p += harvest_blob;
merge_p += "\nCOMMS:\n";
merge_p += comms_blob;
merge_p += "\nCLASSIFY:\n";
merge_p += classify_blob;
merge_p += "\nFRICTION:\n";
merge_p += friction_blob;
merge_p += "\nDESIGNS:\n";
merge_p += design_blob;
merge_p += "\nSKEPTICS:\n";
merge_p += sk_blob;
merge_p += "\n";
let merge_r = agent(merge_p, #{
    label: "merge-org-rsi",
    agent_type: "mortimer",
    capability_mode: "read-only",
    output_schema: merge_schema,
});
log("merge done");
let merge_json = encode_out(merge_r);
persist("merge.json", merge_json);

let do_apply = apply_wanted;
if overnuke {
    do_apply = false;
}
if skeptics_ok != true {
    do_apply = false;
}
if merge_r == () {
    do_apply = false;
} else {
    if merge_r.success != true {
        do_apply = false;
    } else {
        if merge_r.output == () {
            do_apply = false;
        } else {
            if merge_r.output.apply == false {
                do_apply = false;
            }
        }
    }
}

let slices = [];
if merge_r != () {
    if merge_r.success == true {
        if merge_r.output != () {
            if merge_r.output.slices != () {
                for sl in merge_r.output.slices {
                    slices.push(sl);
                }
            }
        }
    }
}
log("slices=" + slices.len().to_string() + " do_apply=" + do_apply.to_string());
log_budget("after-merge");

let apply_blob = "";
if do_apply {
    phase("Apply");
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
            if type_of(sl.edits) == "string" {
                edits = sl.edits;
            }
        }
        let skip = false;
        if files.len() == 0 {
            skip = true;
        }
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
            let ap = apply_prompt(prior, stamp, sl_json, merge_json);
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
} else {
    log("apply skipped");
    let skip_txt = "APPLY SKIPPED\n";
    skip_txt += merge_json;
    persist("apply.md", skip_txt);
    apply_blob = skip_txt;
}

phase("Verify");
let test_p = law(prior);
test_p += "VERIFY unit tests. source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\n";
test_p += "If apply ran, quote failures and FIX tests or kernel to match the merge — do not weaken f013. Do not fly. Do not Hangar.\n";
test_p += "If apply skipped, still run the tests; do not edit unless they are already failing.\n";
test_p += "MERGE:\n";
test_p += merge_json;
test_p += "\nAPPLY:\n";
test_p += apply_blob;
test_p += "\n";
let test_r = agent(test_p, #{
    label: "verify-unittests",
    capability_mode: "all",
    agent_type: "wernher",
});
log("tests done");

let sk_over_p = law(prior);
sk_over_p += "Post-apply overnuke. real=true only if git diff / live tree shows CHARTER creed rewrite, pulse .py law edit, two kRPC writers, protocol fly fallback deleted, GameData, persistent.sfs, or a new live docs/program org novel (not archive). Else real=false with paths. Fail closed.\nMERGE:\n";
sk_over_p += merge_json;
sk_over_p += "\nAPPLY:\n";
sk_over_p += apply_blob;
sk_over_p += "\n";
let sk_under_p = law(prior);
sk_under_p += "Post-apply undernuke. real=true if apply ran AND (a cold child packet or Lars After a miss still names docs/lessons.md as miss physics, OR .grok/agents/spotter.md is still a spawnable card in the AGENTS.md spawn table, OR BOARD.md is still packet skim, OR live RSI novels still sit in docs/program/ as dispatch). If apply skipped, real=false. Fail closed. Re-open the live files.\n";
let post_sk = parallel([
    #{ label: "post-overnuke", agent_type: "org-review", capability_mode: "read-only", output_schema: verdict_schema, prompt: sk_over_p },
    #{ label: "post-undernuke", agent_type: "org-review", capability_mode: "read-only", output_schema: verdict_schema, prompt: sk_under_p },
]);
persist("post-overnuke.json", encode_out(post_sk[0]));
persist("post-undernuke.json", encode_out(post_sk[1]));

let tests_bad = false;
if test_r == () {
    tests_bad = true;
} else {
    if test_r.success != true {
        tests_bad = true;
    }
}
let under_bad = false;
if post_sk[1] != () {
    if post_sk[1].success == true {
        if post_sk[1].output != () {
            if post_sk[1].output.real == true {
                under_bad = true;
            }
        }
    }
}
let over_bad = false;
if post_sk[0] != () {
    if post_sk[0].success == true {
        if post_sk[0].output != () {
            if post_sk[0].output.real == true {
                over_bad = true;
            }
        }
    }
}

let fix_blob = "";
if do_apply {
    if tests_bad || under_bad || over_bad {
        phase("Fix");
        let fix_p = law(prior);
        fix_p += "ONE fix round. Isolation none. Commit. Do not Hangar. Do not pulse .py. Do not CHARTER creed.\n";
        fix_p += "tests_bad=";
        fix_p += tests_bad.to_string();
        fix_p += " undernuke=";
        fix_p += under_bad.to_string();
        fix_p += " overnuke=";
        fix_p += over_bad.to_string();
        fix_p += "\nRe-run: source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\nMERGE:\n";
        fix_p += merge_json;
        fix_p += "\nTESTS:\n";
        fix_p += text_of(test_r);
        fix_p += "\nPOST-SKEPTICS:\n";
        fix_p += encode_out(post_sk[0]);
        fix_p += "\n";
        fix_p += encode_out(post_sk[1]);
        fix_p += "\n";
        let fix_jobs = [];
        if over_bad {
            let fp0 = fix_p;
            fp0 += "You are Wernher. REVERT any denylist hit (CHARTER creed, slate, pulse .py, GameData, persistent.sfs) and any new live docs/program org novel. Commit the revert. Do not retune pulse law.\n";
            fix_jobs.push(#{
                label: "fix-revert",
                agent_type: "wernher",
                capability_mode: "all",
                prompt: fp0,
            });
        }
        if tests_bad {
            if over_bad != true {
                fix_jobs.push(#{
                    label: "fix-kernel",
                    agent_type: "wernher",
                    capability_mode: "all",
                    prompt: fix_p,
                });
            }
        }
        if under_bad {
            if over_bad != true {
                let fp2 = fix_p;
                fp2 += "You are Mortimer. Finish inject/card/PROTOCOL holes the undernuke named. Do not edit hop.py. Do not write a live program novel.\n";
                fix_jobs.push(#{
                    label: "fix-docs",
                    agent_type: "mortimer",
                    capability_mode: "all",
                    prompt: fp2,
                });
            }
        }
        if fix_jobs.len() > 0 {
            let fixes = parallel(fix_jobs);
            for fr in fixes {
                fix_blob += text_of(fr);
                fix_blob += "\n";
            }
        }
        persist("fix.md", fix_blob);
        let retest_p = law(prior);
        retest_p += "Re-run unit tests after fix. source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\nFix remaining test-only breakage. Do not fly.\n";
        let retest_r = agent(retest_p, #{
            label: "retest",
            capability_mode: "all",
            agent_type: "wernher",
        });
        test_r = retest_r;
    }
}

phase("Report");
let report_name = "REPORT.md";
if do_apply {
    report_name = "APPLIED.md";
}
let rep = law(prior);
rep += "You are Mortimer Grokman, CEO. Write the report to ";
rep += archive_dir;
rep += "/";
rep += report_name;
rep += " (create the directory). Also one dated line in docs/crew/log/mortimer.md. ";
rep += "Do NOT write docs/program/org-rsi.md or any new live docs/program org novel. ";
rep += "Do not Hangar. Do not open tickets unless merge.tickets named them AND apply ran — then open at most those, type/desk/fingerprint, no pulse work.\n";
rep += "Stand-alone. Verify counts you cite. Sections: 1 Sit 2 What changed (path | action) 3 Injection after 4 Tests 5 Skeptics 6 Tickets opened or deferred 7 Open risks 8 This did not retune pulse / CHARTER creed.\n";
rep += "do_apply=";
rep += do_apply.to_string();
rep += " overnuke=";
rep += overnuke.to_string();
rep += " skeptics_ok=";
rep += skeptics_ok.to_string();
rep += " stamp=";
rep += stamp;
rep += "\nCOVERAGE:\n";
rep += cov_blob;
rep += "\nCENSUS:\n";
rep += census_blob;
rep += "\nHARVEST:\n";
rep += harvest_blob;
rep += "\nMERGE:\n";
rep += merge_json;
rep += "\nAPPLY:\n";
rep += apply_blob;
rep += "\nTESTS:\n";
rep += text_of(test_r);
rep += "\nPOST-SKEPTICS:\n";
rep += encode_out(post_sk[0]);
rep += "\n";
rep += encode_out(post_sk[1]);
rep += "\nFIX:\n";
rep += fix_blob;
rep += "\nDESIGNS:\n";
rep += design_blob;
rep += "\nSKEPTICS:\n";
rep += sk_blob;
rep += "\n";
let report_r = agent(rep, #{
    label: "report-org-rsi",
    agent_type: "mortimer",
    capability_mode: "read-write",
});
let report = text_of(report_r);
if report == "" {
    report = "# Org RSI\n\nEMPTY report agent. Merge follows.\n\n";
    report += merge_json;
}
let report_scratch = persist("org-rsi-report.md", report);

let tests_ok = false;
if test_r != () {
    if test_r.success == true {
        tests_ok = true;
    }
}
let merge_ok = false;
if merge_r != () {
    if merge_r.success == true {
        merge_ok = true;
    }
}

complete(#{
    path: report_scratch,
    apply: do_apply,
    overnuke: overnuke,
    skeptics_ok: skeptics_ok,
    merge_ok: merge_ok,
    tests_ok: tests_ok,
    slices: slices.len(),
    prior: prior,
    stamp: stamp,
    census: do_census,
    archive: archive_dir,
});
