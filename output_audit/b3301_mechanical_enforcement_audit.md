# B3301 - mechanical-enforcement audit of the 2026-10-20..23 lessons (owner question 2026-10-24)

# Source: scratchpad mech_audit.py (B3139q-r109) over LEARNINGS.md L940-L959, backtest/tests/test_*.py, scripts/verify_turn_compliance.py, scripts/preflight.py and scripts/*.py at HEAD 344cffdae; per CHECKLIST #77

**Question (owner, verbatim):** "have all the new updates been mechanically enforced so that opus does not go astray. no silent misses."

**Scope:** L940-L959, the twenty lessons written between 2026-10-20 and 2026-10-23, plus the pins named by this session's tool tickets. Method: scratchpad mech_audit.py (B3139q-r109) parses each entry's **Mechanism** paragraph, extracts every test_ / scan_ / check_ / preflight C-name / script it cites, and resolves each against the tree (a `def test_` in backtest/tests, a `def scan_` or `def check_` in scripts/verify_turn_compliance.py or scripts/preflight.py, or a script file). Classification: MECHANISED when at least one named detector or refusal resolves; JUDGMENT-ONLY when the entry says so, with "+ durability pin" when a named test pins the rule's text or its fix; NO MECHANISM NAMED when the paragraph names nothing. Run 2026-10-24 (B3139q-r109), 20 of 20 entries parsed.

## Result

| Lesson | Class | Named mechanisms that resolve |
|---|---|---|
| L940 | JUDGMENT-ONLY + durability pin | test_b3196_band_levels_follow_each_knobs_gate_direction, test_b3196_selector_rule_is_in_the_durable_docs, test_b2123 |
| L941 | MECHANISED | test_b3224_every_offline_cell_leads_with_its_counted_class, test_b3224b_table_generators_type_no_code_population_claim |
| L942 | MECHANISED | pyramid_gate start refusal, preflight C15, preflight C17, test_b3230_gate_records_are_write_once |
| L943 | MECHANISED | moved_line_citations.py, test_b3231_screener_is_cited_by_symbol_not_line, test_b3245_the_gate_discloses_code_line_citations_an_edit_moved, test_b3139ai |
| L944 | MECHANISED | scan_decision_without_ticket, test_b3233_decision_list_items_name_a_live_ticket |
| L945 | JUDGMENT-ONLY + durability pin | test_b1248_withdrawn_short_default_is_never_stated_as_current, test_b3222 |
| L946 | MECHANISED | test_b3232 (per-side survival formula on every two-sided row) |
| L947 | MECHANISED | test_b3243_a_writing_script_parses_its_arguments (shrink-only, 120 legacy writers) |
| L948 | MECHANISED | scan_help_on_parserless_script (wired in main), test_b3259 |
| L949 | MECHANISED | scan_obligation_in_closing_row (wired in main), test_b3250, test_b3260 |
| L950 | MECHANISED | pregate_select.py (S6-B3269), test_b3269; its first live catch is B3139q-r109c (test_b3139, below) |
| L951 | JUDGMENT-ONLY + durability pin | test_b3262 |
| L952 | MECHANISED | exit_cube_coverage.py, test_b3263 |
| L953 | JUDGMENT-ONLY + durability pin | test_b2123 (fix S6-B3270 pending) |
| L954 | MECHANISED | test_b3282 (COMPACTION_TIMELINE_CLAIM admits qualifier words) |
| L955 | JUDGMENT-ONLY + durability pin | moved_line_citations.py enclosing-function names, test_b3285 |
| L956 | MECHANISED | test_b3286 (data_env_parity normalises text endings in every root) |
| L957 | MECHANISED | preflight C19 check_tracked_set_readers_on_add, test_b3287 |
| L958 | JUDGMENT-ONLY | relies on existing mechanisms it names: the S6-B3139bb per-file citation ratchet and S6-B3269 pre-gate selection |
| L959 | JUDGMENT-ONLY at the time of the audit | mechanism lands at B3139q-r110: scripts/mutation_probe.py (S6-B3296, test_b3296) |

**Totals:** 20 entries; 13 MECHANISED; 7 judgment-only, of which 5 carry a durability pin; 0 with no mechanism named. After B3139q-r110 lands scripts/mutation_probe.py, L959 moves to MECHANISED: 14 of 20.

**Resolver notes (hand-read, not counted as gaps):** the resolver reported MISSING names on 2 entries. L943's three - screener.py, smc_ict.py, technical.py - are the subject files of its citation ratchets and exist at backtest/signals/ (the resolver looked for scripts/ files only). L955's two - test_unit / test_unit.py - are the test module named as a location, not a mechanism. Neither is an unenforced rule.

**Live evidence this turn that the mechanisms fire:** pregate_select (L950's mechanism) selected 188 tests for batch E and refused 1 before the gate (test_b3139, a text pin on a call site, L748 class) - recorded as CHECKLIST #315 INSTANCE 5 and an L950 INSTANCE; the turn gate blocked two closes on the mandated blocks (ticket table form, owner-decision acknowledgement), both rewritten from the accepted form.

**Judgment-only remainder, with what holds each:** L940 (classing a band level by each consumer's construct) - test_b3196 pins every vix_band_low read as an if-test; L945 (an approved change reaching past its packet) - durability pins only; L951 (a copied false premise) - test_b3262 pins the corrected premise; L953 (per-side quantiles from a mixed population) - fix S6-B3270 open, pin by test_b2123; L955 (a citing test named from recall) - moved_line_citations.py prints the enclosing function so the next citation is copied, not recalled; L958 (citations copied from renders; a pin written for a pre-flip state) - held by the existing ratchet and the pre-gate selection, both of which caught the instance.

Ticket: S6-B3301 (B3139q-r110).
