# OPM Travel Policy Flight Booking

**Source of the handbook:** https://www.opml.co.uk/sites/default/files/2024-03/travel-policy-v4-0-march-2024.pdf. The agent reads it verbatim (bundled at `src/plugin/data/policy.txt`); flights, fares and trips are synthetic.

**No affiliation with Oxford Policy Management.** The handbook is the *OPM Travel Policy* (Oxford Policy
Management Limited, Project Management Office, March 2024, version 4.0), a published company policy bundled
verbatim for research. Its public source URL was not recorded (`pilot_work/originals/MANIFEST.md`: UNVERIFIED; the
raw PDF is the pinned copy). It is a corporate handbook: do not publish this plugin before the course staff confirm
that a verbatim corporate handbook may be redistributed (MASTER_PLAN section 4).

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the organisation's real
travel policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and policy section. A deterministic Python verifier,
with no LLM, rebuilds the offers and the policy's answer itself and checks every field. Built from the
original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario files
(the JSON files are the truth). Fares are in pence (`currency: GBP`).

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 3,403 words, 413 lines, 23,601 characters, sha256
`923ed410...a9d9414f`, equal to `pilot_work/originals/opml/frozen/SHA256SUMS`) is never paraphrased, and the task
text restates no rule. It keeps the converter's stray mid-word spaces ("bus iness") and private-use bullet glyphs.
Under stock NanoAgent the agent does not see it: the plugin then runs as the `off` baseline. The `harness.policy`
switch of the NanoAgent fork (github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system
prompt: `harness.policy: full` adds all of it, and the selection methods add parts of it. These plugins are meant to
run with `query: instructions+input`, so a selector sees the traveller's request.

**Size.** On the calibration of the paid Thornton and NJC runs (about 0.2 tokens a character of handbook plus
1,800) the first call under `full` is about 6,500 input tokens, the second about 7,100 and the third 7,600 to 8,600.
A 3-call run (`get_trip`, `search_flights`, `submit`) is about 22,000 input tokens, far under the 65,536 hosted cap.

## Task

- **Input:** `TaskInput`: `scenario` (one of 24 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on the trip's route and date, then `submit` (3 of the 6 hosted steps).
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing),
  `reason_code`, `approver` and `clause`, each from a closed list. The reason list is shared by every handbook
  plugin, plus this policy's codes and decoy codes from other handbooks' rules. Approvers follow SYNC_NOTES 4': a
  booking or refusal with a sign-off on file accepts that role and `NONE`; a hold accepts only the role(s) it waits
  for (`NOT_NAMED` where the policy names nobody).
- **Success:** every field is one the answer key accepts. Score = fields right / 6.

What the policy decides here: flexible (refundable) economy is the default fare (line 253); a nonstop within the
fare budget may beat a cheaper connection (lines 248-250); premium cabins come from the client contract or the
client/donor's written approval on project travel, and from the CFO and Board/SMT rules on corporate travel (lines
253-262); USAID projects fly US carriers (line 272) and need the client's written approval (lines 128-131); requests
go in at least five days ahead, urgent ones through the TSSM (lines 117-123); a subcontractor's contract must cover
the trip (line 127); personal trips and commutes are never booked (lines 65-67, 114-115); Eurostar is used where
cheaper (lines 297-299).

| Scenario | Category | Expected decision (offer) | Reason (one of) | Approver (one of) | Clause cited (frozen lines) |
|---|---|---|---|---|---|
| `copper-lagoon` | easy | BOOK (kenya-flex) | LOWEST_FARE, FLEXIBLE_ECONOMY_POLICY | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (253-255, 248-250) |
| `mistral-quay` | easy | BOOK (emirates-flex) | LOWEST_FARE, FLEXIBLE_ECONOMY_POLICY | NONE, LINE_MANAGER | AIR_CLASS_AND_RATES (253-255) |
| `orchard-tide` | easy | BOOK (india-flex) | LOWEST_FARE, FLEXIBLE_ECONOMY_POLICY | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (253-255) |
| `fennel-cairn` | easy | BOOK (amsterdam-flex) | LOWEST_FARE, FLEXIBLE_ECONOMY_POLICY | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (127, 253-255) |
| `saltmarsh-vigil` | easy | BOOK (american-flex) | LOWEST_FARE, FLEXIBLE_ECONOMY_POLICY | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (253-255) |
| `heron-quill` | boundary_twin | BOOK (british-flex nonstop, or dubai-flex) | DIRECT_OPTION_WITHIN_BUDGET, LOWEST_FARE | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (248-250) |
| `pewter-rill` | boundary_twin | BOOK (dubai-flex) | DIRECT_OPTION_OVER_BUDGET, LOWEST_FARE, FLEXIBLE_ECONOMY_POLICY | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (248-250) |
| `lumen-thicket` | boundary_twin | BOOK (singapore-premium) | CLIENT_PERMITS_PREMIUM_CABIN | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (253-255) |
| `garnet-thistle` | boundary_twin | BOOK (singapore-flex) | PREMIUM_CABIN_NOT_PERMITTED, FLEXIBLE_ECONOMY_POLICY | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (253-255) |
| `basalt-orrery` | boundary_twin | BOOK (newark-flex, United) | FLY_AMERICA_US_CARRIER_REQUIRED | NONE, PROJECT_MANAGER, CLIENT_OR_DONOR | FLIGHT_CARRIERS (272-274) |
| `quartz-heddle` | boundary_twin | BOOK (dubai-flex) | LOWEST_FARE, FLEXIBLE_ECONOMY_POLICY | NONE, PROJECT_MANAGER, CLIENT_OR_DONOR | AIR_CLASS_AND_RATES (253-255) |
| `sorrel-beacon` | multi_rule | BOOK (african-business) | PREMIUM_CABIN_APPROVED | NONE, LINE_MANAGER, CHIEF_FINANCIAL_OFFICER | AIR_CLASS_AND_RATES (255-262) |
| `tansy-ledger` | multi_rule | BOOK (british-flex) | PREMIUM_CABIN_NOT_PERMITTED, FLEXIBLE_ECONOMY_POLICY | NONE, LINE_MANAGER | AIR_CLASS_AND_RATES (255-262) |
| `wicket-moraine` | multi_rule | BOOK (turkish-flex) | URGENT_TRAVEL_APPROVED | NONE, PROJECT_MANAGER, TSSM | BOOKING_TRAVEL (117, 123) |
| `ember-cistern` | multi_rule | BOOK (avianca-business) | CLIENT_PERMITS_PREMIUM_CABIN | NONE, PROJECT_MANAGER | AIR_CLASS_AND_RATES (253-255) |
| `drover-paddock` | hidden_clause | REFUSE | COMMUTE_NOT_TRAVEL | NONE | DEFINITIONS (65-67, 89-92) |
| `linnet-gable` | hidden_clause | BOOK (india-premium) | CLIENT_PERMITS_PREMIUM_CABIN, PREMIUM_CABIN_APPROVED | NONE, PROJECT_MANAGER, CLIENT_OR_DONOR | AIR_CLASS_AND_RATES (253-255) |
| `cobble-larch` | distractor | BOOK (egypt-flex) | LOWEST_FARE, FLEXIBLE_ECONOMY_POLICY | NONE, PROJECT_MANAGER | BOOKING_TRAVEL (117) |
| `pallas-weir` | distractor | BOOK (france-flex) | RAIL_NOT_CHEAPER, LOWEST_FARE | NONE, LINE_MANAGER | TRAINS (297-299), AIR_CLASS_AND_RATES |
| `marram-kite` | refusal | REFUSE | PERSONAL_TRAVEL_NOT_COVERED | NONE | PERSONAL_TRAVEL (114-115, 142-144) |
| `bracken-tarn` | refusal | REFUSE | SUBCONTRACT_NOT_COVERING_TRIP | NONE, PROJECT_MANAGER | PROJECT_TRAVEL (127) |
| `gossamer-hatch` | flag | FLAG (egypt-flex) | APPROVAL_REQUIRED | TSSM | BOOKING_TRAVEL (117, 123) |
| `umber-spindle` | flag | FLAG (newark-flex) | APPROVAL_REQUIRED | CLIENT_OR_DONOR | PROJECT_TRAVEL (128-131) |
| `vesper-lattice` | flag | FLAG (african-business or british-flex) | UNCLEAR_POLICY_TEXT | NOT_NAMED, CHIEF_OPERATING_OFFICER, CHIEF_FINANCIAL_OFFICER | AIR_CLASS_AND_RATES (255-262) |

Decisions: 18 BOOK, 3 REFUSE, 3 FLAG_FOR_APPROVAL. The full accept sets are in each scenario's `expected`. An agent
that always books the cheapest seat with `LOWEST_FARE` and `NONE` passes none of the 24; one that always holds the
right offer as unclear with `NOT_NAMED` passes one (`vesper-lattice`).

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, seniority, home and usual office, route, dates (travel, end of trip, request submitted, today), project or corporate, funder, the client contract's cabin, a subcontractor's contract end, requested cabin and routing, fare budget, a train quote, sign-offs, notes | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date: the pinned scenario offers plus seeded background offers on those searches only; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-opml-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this policy's scenario ids, approvers, sections, reason codes,
  decoys and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  policy's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this policy's settings.
- `tests/build_scenarios.py`: writes the scenario files (an authoring aid, not a test).
- `tests/BUILD_NOTES.md`: design decisions, the blind read and the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/opml-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
