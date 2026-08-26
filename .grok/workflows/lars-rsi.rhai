let meta = #{
    name: "lars-rsi",
    description: "Full RSI on Lars pulse factory: why hires take too long, why hop_factory is a ticket log, S/M/C ticket prefixes, then apply",
    when_to_use: "When Lars hires run 8–15 min, hop_factory grows a helper per T-id, or Os wants science/mission/craft ids off T-xxx",
    phases: [
        #{ title: "Compile", detail: "Lars file, hires, T-namespace, XOR" },
        #{ title: "Friction", detail: "helper-per-ticket, hire length, prefixes" },
        #{ title: "Interview", detail: "Lars, Hank, Wernher, Mortimer" },
        #{ title: "Design", detail: "bounded patches" },
        #{ title: "Apply", detail: "kernel prefixes, lars card, optional pad extract" },
        #{ title: "Verify", detail: "tests plus skeptics" },
        #{ title: "Report", detail: "scratch lars-rsi.md — not live docs/program/" },
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
    p += "NO kRPC. NO python main.py hop/pad/phase/recover-probe/load/Hangar. ";
    p += "NO GameData. NO persistent.sfs. NO CHARTER creed. ";
    p += "Do not answer from memory. Use read_file, list_dir, grep. Missing = MISSING. ";
    p += "Empty only after search. Token cap: MAX 55 lines. Cite path:line. ";
    p += "No jsonl dump. Crew logs: last 40 lines + grep counts. ";
    p += "Pulse LAW (sit names, warp, suicide envelope) is not this RSI unless Design explicitly extracts RF pad structure. ";
    p += "Os 2026-08-25: Lars takes too long; hop_factory unmaintainable; S-xxx science, M-xxx mission/fly, C-xxx craft; T-xxx not for those.\n";
    p
}

let apply_edits = true;
if args != () {
    if args.apply == false {
        apply_edits = false;
    }
}

phase("Compile");
let cjobs = [];
cjobs.push(#{
    label: "compile-lars-file",
    capability_mode: "read-only",
    prompt: walls() + "Historian. Desk: Lars Grokman hop_factory.py.\n"
        + "COUNT on disk: wc -l hop_factory.py; grep -c '^def ' hop_factory.py; grep -c 'Forest / Grasslands' hop_factory.py; grep -c 'Do not Hangar' docs/crew/log/lars.md.\n"
        + "Read hop_factory.py header + _pad_light _pad_hold _apply_pad_throttle _lid_burn_sit _inland_high_sit and the compose around _pad_light / _hold_or_cut.\n"
        + "Read .grok/agents/lars.md (one helper, sit not stamp, packet third path).\n"
        + "Focus: is the file a ticket log? Does each T-id add a sit helper + docstring novel? Does compose still call hop.py _hold_or_cut (suicide)?\n"
        + "Headings: ## File ## Helper count ## Ticket-shaped docstrings ## Compose still calls ## Pain ## Files read\n",
});
cjobs.push(#{
    label: "compile-lars-hires",
    capability_mode: "read-only",
    prompt: walls() + "Historian. Lars hires 2026-08-25 rf-ignition-ullage + hold-ground-card.\n"
        + "Read docs/crew/log/lars.md last 40. BOARD.md / head.json T-436 T-438 T-440 T-446 T-457 T-459 T-462 T-464 T-465.\n"
        + "Focus: same fingerprint rf-ignition-ullage four times (T-457 lid, T-459 throttle-then-stage, T-462 hold, T-464 engine throttle). Each hire 8–15 min. T-465 flameout cancelled. Tonight 20-36-06Z: RF DID light then fuel stuck 1396 throttle 1 apo 1.2 km — last-flight said shear 27→11, jsonl parts_n=27.\n"
        + "Headings: ## Hires ## Same stem reused? ## What each helper added ## Tonight tape vs last hire ## Files read\n",
});
cjobs.push(#{
    label: "compile-ids",
    capability_mode: "read-only",
    prompt: walls() + "Historian. Ticket ids are all T-NNN.\n"
        + "Read tickets.py TYPES TYPE_CATEGORY _next_id. BRIEF.md. BOARD.md sample fly/science/vehicle vs control/systems.\n"
        + "COUNT open science vs vehicle vs fly vs control. Os wants S-xxx science, M-xxx mission/fly, C-xxx craft. T-xxx not for those.\n"
        + "Headings: ## TYPES ## _next_id ## What is a T- today that should not be ## Prefix map ## Files read\n",
});
cjobs.push(#{
    label: "compile-xor",
    capability_mode: "read-only",
    prompt: walls() + "Historian. Lars vs Wernher named files.\n"
        + "Read .grok/agents/lars.md .grok/agents/wernher.md AGENTS.md XOR table. hop_factory.py imports physics_warp. T-450 Wernher thick_air vs T-438 Lars high_dwell as burn.\n"
        + "Focus: packet third path hop_factory not hop.py. Does Lars still patch hop.py? Does he call suicide via H._hold_or_cut?\n"
        + "Headings: ## XOR law ## Named files ## Leak into hop.py ## Files read\n",
});
cjobs.push(#{
    label: "compile-hank",
    capability_mode: "read-only",
    prompt: walls() + "Historian. Hank bus after Lars miss.\n"
        + "Read .grok/agents/hank.md docs/crew/log/hank.md last 40 ops.py leftover_sit PROTOCOL fly waste_blocks_refly.\n"
        + "Focus: pad abort sci_run=0 → protocol wait chicken-egg vs RF test hop. Hire Lars 4× same stem same day. Packet skim vs 200-line hop_factory.\n"
        + "Headings: ## Bus ## Why four rf-ignition hires ## Packet vs file size ## Files read\n",
});
cjobs.push(#{
    label: "compile-shelf",
    capability_mode: "read-only",
    prompt: walls() + "Historian. Science + craft tickets as T-xxx.\n"
        + "Read docs/program/science.md first 40 docs/program/vab.md first 40 BOARD science/vehicle ids T-404 T-406 T-081.\n"
        + "Focus: binds and hangs live as T-ids mixed with control bugs. Os: S/M/C prefixes if reasonable.\n"
        + "Headings: ## Science tickets ## Vehicle tickets ## Fly ticket ## Prefix fit ## Files read\n",
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
let compile_digest = clip(compile_blob, 7000);
let _cscratch = write_scratch_file("compile.md", compile_blob);

phase("Friction");
let fjobs = [];
fjobs.push(#{
    label: "friction-helpers",
    capability_mode: "read-only",
    prompt: walls() + "Analyst. Why hop_factory is unmaintainable.\n"
        + "Re-read hop_factory.py defs. Hypothesis: one miss → one _foo_sit + docstring that restates the ticket + Forest/Grasslands same. Compose still calls hop.py _hold_or_cut. Pad RF is four stacked functions for one light. Verify path:line. What the NEXT Lars hire would add if we do nothing.\n"
        + "COMPILE (untrusted):\n" + compile_digest + "\n"
        + "Headings: ## Topic ## Evidence ## Why ## Next-hire damage ## Files read\n",
});
fjobs.push(#{
    label: "friction-time",
    capability_mode: "read-only",
    prompt: walls() + "Analyst. Why Lars hires take 8–15 min.\n"
        + "Job card: forensic novelist, packet skim, pytest, git commit, lessons.md, feedback --claim. He re-reads hop_factory (~800 lines) every hire. Packet third path is the whole file. Four rf-ignition hires same day each re-deriving throttle vs stage.\n"
        + "COMPILE (untrusted):\n" + compile_digest + "\n"
        + "Headings: ## Topic ## Evidence ## Why ## Cheap cut ## Files read\n",
});
fjobs.push(#{
    label: "friction-ids",
    capability_mode: "read-only",
    prompt: walls() + "Analyst. T-xxx for science/craft/fly vs bugs.\n"
        + "tickets.py _next_id only T-. Os: S/M/C. Reasonable if packet/ops next/desk can key by prefix without a TYPE zoo. Do not add TYPES. Prefix is the id, type stays science/vehicle/fly.\n"
        + "COMPILE (untrusted):\n" + compile_digest + "\n"
        + "Headings: ## Topic ## Evidence ## Why ## Prefix map ## Files read\n",
});
fjobs.push(#{
    label: "friction-pad",
    capability_mode: "read-only",
    prompt: walls() + "Analyst. RSI vs pad occupancy vs Lars novels.\n"
        + "CHARTER sharper sit vs 15 min helper novel. Four closed rf-ignition tickets then T-465 flameout with fuel left — the pad-light stack was not the burn miss. Protocol wait sci-unchanged after pad abort chicken-eggs the next light.\n"
        + "COMPILE (untrusted):\n" + compile_digest + "\n"
        + "Headings: ## Topic ## Evidence ## Why ## Files read\n",
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
sim += "2026-08-25 rf-ignition-ullage: T-457 T-459 T-462 T-464 closed. Live 20-36-06Z lit then flameout MET10 fuel 1396 throttle 1 apo 1.2 km. ";
sim += "hop_factory ~800 lines, helper per T-id. T-465 cancelled. Os: Lars too long, file unmaintainable. S/M/C prefixes. ";
sim += "Bank 2.29. KSP was down then up. Pad occupancy. Do not raise ignitions.";

let ijobs = [];
ijobs.push(#{
    label: "talk-lars",
    agent_type: "lars",
    capability_mode: "read-only",
    prompt: walls() + "INTERVIEW only. You are Lars Grokman, VSE. Do not edit. Do not fly.\n"
        + "Sim: " + sim + "\n"
        + "Read .grok/agents/lars.md hop_factory.py header your log last 20. Answer:\n"
        + "## First command if this were T-465\n## Why each rf-ignition hire re-read the whole factory\n"
        + "## Why I add a helper instead of editing one pad block\n## Token waste I know\n"
        + "## One cheap cut so the next hire is 3 min not 15\n## Prefix I would put a science bind under (S vs T)\n",
});
ijobs.push(#{
    label: "talk-hank",
    agent_type: "hank",
    capability_mode: "read-only",
    prompt: walls() + "INTERVIEW only. You are Hank Grokman, COO. Do not edit.\n"
        + "Sim: " + sim + "\n"
        + "Read .grok/agents/hank.md. Answer:\n"
        + "## Why I hired Lars four times the same stem in one afternoon\n"
        + "## Packet third path is the whole hop_factory — should it be hop_factory_pad.py?\n"
        + "## protocol fly wait after pad abort — chicken-egg?\n## S/M/C on ops next\n",
});
ijobs.push(#{
    label: "talk-wernher",
    agent_type: "wernher",
    capability_mode: "read-only",
    prompt: walls() + "INTERVIEW only. You are Wernher Grokman, CSE. Do not edit hop_factory pulse law.\n"
        + "Sim: " + sim + "\n"
        + "Read tickets.py _next_id TYPES. Answer:\n"
        + "## Prefix S/M/C without a TYPE zoo — kernel change\n## hop_factory_pad extract vs leave Lars the compose\n## Files you would own\n",
});
ijobs.push(#{
    label: "talk-mortimer",
    agent_type: "mortimer",
    capability_mode: "read-only",
    prompt: walls() + "INTERVIEW only. You are Mortimer Grokman, CEO. Do not edit.\n"
        + "Sim: " + sim + "\n"
        + "Read Practice. Answer:\n"
        + "## Is one-helper-per-miss the RSI pitfall?\n## Prefix law\n## What must stay T-\n",
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
design_p += "You are Mortimer Grokman, CEO. BOUNDED RSI. Do not edit. Do not fly.\n";
design_p += "Read tickets.py _next_id TYPES, .grok/agents/lars.md, hop_factory.py first 350 lines, BRIEF.md, OPS.md.\n";
design_p += "Os: Lars too long; factory unmaintainable; S-xxx science, M-xxx mission/fly, C-xxx craft; T-xxx not for those; full apply.\n";
design_p += "Hard caps: no TYPE zoo (type stays science/vehicle/fly). Prefix is the id. ";
design_p += "Do not retune sit/warp/suicide LAW. You MAY extract pad-RF helpers to hop_factory_pad.py if compile proved the file is a ticket log. ";
design_p += "Do not raise ignitions. Do not Hangar. Pad occupancy. Depth 1.\n";
design_p += "Pick: (1) id prefixes S/M/C + T leftover for control/systems/ops/rsi/org (2) Lars card: one pad-RF block, no new helper per stamp, packet third path the NAMED helper file (3) optional hop_factory_pad.py extract.\n";
design_p += "COMPILE:\n" + compile_digest + "\nFRICTION:\n" + friction_digest + "\nTALKS:\n" + talk_digest + "\n";
design_p += "Write: ## Summary ## Why Lars is slow ## Why the file rots ## Prefix map ## Patches (max 8 rows file|change|owner|why) ## Tickets now (max 4) ## Do not touch\n";

let design_r = agent(design_p, #{
    label: "design-lars",
    agent_type: "mortimer",
    capability_mode: "read-only",
});
let design_text = text_of(design_r);
if design_text == "" {
    design_text = "DESIGN EMPTY";
}
log("design done");
let _dscratch = write_scratch_file("lars-rsi-design.md", design_text);
let design_json = json_encode(clip(design_text, 7000));
let design_ok = false;
if design_r != () {
    if design_r.success == true {
        if design_text != "" {
            if design_text != "DESIGN EMPTY" {
                design_ok = true;
            }
        }
    }
}
if apply_edits == true {
    if design_ok != true {
        apply_edits = false;
        log("design empty — report only");
    }
}

if apply_edits != true {
    phase("Report");
    let rep = walls();
    rep += "Do not write live docs/program/lars-rsi.md. Report via write_scratch_file only. Title: Lars RSI (compile, no apply).\n";
    rep += "DESIGN:\n" + design_json + "\nCOMPILE:\n" + compile_digest + "\nFRICTION:\n" + friction_digest + "\nTALKS:\n" + talk_digest;
    let report_r = agent(rep, #{
        label: "report-audit",
        agent_type: "mortimer",
        capability_mode: "read-write",
    });
    let report = text_of(report_r);
    if report == "" { report = design_text; }
    let scratch = write_scratch_file("lars-rsi.md", report);
    complete(#{
        path: scratch,
        apply: false,
        compile_slots: ci,
        friction_slots: fi,
        interview_slots: ti,
        design_ok: design_ok,
    });
}

phase("Apply");
let k_p = walls();
k_p += "KERNEL. Isolation none. Allowlist: tickets.py ops.py protocol.py desk.py tests/test_tickets.py tests/test_protocol.py tests/test_protocol_gate.py tests/test_desk.py.\n";
k_p += "If Design confirmed prefixes: _next_id by type — science→S-, fly→M-, vehicle→C-, else T-. Packet/ops next/BRIEF accept S- M- C- T-. Existing T- science/vehicle/fly KEEP their ids (no rewrite of history). New opens use the prefix. Tests.\n";
k_p += "Do not retune hop_factory pulse law here (that is impl-lars if Design extract). Do not TYPE zoo.\n";
k_p += "DESIGN:\n" + design_json + "\nReturn files and test result.\n";
let k_r = agent(k_p, #{
    label: "impl-kernel",
    capability_mode: "all",
    agent_type: "wernher",
});
log("kernel done");
let k_text = clip(text_of(k_r), 3500);

let lars_p = walls();
lars_p += "LARS CARD + optional pad extract. Isolation none.\n";
lars_p += "Allowlist: .grok/agents/lars.md docs/crew/lars.md hop_factory.py AND hop_factory_pad.py only if Design said extract. tests/test_hop_factory.py tests/test_hangar.py if they import pad helpers.\n";
lars_p += "DO: job card — do not add a new _sit helper per stamp; RF pad is one block; packet third path is the named file (hop_factory_pad.py if extracted else hop_factory.py); lessons heading names fingerprint not T-id; hire should pytest that file not the house.\n";
lars_p += "If extract: move _pad_light _pad_hold _apply_pad_throttle _pad_engines _engine_throttle _pad_engine_live _release_pad_throttle; hop_factory imports them. Do NOT change sit/warp/suicide law. Tests must pass.\n";
lars_p += "DESIGN:\n" + design_json + "\nKERNEL:\n" + k_text;
let lars_r = agent(lars_p, #{
    label: "impl-lars",
    agent_type: "lars",
    capability_mode: "all",
});
log("lars implementer done");

let cards_p = walls();
cards_p += "Job cards BRIEF hank gene linus gus wernher mortimer: S/M/C prefixes on new science/fly/vehicle opens; packet T-NNN also S- M- C-; control/systems/ops/rsi/org stay T-.\n";
cards_p += "DESIGN:\n" + design_json + "\nKERNEL:\n" + k_text + "\nDo not edit CHARTER creed. Do not edit hop.py pulse law.\n";
let docs_p = walls();
docs_p += "PROTOCOL OPS world-model Practice BRIEF AGENTS.md: prefix law; Lars one-block pad RF; last-flight still postcard. DESIGN:\n";
docs_p += design_json + "\nKERNEL:\n" + k_text + "\nDo not paste OPS into AGENTS. Do not Hangar.\n";

let apply_panel = parallel([
    #{ label: "impl-job-cards", capability_mode: "read-write", prompt: cards_p },
    #{ label: "impl-docs", agent_type: "mortimer", capability_mode: "read-write", prompt: docs_p },
]);
log("cards+docs done");

phase("Verify");
let test_p = "";
test_p += "source .venv/bin/activate && python -m unittest tests.test_tickets tests.test_protocol tests.test_protocol_gate tests.test_desk -q\n";
test_p += "If hop_factory_pad.py exists, also tests that import it. Fix breakage. Do not fly.\n";
let test_r = agent(test_p, #{
    label: "verify-unittests",
    capability_mode: "all",
});

let sk_over = walls();
sk_over += "Skeptic overscope. real=true only if TYPE zoo, pulse LAW retune, CHARTER creed, two writers, raise ignitions, or Gene merge. Else real=false with path. DESIGN:\n" + design_json + "\nKERNEL:\n" + k_text;
let sk_gap = walls();
sk_gap += "Skeptic gap. real=true if new science/vehicle/fly opens are still T- OR lars.md still says add a helper per miss with no pad-block rule OR hop_factory still the only packet path with no extract when Design required extract. Else real=false. Evidence path:line.\n" + design_json;

let skeptics = parallel([
    #{ label: "skeptic-overscope", capability_mode: "read-only", prompt: sk_over },
    #{ label: "skeptic-gap", capability_mode: "read-only", prompt: sk_gap },
]);

phase("Report");
let rep2 = walls();
rep2 += "Do not write live docs/program/lars-rsi.md. Report via write_scratch_file only. Title: Lars RSI (applied).\n";
rep2 += "Sections: 1 Sit 2 Why slow 3 Why unmaintainable 4 Prefix map 5 Files 6 Tests 7 Skeptics 8 Tickets 9 Open risks.\n";
rep2 += "Open leftover tickets if Design named them (systems/rsi). Log docs/crew/log/mortimer.md.\n";
rep2 += "DESIGN:\n" + design_json + "\nKERNEL:\n" + k_text;
rep2 += "\nLARS:\n" + json_encode(clip(text_of(lars_r), 2500));
rep2 += "\nCARDS:\n" + json_encode(clip(text_of(apply_panel[0]), 2000));
rep2 += "\nDOCS:\n" + json_encode(clip(text_of(apply_panel[1]), 2000));
rep2 += "\nTESTS:\n" + json_encode(clip(text_of(test_r), 1500));
rep2 += "\nSKEPTICS:\n" + json_encode(clip(text_of(skeptics[0]), 1200)) + "\n" + json_encode(clip(text_of(skeptics[1]), 1200));

let report2 = agent(rep2, #{
    label: "report-applied",
    agent_type: "mortimer",
    capability_mode: "read-write",
});
let report_t = text_of(report2);
if report_t == "" { report_t = design_text; }
let scratch2 = write_scratch_file("lars-rsi.md", report_t);
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
