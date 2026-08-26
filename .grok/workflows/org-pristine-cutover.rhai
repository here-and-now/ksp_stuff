let meta = #{
    name: "org-pristine-cutover",
    description: "From the parked org-pristine census, design uncapped shards then apply a ticket-bus org. No live program novel.",
    when_to_use: "When org-pristine census is parked under docs/archive/2026-08-26-org-pristine/ and Os wants the house cut over, not another letter",
    phases: [
        #{ title: "Coverage", detail: "prior index vs live tree; gaps only" },
        #{ title: "Design", detail: "one shard per original heading group; disk wins" },
        #{ title: "Skeptics", detail: "overnuke / undernuke per shard" },
        #{ title: "Merge", detail: "pad-safe slices, apply flag" },
        #{ title: "Apply", detail: "Wernher kernel then Mortimer cards; git mv archive" },
        #{ title: "Verify", detail: "unit tests plus post-apply skeptics" },
        #{ title: "Fix", detail: "one round if tests or undernuke fail" },
        #{ title: "Report", detail: "archive APPLIED.md — not docs/program" },
    ],
};

let row_schema = #{
    "type": "object",
    "required": ["path", "action", "why", "owner", "slice"],
    "properties": #{
        "path": #{ "type": "string" },
        "action": #{ "type": "string" },
        "why": #{ "type": "string" },
        "owner": #{ "type": "string" },
        "slice": #{ "type": "integer" },
        "evidence": #{ "type": "string" },
    },
};

let design_schema = #{
    "type": "object",
    "required": ["heading", "rows"],
    "properties": #{
        "heading": #{ "type": "string" },
        "rows": #{
            "type": "array",
            "maxItems": 80,
            "items": row_schema,
        },
        "notes": #{ "type": "string" },
        "do_not_touch": #{
            "type": "array",
            "maxItems": 24,
            "items": #{ "type": "string" },
        },
    },
};

let coverage_schema = #{
    "type": "object",
    "required": ["ok", "prior_read"],
    "properties": #{
        "ok": #{ "type": "boolean" },
        "prior_read": #{ "type": "boolean" },
        "gaps": #{
            "type": "array",
            "maxItems": 40,
            "items": #{
                "type": "object",
                "required": ["path", "note"],
                "properties": #{
                    "path": #{ "type": "string" },
                    "note": #{ "type": "string" },
                },
            },
        },
    },
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
            "maxItems": 20,
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
    let g = p.index_of("GameData");
    if g >= 0 { return true; }
    let c = p.index_of("/crafts/");
    if c >= 0 { return true; }
    let c2 = p.index_of("crafts/");
    if c2 == 0 { return true; }
    false
}

fn law() {
    let p = "";
    p += "Repo /home/os/gits/ksp_stuff. Isolation none. ";
    p += "NO kRPC. NO python main.py phase/pad/hop/ksc/recover-probe/load/Hangar. ";
    p += "NO GameData. NO persistent.sfs. NO CHARTER creed rewrite. NO slate goal rewrite. ";
    p += "NO hop.py / hop_factory.py / hop_factory_pad.py / physics_warp.py / pad.py / splash.py / science.py pulse retune. ";
    p += "Do not answer from memory. Use read_file, list_dir, grep. Missing path = MISSING. ";
    p += "Empty is valid only after you searched. NO LINE CAP. NO TOKEN CAP. Write the tables you need. Cite path:line. ";
    p += "No jsonl dump. Crew logs: grep counts + last 40 lines, not the whole file. ";
    p += "docs/archive/ is PARKED — say PARKED when you open it. ";
    p += "Prior notes live at docs/archive/2026-08-26-org-pristine/ (README first). They are an UNTRUSTED index. ";
    p += "Open those files as a bibliography, then verify on live disk. Disk wins on conflict. ";
    p += "Do not copy a KEEP/NUKE/TAPE class until you opened the live path. ";
    p += "Do not open discarded/design.md, discarded/plan-tight.md, discarded/org-pristine.md, discarded/skeptics.md as law. ";
    p += "Os intent (brief, not proven facts): ticket bus is comms; MD only when a ticket cannot hold it; rip stale; ";
    p += "do not inject lessons as miss physics; uncrewed tape should not be named after a kerbal seat; spotter is retired; ";
    p += "Lars compose from a Wernher catalog is a later ticket — not a pulse retune this run. ";
    p += "Keep: learn-rsi attach-run, lars-rsi S/M/C prefixes + hop_factory_pad.py as the pad-RF file, pad occupancy, depth 1, one control writer. ";
    p += "Do not restore spotter, Gene merge, Batch Learn, Return keys, need_*. ";
    p += "Do not leave a new live docs/program/*.md org novel. Reports go to archive or workflow scratch.\n";
    p
}

fn design_prompt(heading, focus, prior_files, live_paths) {
    let p = law();
    p += "You DESIGN one shard. Read-only. Do not edit. Do not fly. Do not open tickets.\n";
    p += "Heading you own: ";
    p += heading;
    p += "\nFocus: ";
    p += focus;
    p += "\nMUST read, in order: docs/archive/2026-08-26-org-pristine/README.md then these prior files:\n";
    p += prior_files;
    p += "\nThen list_dir + read live:\n";
    p += live_paths;
    p += "\nFill rows. action is exactly one of KEEP TAPE ARCHIVE NUKE REWRITE MOVE OPEN-TICKET LEAVE. ";
    p += "owner is mortimer, wernher, hank, or lars. slice is 1-8. ";
    p += "Pad-safe: tests that pin a file must REWRITE before NUKE/ARCHIVE of that file. ";
    p += "OPEN-TICKET for anything that would retune pulse law. Max 80 rows; overflow grouped in notes. ";
    p += "do_not_touch: paths this shard refuses to schedule.\n";
    p
}

fn skeptic_prompt(heading, design_json) {
    let p = law();
    p += "Adversarial skeptic. Heading: ";
    p += heading;
    p += "\nRe-open live paths named in the shard. Do not trust the JSON alone.\n";
    p += "overnuke=true ONLY if THIS shard tickets CHARTER/portraits/jsonl schema/desk.md snapshot, ";
    p += "deletes protocol fly fallback, restores two kRPC writers, idles the pad, deletes Learn/bind tape, ";
    p += "or schedules edits to hop.py / hop_factory.py / hop_factory_pad.py / physics_warp.py / pad.py / splash.py / science.py pulse law.\n";
    p += "undernuke=true ONLY if THIS heading's job is unfinished on disk given its own rows. ";
    p += "A comms shard need not archive lessons.md. A lessons shard MUST stop append and inject. ";
    p += "A cards shard MUST retire spotter as a spawnable card if it claims leftover roles. ";
    p += "Fail closed: missing evidence = both false.\nSHARD:\n";
    p += design_json;
    p += "\n";
    p
}

fn apply_prompt(sl_json, merge_json) {
    let p = law();
    p += "You APPLY one slice. Isolation none. capability all. ";
    p += "A desk that changes the checkout commits it (Os 2026-08-25). One commit, message: org-pristine-cutover slice <n> <title>.\n";
    p += "Do not Hangar. Do not fly. Do not write CHARTER creed, slate, pulse .py listed in law(), GameData, persistent.sfs, .craft.\n";
    p += "ARCHIVE = git mv into docs/archive/2026-08-26-docs-cutover/ (mkdir). ";
    p += "NUKE = delete or one-line stub; only after tests that required the body are rewritten. ";
    p += "REWRITE = edit that file as `edits` says. MOVE = field onto a ticket payload or packet skim, then stop writing the board. ";
    p += "OPEN-TICKET = python main.py tickets open with type/desk/fingerprint from edits — do not implement pulse. ";
    p += "KEEP/TAPE/LEAVE = do not edit that path this slice.\n";
    p += "After edits, if you touched .py or tests: source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\n";
    p += "Fix tests that pinned leftover prose (whole-file lessons reads, Forest freeze). Do not weaken f013 or empty-card wait.\n";
    p += "Do not write docs/program/org-pristine.md or any new live org novel.\nSLICE:\n";
    p += sl_json;
    p += "\nMERGE (context only):\n";
    p += merge_json;
    p += "\nReturn files changed, commit, test result.\n";
    p
}

let prior = "docs/archive/2026-08-26-org-pristine";
let apply_edits = true;
if args != () {
    if args.prior != () {
        prior = args.prior;
    }
    if args.apply == false {
        apply_edits = false;
    }
}

phase("Coverage");
let cov_p = law();
cov_p += "Coverage only. Read ";
cov_p += prior;
cov_p += "/README.md and list_dir that directory. ";
cov_p += "list_dir live docs/program (md), .grok/agents, docs/missions (not logs), docs/crew (portraits), docs/press, docs/lessons.md, docs/agent-notes.md, AGENTS.md. ";
cov_p += "prior_read=true only if you opened the README and at least census.md + classify.md. ";
cov_p += "gaps = live md the prior notes never mention (path or basename). Test fixtures under tests/ are not gaps. ";
cov_p += "ok=true if prior_read and no unexpected live dispatch files missing from the index. ";
cov_p += "Do not classify. Do not plan.\n";
let cov_r = agent(cov_p, #{
    label: "coverage-index",
    capability_mode: "read-only",
    output_schema: coverage_schema,
});
log("coverage done");
let _cov_scratch = write_scratch_file("coverage.json", encode_out(cov_r));

phase("Design");
let djobs = [];
djobs.push(#{
    label: "design-comms-inject",
    capability_mode: "read-only",
    output_schema: design_schema,
    prompt: design_prompt(
        "comms-law + injection-law + hank-in-between",
        "Who talks to whom; what a cold hire loads; what Hank still opens to run ops next. Packet vs parent AGENTS vs job-card Inputs.",
        "- " + prior + "/comms.md\n- " + prior + "/interviews.md\n- " + prior + "/census.md\n",
        "- AGENTS.md When to spawn + packet\n- docs/program/PROTOCOL.md Spawn packet + Hank handoffs\n- docs/program/OPS.md split of power\n- tickets.py packet() skim\n- .grok/agents/hank.md first command\n- docs/program/desk.md first 40\n- docs/program/tickets/BRIEF.md\n"
    ),
});
djobs.push(#{
    label: "design-keep-tape",
    capability_mode: "read-only",
    output_schema: design_schema,
    prompt: design_prompt(
        "KEEP-MD + TAPE",
        "What the next hire must still read as prose, vs evidence that stays on disk and is never injected.",
        "- " + prior + "/classify.md\n- " + prior + "/census.md\n",
        "- docs/program/ (list_dir, wc every md)\n- docs/program/tickets/\n- docs/crew/log/ (names only)\n- docs/flights/\n- docs/program/ship.md first 15\n- docs/last-flight.md if present\n"
    ),
});
djobs.push(#{
    label: "design-archive-nuke",
    capability_mode: "read-only",
    output_schema: design_schema,
    prompt: design_prompt(
        "ARCHIVE + NUKE-LIVE",
        "What must leave the live tree this sit, vs delete/stub. Inventory leftover vs live. RSI novels. spotter. sit-card. BOARD dump vs its writer.",
        "- " + prior + "/classify.md\n- " + prior + "/harvest.md\n- " + prior + "/friction.md\n",
        "- docs/program/ (rsi papers, org-flow, RO, note-tech, BOARD.md)\n- docs_inventory.py DOC_CLASSES FORBIDDEN_DISPATCH _ORG_NOVEL_NAMES classify\n- .grok/agents/spotter.md\n- docs/crew/builder.md\n- docs/program/sit-card.json\n- tickets.py _write_board_md\n"
    ),
});
djobs.push(#{
    label: "design-move-tickets",
    capability_mode: "read-only",
    output_schema: design_schema,
    prompt: design_prompt(
        "MOVE to tickets",
        "Content that already is or should be a ticket field/finding, not a board. Dual plan/science/vab/world-model Open questions. Packet extras.",
        "- " + prior + "/census.md\n- " + prior + "/classify.md\n- " + prior + "/comms.md\n",
        "- tickets.py packet() infer_links TYPES ID_PREFIX findings close_why\n- protocol.py fly_gate\n- docs/program/plan.md vs docs/missions/jebediah/plan.md\n- docs/program/science.md vs seated science.md\n- docs/program/vab.md\n- docs/program/world-model.md Open questions last heading\n- missions.py sync_shim\n"
    ),
});
djobs.push(#{
    label: "design-lessons",
    capability_mode: "read-only",
    output_schema: design_schema,
    prompt: design_prompt(
        "lessons.md replacement",
        "The next Lars hire must not open the lessons novel as miss physics. Append, inject, tests that pin the file, heading twins. Replacement the next hire actually reads.",
        "- " + prior + "/census.md\n- " + prior + "/friction.md\n- " + prior + "/classify.md\n",
        "- docs/lessons.md header + grep ^## count\n- AGENTS.md lines that name lessons.md\n- .grok/agents/lars.md After a miss\n- .grok/agents/wernher.md miss heading\n- docs/program/PROTOCOL.md lessons line\n- docs/program/OPS.md lessons line\n- docs/program/tickets/BRIEF.md lessons line\n- tests/test_protocol.py lessons reads\n- tickets.py heading twins / lesson_headings\n- docs/agent-notes.md header\n"
    ),
});
djobs.push(#{
    label: "design-mission-id",
    capability_mode: "read-only",
    output_schema: design_schema,
    prompt: design_prompt(
        "mission identity",
        "Stop naming uncrewed tape after a kerbal seat. attach-run dest, seated_logs_dir, current.md, INDEX, flights/. Do not ticket jsonl schema.",
        "- " + prior + "/census.md\n- " + prior + "/friction.md\n- " + prior + "/interviews.md\n",
        "- docs/program/current.md\n- docs/missions/INDEX.md\n- docs/missions/jebediah/ (list_dir, not 442 logs)\n- tickets.py attach_run / live_run path\n- flightlog.py seated_logs_dir\n- missions.py seated_id\n- docs/flights/README.md\n- docs/program/GLOSSARY.md mission line\n- CHARTER.md logs path (read only — do not schedule a creed rewrite)\n"
    ),
});
djobs.push(#{
    label: "design-cards",
    capability_mode: "read-only",
    output_schema: design_schema,
    prompt: design_prompt(
        "job-card cuts",
        "What to delete from cards so the next hire is minutes. leftover roles. prefixes S/M/C vs T. Return fences vs findings. Do not rewrite portraits.",
        "- " + prior + "/census.md\n- " + prior + "/interviews.md\n- " + prior + "/comms.md\n",
        "- .grok/agents/ (list_dir + wc every card)\n- AGENTS.md spawn table\n- docs/program/tickets/BRIEF.md first command\n- .grok/agents/lars.md .grok/agents/hank.md .grok/agents/gene.md .grok/agents/wernher.md first command + Return\n- docs/crew/builder.md\n"
    ),
});
djobs.push(#{
    label: "design-compose-sequence",
    capability_mode: "read-only",
    output_schema: design_schema,
    prompt: design_prompt(
        "lars-compose ticket + sequence + do-not-touch",
        "Name the later compose ticket. Do not retune pulse this run. Order at most 8 pad-safe slices with owner. Hard do-not-touch list.",
        "- " + prior + "/harvest.md\n- " + prior + "/friction.md\n- " + prior + "/census.md\n",
        "- hop_factory.py header + run_factory_vessel line span (read, do not edit)\n- hop_factory_pad.py header\n- physics_warp.py header\n- docs/program/blocks.md first 40\n- .grok/agents/lars.md Where the cause lives\n- .grok/agents/wernher.md control blocks\n- PROTOCOL.md / OPS.md compose law\n"
    ),
});

let designs = parallel(djobs);
log("design slots=8");
let design_blob = "";
let di = 0;
for r in designs {
    design_blob += "\n\n===== DESIGN ";
    design_blob += di.to_string();
    design_blob += " =====\n";
    design_blob += encode_out(r);
    di += 1;
}
let _dscratch = write_scratch_file("design-shards.json", design_blob);

phase("Skeptics");
let sjobs = [];
let headings = [
    "comms-law + injection-law + hank-in-between",
    "KEEP-MD + TAPE",
    "ARCHIVE + NUKE-LIVE",
    "MOVE to tickets",
    "lessons.md replacement",
    "mission identity",
    "job-card cuts",
    "lars-compose ticket + sequence + do-not-touch",
];
let hi = 0;
for r in designs {
    let h = headings[hi];
    sjobs.push(#{
        label: "skeptic-" + hi.to_string(),
        capability_mode: "read-only",
        output_schema: skeptic_schema,
        prompt: skeptic_prompt(h, encode_out(r)),
    });
    hi += 1;
}
let skeptics = parallel(sjobs);
log("skeptics done");
let sk_blob = "";
let overnuke = false;
let si = 0;
for v in skeptics {
    sk_blob += "\n\n===== SKEPTIC ";
    sk_blob += si.to_string();
    sk_blob += " =====\n";
    sk_blob += encode_out(v);
    if v != () {
        if v.success == true {
            if v.output != () {
                if v.output.overnuke == true {
                    overnuke = true;
                }
            }
        }
    }
    si += 1;
}
let _sscratch = write_scratch_file("skeptics.json", sk_blob);
if overnuke {
    log("overnuke true — apply will halt");
}

phase("Merge");
let merge_p = law();
merge_p += "You are Mortimer Grokman, CEO. MERGE only. Do not edit the repo. Do not fly.\n";
merge_p += "Read docs_inventory.py classify, PROTOCOL.md Spawn packet, OPS.md split of power, AGENTS.md spawn table, tickets.py packet() + ID_PREFIX, docs/lessons.md header, docs/program/current.md, CHARTER.md RSI paragraph (read only).\n";
merge_p += "If any skeptic overnuke=true, set apply=false and halt_reason. Do not schedule blocked pulse files or CHARTER.md.\n";
merge_p += "If overnuke is false, set apply=true and emit at most 8 slices, pad-safe, non-overlapping files when possible. ";
merge_p += "Slice 1 must unpin tests that would fail when lessons/novels move. ";
merge_p += "Wernher owns .py / tests / inventory / git mv of docs. Mortimer owns PROTOCOL OPS BRIEF AGENTS job cards. ";
merge_p += "Hank may open tickets only. Lars OPEN-TICKET compose only — no pulse files.\n";
merge_p += "Drop a row rather than write hop.py. Tickets array: at most 6 later opens, do not open them here.\n";
merge_p += "COVERAGE:\n";
merge_p += encode_out(cov_r);
merge_p += "\nDESIGNS:\n";
merge_p += design_blob;
merge_p += "\nSKEPTICS:\n";
merge_p += sk_blob;
merge_p += "\n";
let merge_r = agent(merge_p, #{
    label: "merge-cutover",
    agent_type: "mortimer",
    capability_mode: "read-only",
    output_schema: merge_schema,
});
log("merge done");
let merge_json = encode_out(merge_r);
let _mscratch = write_scratch_file("merge.json", merge_json);

let do_apply = apply_edits;
if overnuke {
    do_apply = false;
}
if merge_r != () {
    if merge_r.success == true {
        if merge_r.output != () {
            if merge_r.output.apply == false {
                do_apply = false;
            }
        }
    } else {
        do_apply = false;
    }
} else {
    do_apply = false;
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
        if files.len() == 0 {
            apply_blob += "\n===== APPLY ";
            apply_blob += ai.to_string();
            apply_blob += " SKIP (no allowed files, blocked=";
            apply_blob += blocked_n.to_string();
            apply_blob += ")\n";
        } else {
            let owner = "wernher";
            if sl.owner != () {
                if sl.owner == "mortimer" {
                    owner = "mortimer";
                }
                if sl.owner == "hank" {
                    owner = "hank";
                }
                if sl.owner == "lars" {
                    owner = "lars";
                }
            }
            let sl_copy = sl;
            sl_copy.files = files;
            let sl_json = json_encode(sl_copy);
            let ap = apply_prompt(sl_json, merge_json);
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
    let _ascratch = write_scratch_file("apply.md", apply_blob);
} else {
    log("apply skipped");
    let _askip = write_scratch_file("apply.md", "APPLY SKIPPED\n" + merge_json);
}

phase("Verify");
let test_p = law();
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

let sk_over_p = law();
sk_over_p += "Post-apply overnuke. real=true only if git diff shows CHARTER creed, pulse .py law, two kRPC writers, protocol fly fallback deleted, or a new live docs/program org novel (not archive). Else real=false with paths. Fail closed.\nMERGE:\n";
sk_over_p += merge_json;
let sk_under_p = law();
sk_under_p += "Post-apply undernuke. real=true if a cold child packet or Lars After a miss still names docs/lessons.md as miss physics, OR .grok/agents/spotter.md is still a spawnable card in AGENTS.md spawn table, OR BOARD.md is still packet skim, OR apply was requested and live RSI novels still sit in docs/program/ as dispatch. If apply skipped, real=false. Fail closed. Re-open the live files.\n";
let post_sk = parallel([
    #{ label: "post-overnuke", capability_mode: "read-only", output_schema: verdict_schema, prompt: sk_over_p },
    #{ label: "post-undernuke", capability_mode: "read-only", output_schema: verdict_schema, prompt: sk_under_p },
]);

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
    if over_bad != true {
        if tests_bad || under_bad {
            phase("Fix");
            let fix_p = law();
            fix_p += "ONE fix round. Isolation none. Commit. Do not Hangar. Do not pulse .py. Do not CHARTER creed.\n";
            fix_p += "tests_bad=";
            fix_p += tests_bad.to_string();
            fix_p += " undernuke=";
            fix_p += under_bad.to_string();
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
            if tests_bad {
                fix_jobs.push(#{
                    label: "fix-kernel",
                    agent_type: "wernher",
                    capability_mode: "all",
                    prompt: fix_p,
                });
            }
            if under_bad {
                let fp2 = fix_p;
                fp2 += "You are Mortimer. Finish inject/card/PROTOCOL holes the undernuke named. Do not edit hop.py. Do not write a live program novel.\n";
                fix_jobs.push(#{
                    label: "fix-docs",
                    agent_type: "mortimer",
                    capability_mode: "all",
                    prompt: fp2,
                });
            }
            if fix_jobs.len() > 0 {
                let fixes = parallel(fix_jobs);
                for fr in fixes {
                    fix_blob += encode_out(fr);
                    fix_blob += "\n";
                }
            }
            let _fscratch = write_scratch_file("fix.md", fix_blob);
            let retest_p = law();
            retest_p += "Re-run unit tests after fix. source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\nFix remaining test-only breakage. Do not fly.\n";
            let retest_r = agent(retest_p, #{
                label: "retest",
                capability_mode: "all",
                agent_type: "wernher",
            });
            test_r = retest_r;
        }
    }
}

phase("Report");
let rep = law();
rep += "You are Mortimer Grokman, CEO. Write the apply report to docs/archive/2026-08-26-org-pristine/APPLIED.md (create). ";
rep += "Also one dated line in docs/crew/log/mortimer.md. ";
rep += "Do NOT write docs/program/org-pristine.md or any new live docs/program org novel. ";
rep += "Do not Hangar. Do not open tickets unless merge.tickets named them AND apply ran — then open at most those, type/desk/fingerprint, no pulse work.\n";
rep += "Title: Org pristine cutover — applied or halted (2026-08-26).\n";
rep += "Stand-alone. Verify counts you cite. Sections: 1 Sit 2 What changed (path | action) 3 Injection after 4 Tests 5 Skeptics 6 Tickets opened or deferred 7 Open risks 8 This did not retune pulse / CHARTER creed.\n";
rep += "do_apply=";
rep += do_apply.to_string();
rep += " overnuke=";
rep += overnuke.to_string();
rep += "\nCOVERAGE:\n";
rep += encode_out(cov_r);
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
    label: "report-applied",
    agent_type: "mortimer",
    capability_mode: "read-write",
});
let report = text_of(report_r);
if report == "" {
    report = "# Org pristine cutover\n\nEMPTY report agent. Merge follows.\n\n";
    report += merge_json;
}
let scratch = write_scratch_file("cutover-report.md", report);

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
    path: scratch,
    apply: do_apply,
    overnuke: overnuke,
    merge_ok: merge_ok,
    tests_ok: tests_ok,
    slices: slices.len(),
    prior: prior,
});
