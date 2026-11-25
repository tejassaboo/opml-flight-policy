# Validation notes: opml-flight-policy (paid wave 3 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w3_2026-11-25/opml-flight-policy@w3/`, arm
`full`, DeepSeek V4 Flash (Nebius fp8), temperature 0, max_steps 6, max_tokens 8192, one run per scenario, at plugin
head 73a926f. Line numbers are lines of `src/plugin/data/policy.txt`.

## Results

20/24 valid (83.3%), mean field score 0.924, **easy 5/5**. By category: boundary 5/6, distractor 2/2, easy 5/5,
flag 0/3, hidden 2/2, multi 4/4, refusal 2/2. $0.00159 billed per run, 4.4 calls per run, 9,270 prompt tokens per
call, no run over the hosted 65,536 cap. Every run submitted.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| gossamer-hatch | flag | BOOK EgyptAir flexible KNDK-XJZN (the held offer), FLEXIBLE_ECONOMY_POLICY, NONE, AIR_CLASS_AND_RATES; key FLAG for TSSM, ADVANCE_PURCHASE_TOO_LATE or APPROVAL_REQUIRED, BOOKING_TRAVEL | model slip | The request opens "Short notice, I know", and the record has `request_submitted` 2026-11-28 for travel on 2026-12-02 (four days). The reasoning never looks at either date: it goes straight to line 253's flexible economy ("OPM's policy is to book flexible economy class flights ... Book it") and treats the Project Manager's sign-off as the end of approvals. Line 117 requires requests "at least five days prior to Travel", and line 123 sends urgent travel to the TSSM. The twins cobble-larch (five days: BOOK) and wicket-moraine (three days, TSSM signed: BOOK) passed. |
| umber-spindle | flag | BOOK United flexible 9C4Q-TZAY (the held offer), FLEXIBLE_ECONOMY_POLICY, NONE; key FLAG for CLIENT_OR_DONOR, APPROVAL_REQUIRED, PROJECT_TRAVEL | model slip | It saw the funder and applied the USAID carrier rule ("US Flag Carrier Rules apply (Section 3.2), which excludes the Emirates and Qatar Airways offers"), then "The trip already has the required Project Manager sign-off on file, so no further approval is needed." It never read lines 128-131: "all travel undertaken on USAID projects must be approved in writing in advance by the client". The record's only sign-off is the Project Manager's. The twins basalt-orrery (client approval on file: BOOK) and quartz-heddle (FCDO: BOOK) passed. |
| vesper-lattice | flag | BOOK SAA business 8YEK-6XX5 (a held offer), PREMIUM_CABIN_APPROVED, CHIEF_FINANCIAL_OFFICER; key FLAG, UNCLEAR_POLICY_TEXT or APPROVAL_REQUIRED | model slip (borderline) | "per section 3.1, CFO approval is required for business class bookings — which is on file." It read lines 255-257 as sufficient and never weighed lines 258-262 in the same paragraph: only "the OPM Board and members of the Senior Management Team may be permitted to Travel in a class other than economy", and "other Staff" who upgrade reimburse OPM. The traveller is a Principal Consultant (`seniority` STAFF). Both readings are live, and the hold accepts the held offer of each. The twins sorrel-beacon (SMT + CFO: BOOK business) and tansy-ledger (staff, no CFO: BOOK economy) passed. |
| pewter-rill | boundary_twin | BA flexible nonstop Y98C-GZ39 (£915), FLEXIBLE_ECONOMY_POLICY; key Emirates flexible via Dubai QLGG-7JPB (£720) | model slip (limit rationalised away) | It found the boundary itself: "The flexible economy direct BA is 91500, which is 1.7% over ... the budget is £900", then booked it anyway because it is "the direct overnight flight the traveller requested". Lines 248-250 allow the direct option over a cheaper indirect route only "where the most direct option available is within budget parameters"; both flexible nonstops (£915, £930) are over £900. The Emirates flexible fare lands 09:30 on the 27th, before the workshop on the 28th. The twin heron-quill (flexible nonstop within budget) passed. |

All three flags were read against the record and the handbook to check for weak or defective holds. None is: each
turns on a sentence the model did not read (lines 117 and 123, lines 128-131, lines 258-262), and every twin passed.
`FLEXIBLE_ECONOMY_POLICY` on three of the four failures is the model's default label for line 253, not a sign of a
defective key; the plain flexible-economy BOOK keys accept it, and the keys decided on a more specific ground (budget,
Fly America, approvals, client cabin) rightly do not.

## Fixes

None. All four failures are slips, so no accept set was widened and no record changed.

## Q2

The always-cheapest agent passes **0/24 (0%)** before and after (`MAX_PASS_ALWAYS_LOWEST = 0`), because every
booking is a flexible fare and the cheapest open seat is always a restricted saver.

## Re-score

Stored answers re-scored at this head: 20/24, easy 5/5 (unchanged).

## Re-run

None required. Optional (variance only): vesper-lattice (the borderline flag).

## Checks

`uv run pytest -q` (196 passed, 3 skipped), `uv run ruff check .`, `uv lock --check`, `check_shared.py`, `tools/stock_verify.py`
(24 scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).
