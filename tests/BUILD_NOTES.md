# Build notes: opml-flight-policy (wave 3)

Built 2026-11-24 from `pilot_work/tier_plan/build/WAVE3_BUILD_BRIEF.md`, unattended: every open choice below took
the recommended option and is recorded here.

## Handbook

`pilot_work/originals/opml/frozen/opml_policy.txt`: OPM Travel Policy (Oxford Policy Management, March 2024,
version 4.0), 3,403 words, 413 lines, 23,601 characters, sha256 `923ed410...a9d9414f`. Under 10,000 words, so 24
scenarios (EDGE_CASES 5.1). Instantiated with `--slug opml --task-id book-opml-flight --currency GBP --background 0
--scenarios 24`; `handbook.json` holds the raw PDF's sha256 and `frozen_on`. Every fare is in pence. Source URL:
not recorded (MANIFEST: UNVERIFIED).

## Checkable flight rules found (frozen lines)

| Rule | Lines | Operator | Used by |
|---|---|---|---|
| Travel = outside the normal place of work; not a commute between home and the normal place of work | 65-67, 89-92 | definition | `drover-paddock` |
| No personal travel on the business account or project funds; no personal cost reimbursed | 114-115, 142-144 | | `marram-kite` |
| Requests at least five days before travel | 117 | "at least", inclusive, calendar days from `request_submitted` | `cobble-larch` (5), `gossamer-hatch` (4), `wicket-moraine` (3) |
| Manager approval before booking; urgent travel: contact the TSSM | 122-123 | | every booking; `gossamer-hatch`, `wicket-moraine` |
| Subcontractor's contract must cover the trip | 127 | contract end on or after the trip's last day | `fennel-cairn`, `bracken-tarn` |
| USAID travel approved in writing in advance by the client | 128-131 | | `basalt-orrery`, `umber-spindle` |
| Most cost-effective direct route; a direct option within budget may be selected over a cheaper connection | 248-250 (and 107-108) | fare <= budget | `heron-quill`, `pewter-rill` |
| Flexible economy; better only if the client contract expressly permits or the client/donor approves in writing | 253-255 | | every economy booking; `lumen-thicket`, `garnet-thistle`, `ember-cistern`, `linnet-gable`, `orchard-tide`, `saltmarsh-vigil` |
| Corporate business/premium economy needs the CFO's approval | 255-257 | | `sorrel-beacon`, `tansy-ledger`, `vesper-lattice` |
| Board/SMT may travel above economy with COO/CFO/CEO approval; other staff upgrade at own cost | 258-262 | | `sorrel-beacon`, `tansy-ledger`, `vesper-lattice` |
| USAID projects: US Flag Carrier Rules (Fly America) | 272-274 | | `basalt-orrery`, `quartz-heddle`, `umber-spindle` |
| UK-EU: examine Eurostar; use it where cheaper unless timings are prohibitive | 250-252, 297-299 | | `pallas-weir` |

Rules present but not tested, and why:

- **High/Critical-risk countries** (117-119): "longer lead times will be required" gives no number, and a missing
  portal approval would be a fourth flag (the 15% cap allows 3). No trip record carries a risk rating.
- **FAA/EU-approved carriers, MAF, TSSM approval of non-FAA airlines** (264-271): testing it would mean stating that a
  real airline of the shared world lacks FAA/EU approval. Not done; see the template change requests.
- **No international travel on PIA** (275-276): the shared world has no Pakistan airport and no PIA. Template
  change request below.
- **Booking outside OPM's service providers needs TSSM approval** (157-159): every offer in the world comes from the
  booking tool, so no case can book elsewhere.
- **Visas** (378-381: a visa or the supplier's confirmation before flights are booked): a pending visa is neither a
  refusal nor a sign-off, so none of the three decisions fits it. Not used.
- **Insurance confirmation** (346-349), **Air Miles** (260-261, soft), **6-week insurance email** (339-340),
  **USAID doctor's statement** (364-366), **90-day expense claims** (391-392): used only as distractors or not at
  all; none decides a booking.
- **Portal for all travel** (374-375): the trip record's `request_submitted` says the request went in on the
  approval portal; never tested on its own.

No duration threshold exists, so `rules.DURATION_RULES` is empty, `rules.over` knows no rule, and
`DURATION_CASES` is empty (the three duration tests skip on empty parameter sets). No rule covers several travellers
on one flight or overnight stops, so `OVERLAY_MINIMUMS` asks for neither.

## Decisions taken without asking

1. **"Flexible economy" is the refundable fare.** Line 253 says the policy is to book flexible economy class flights;
   the shared offer field `refundable` is "Whether the fare can be refunded or changed without a fee". Every economy
   answer is the cheapest refundable economy seat that can be bought, and every pinned world lists cheaper
   non-refundable fares beside it. This is the plugin's main handbook signal: the always-cheapest agent passes none.
   Premium-cabin answers are the cheapest seat of that cabin, and that seat is always refundable, so no answer
   depends on whether "flexible" reaches beyond economy (`rules.premium_offer` raises otherwise).
2. **Manager approval in every business trip** (lines 122-123): the Project Manager for project travel, the line
   manager for corporate travel, always on file. Approvers follow SYNC_NOTES 4': BOOKs accept `NONE`, that manager and
   every other sign-off on file; refusals accept `NONE` plus any sign-off on file (4(b)); holds accept only the awaited
   role (`TSSM` in `gossamer-hatch`, `CLIENT_OR_DONOR` in `umber-spindle`), and the unclear hold accepts `NOT_NAMED`,
   `CHIEF_OPERATING_OFFICER` (line 161, overall accountability; policy owner) and `CHIEF_FINANCIAL_OFFICER`.
3. **The five-day rule counts from the request, not the booking** ("Travel requests must be submitted"): the record
   has `request_submitted` beside `booking_date`. `cobble-larch` books two days before travel on a request made five
   days before; "booked as far in advance as possible" (120-121) is a soft wish.
4. **A late request is a hold for the TSSM**, not a refusal: line 123 "In cases of urgent travel, please contact the
   TSSM". Accepts `APPROVAL_REQUIRED` and `ADVANCE_PURCHASE_TOO_LATE` (the reason that calls for the sign-off).
5. **A subcontract that ends before the trip does is a refusal** (line 127, "must have a valid contract covering the
   duration of their trip"): no one can sign off a missing contract, so this is not a hold.
6. **Budget test.** "within budget parameters" is read as the fare at or under `fare_budget_cents`; the twins sit at
   885 and 915 pounds against 900, never on the line. The budget test applies only when the traveller asks for a
   nonstop; a case with a cheaper connection beside a flexible nonstop and no stated wish raises (none exists:
   `quartz-heddle`, `fennel-cairn`, `pewter-rill` have no flexible nonstop within budget or no nonstop at all).
   `pewter-rill` declines the nonstop on the policy's own cost-effective/budget test, so it accepts
   `DIRECT_OPTION_OVER_BUDGET`, `ALTERNATE_ROUTE_TOO_EXPENSIVE` and `LOWEST_FARE` (lesson 12).
7. **Fly America** is applied as "US carriers only", by the airline name `search_flights` shows (United, Delta,
   ...). The non-US options in those cases are Emirates and Qatar, which no Open Skies exception covers, so outside
   knowledge of the Act gives the same answer. `OPEN_SKIES_AGREEMENT` is therefore not used as a decoy here.
8. **Project travel needs no CFO approval** for a premium cabin: line 255's CFO sentence opens "For corporate travel".
   `ember-cistern` and `lumen-thicket` carry that sentence as a distractor.
9. **Commute** is detected from the record: `home_airport` and `workplace_airport` differ and the flight joins them.
10. **Declined requests (lesson 12).** `garnet-thistle`, `tansy-ledger` (premium asked, not allowed) accept
    `PREMIUM_CABIN_NOT_PERMITTED`, `UPGRADE_NOT_ELIGIBLE`, not `LOWEST_FARE`. Every request that asks for a cabin the
    policy may refuse gives a fallback (lesson 3). Economy bookings where the traveller asked "economy" are not
    declines and accept `LOWEST_FARE` and `FLEXIBLE_ECONOMY_POLICY`; requests never say "cheapest".
11. **Arrival times (lesson 4).** Every request names when the business starts (a later day in every case where the
    keyed flight is not the earliest); no key depends on an arrival time.
12. **Decoys:** WEEKEND_TRAVEL_HOME, WEEKEND_TRIP_NOT_EARNED, NEXT_OF_KIN_TRAVEL, CREATIVE_TICKETING,
    EXTENDED_TRAVEL_SAVINGS, DENIED_BOARDING_NOT_ALLOWED, CHANCELLOR_WRITTEN_AUTHORIZATION, DOUBLE_BOOKING_PROHIBITED,
    PRIVATE_AIRCRAFT_NOT_APPROVED, CANDIDATE_TRIP_NOT_COVERED, SAME_CLASS_AS_CUSTOMER (each subject grepped: absent;
    "private" occurs only as "Private Security Company"). Approver decoys: DIRECTOR, VICE_PRESIDENT, DEPARTMENT_HEAD,
    TRAVEL_DEPARTMENT. Handbook codes for untested rules (`PIA_INTERNATIONAL_NOT_PERMITTED`, `CARRIER_NOT_APPROVED`)
    stay in the list; they are real rules of this policy.
13. **Background offers:** 2 per search on four easy cases, 0 elsewhere; background fares are never refundable and
    far dearer, so they never change an answer.
14. **One ticket per case:** every case is the one-way fare out; `trip_end` says the flight back is booked
    separately. No round-trip search is pinned.

## Mix and overlays

5 easy, 6 boundary twins (budget 885/915; contract PE/economy; funder USAID/FCDO), 4 multi-rule, 2 hidden clause,
2 distractor, 2 refusal, 3 flags (12.5%). Also non-mutual one-fact pairs: `cobble-larch`/`gossamer-hatch` (request on
27 or 28 November), `fennel-cairn`/`bracken-tarn` (contract to 31 January or 31 December), `basalt-orrery`/
`umber-spindle` (client approval on file or not). Decisions: 18 BOOK, 3 REFUSE, 3 FLAG. Overlays: multi_leg 6,
date_arithmetic 5, month_end 4, personal_travel 1, dearer_option 6, upgrade_not_taken 2, outside_air_section 8,
plus synonym 1, approval_required 2, unclear_phrase 1.

Degenerate agents: always-cheapest (cheapest seat, `LOWEST_FARE`, `NONE`) passes 0 of 24
(`MAX_PASS_ALWAYS_LOWEST = 0`); always-flag passes 1 (`vesper-lattice`; `MAX_PASS_ALWAYS_FLAG = 1`).

## Flags

| Scenario | Kind | What | Twins |
|---|---|---|---|
| `gossamer-hatch` | approval | request four days ahead (line 117), urgent, no TSSM sign-off (line 123): hold the flexible EgyptAir fare for the TSSM | `cobble-larch` (five days: BOOK), `wicket-moraine` (three days, TSSM signed: BOOK) |
| `umber-spindle` | approval | USAID trip without the client's written approval (lines 128-131): hold the cheapest flexible US-carrier fare for the client/donor | `basalt-orrery` (approval on file: BOOK United), `quartz-heddle` (FCDO: BOOK Emirates) |
| `vesper-lattice` | unclear | "the OPM Board and members of the Senior Management Team may be permitted to Travel in a class other than economy" (258-259) against the CFO approval rule (255-257): a member of staff (not SMT) with the CFO's business approval on corporate travel. Reading 1: the CFO's approval suffices, book business. Reading 2: business at OPM's cost is for the Board/SMT; other staff repay upgrades (261-262), book flexible economy. Holds either; accepts `UNCLEAR_POLICY_TEXT` or `APPROVAL_REQUIRED` | `sorrel-beacon` (SMT + CFO: BOOK business), `tansy-ledger` (staff, no CFO: BOOK economy) |

## Independent blind read (non-flag scenarios)

Re-derived from the frozen text and a dump of every `get_trip` record and `search_flights` listing (pinned and
background offers), without reading `rules.py`. Agreement on decision and offer for all 21 non-flag scenarios:

| Scenario | My reading | Agrees |
|---|---|---|
| copper-lagoon | flexible economy (253): KQ refundable 612 is the cheapest refundable; savers 468/505 are not flexible; PM approved | yes |
| mistral-quay | corporate marketing, economy: EK refundable 446; line manager approved | yes |
| orchard-tide | contract allows business, traveller wants economy: AI refundable 529 | yes |
| fennel-cairn | subcontract to 31 Jan covers a trip to 8 Jan (127); no nonstop; KL via AMS refundable 663 | yes |
| saltmarsh-vigil | BA refundable 540 sold out; AA refundable 575; PE allowed but not asked | yes |
| heron-quill | nonstop asked, budget 900; BA refundable nonstop 885 within budget (249-250): book it | yes |
| pewter-rill | BA refundable nonstop 915, SAA 930, both over 900: cheapest refundable, EK via DXB 720; lands 27th, workshop 28th | yes |
| lumen-thicket | contract permits PE, PE asked: SQ PE 1,280 (refundable; BA PE 1,340 dearer); no CFO for project travel | yes |
| garnet-thistle | contract economy only, no donor approval: SQ refundable economy 660 (fallback in the request) | yes |
| basalt-orrery | USAID: US carriers only (272); UA via EWR refundable 1,090 beats DL 1,150; client's written approval on file (128-131) | yes |
| quartz-heddle | FCDO: no carrier rule; EK via DXB refundable 960 cheapest refundable; no nonstop | yes |
| sorrel-beacon | SMT member, corporate, CFO approved business (255-260): cheapest business SAA 3,180 | yes |
| tansy-ledger | staff, no CFO approval, asks economy otherwise: BA refundable 840 | yes |
| wicket-moraine | request 3 days ahead (<5), TSSM short-notice sign-off on file (123): TK refundable 239 | yes |
| ember-cistern | project, contract permits business; CFO line is corporate only: AV business 2,410 | yes |
| drover-paddock | Edinburgh home to the London office where he is based: a commute, not Travel (65-67): refuse | yes |
| linnet-gable | contract economy, donor's written PE approval on file (253-255): AI PE 960 | yes |
| cobble-larch | request 27 Nov for 2 Dec = 5 days, "at least five": EgyptAir refundable 296; booking 2 days out is fine | yes |
| pallas-weir | UK-France: Eurostar 248 is dearer than every flight, so fly: AF refundable 198 | yes |
| marram-kite | personal long weekend on the business account: strictly prohibited (114-115), repayment irrelevant: refuse | yes |
| bracken-tarn | subcontract ends 31 Dec, trip runs to 8 Jan (127): refuse | yes |

Flags (not blind-read, by design): `gossamer-hatch`, `umber-spindle`, `vesper-lattice` (above).

Lint beyond the test: no request shares a 4-word phrase or a number with its own `must_keep` text (script run during
the build); the requests state no threshold.

## Hosted-cap estimate

23,601 characters of policy: at 0.2 tokens a character plus 1,800 (Thornton/NJC paid calibration) the first call
under `full` is about 6,500 input tokens (1.33 tokens a word gives about 4,500 for the policy itself), the second
about 7,100 and the third 7,600-8,600 (4 to 10 offers). A 3-call run is about 22,000 input tokens, about 30,000 with
the final message and output: far under the 65,536 hosted cap, with room for several extra tool calls.

## Unsure

- **Flexible = refundable** (decision 1) carries every booking. If a model reads "flexible economy" as ordinary
  economy it fails all 14 economy bookings; that is a reading of the handbook, not a slip in the key, but a paid
  run should check it first. The shared field text ("refunded or changed without a fee") is the bridge.
- **`gossamer-hatch`**: a strict reader could refuse a request made four days ahead ("must be submitted"). The
  handbook's own route for urgent travel (line 123) and the traveller's "short notice" make the hold the better
  reading; the request is worded identically in its five-day twin.
- **`bracken-tarn`**: a reader could hold the ticket until the contract is extended. No sign-off can cure it and the
  record shows no extension pending, so REFUSE.
- **`tansy-ledger`**: under reading 1 of `vesper-lattice` a reader might hold for the CFO; the request explicitly
  says not to chase approvals and to book economy otherwise, so BOOK economy on both readings.
- **`heron-quill` / `pewter-rill`**: a reader who weighs "direct within budget" above "flexible" would take the BA
  non-refundable nonstop (610). Line 253 makes the flexible fare the policy, so the key does not accept it.
- **Fly America** relies on knowing that United and Delta are US carriers (from the airline name) and that the
  rule means US carriers; no Open Skies question arises with Emirates and Qatar.

## Template change requests

1. Add Pakistan to the shared world (ISB, LHE, KHI) and PIA (`PK`, hubs ISB/LHE/KHI), so line 275's "no international
   Travel on Pakistan Airlines (PIA); internal flights within Pakistan in the absence of other carriers" can be
   tested (an international PIA fare refused, a domestic one allowed when it is the only carrier).
2. A way to mark a carrier as lacking FAA/EU approval without asserting it about a real airline (a fictional regional
   carrier, or a per-scenario carrier note the world shows), for lines 264-271.
3. Observation only: `instantiate.py` leaves Thornton wording in `product/product.yaml`, `pyproject.toml`'s
   description and `README.md`; rewritten here.

## Acceptance outputs

```
$ uv run pytest -q
196 passed, 3 skipped in 2.62s        (the 3 skips: duration tests with no duration rule to test)
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 9ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .          (COMP580/nanoagent/nanoagent/.venv/bin/nanoagent)
exit 0
$ nanoagent plugin pack . <scratchpad>/opml-flight-policy.tar.gz
packed . into .../opml-flight-policy.tar.gz (155813 bytes)
$ python ../_template/tools/stock_verify.py .   (nanoagent venv python)
basalt-orrery        right=True score=1.00 identical=True wrong-decision-rejected=True
bracken-tarn         right=True score=1.00 identical=True wrong-decision-rejected=True
cobble-larch         right=True score=1.00 identical=True wrong-decision-rejected=True
copper-lagoon        right=True score=1.00 identical=True wrong-decision-rejected=True
drover-paddock       right=True score=1.00 identical=True wrong-decision-rejected=True
ember-cistern        right=True score=1.00 identical=True wrong-decision-rejected=True
fennel-cairn         right=True score=1.00 identical=True wrong-decision-rejected=True
garnet-thistle       right=True score=1.00 identical=True wrong-decision-rejected=True
gossamer-hatch       right=True score=1.00 identical=True wrong-decision-rejected=True
heron-quill          right=True score=1.00 identical=True wrong-decision-rejected=True
linnet-gable         right=True score=1.00 identical=True wrong-decision-rejected=True
lumen-thicket        right=True score=1.00 identical=True wrong-decision-rejected=True
marram-kite          right=True score=1.00 identical=True wrong-decision-rejected=True
mistral-quay         right=True score=1.00 identical=True wrong-decision-rejected=True
orchard-tide         right=True score=1.00 identical=True wrong-decision-rejected=True
pallas-weir          right=True score=1.00 identical=True wrong-decision-rejected=True
pewter-rill          right=True score=1.00 identical=True wrong-decision-rejected=True
quartz-heddle        right=True score=1.00 identical=True wrong-decision-rejected=True
saltmarsh-vigil      right=True score=1.00 identical=True wrong-decision-rejected=True
sorrel-beacon        right=True score=1.00 identical=True wrong-decision-rejected=True
tansy-ledger         right=True score=1.00 identical=True wrong-decision-rejected=True
umber-spindle        right=True score=1.00 identical=True wrong-decision-rejected=True
vesper-lattice       right=True score=1.00 identical=True wrong-decision-rejected=True
wicket-moraine       right=True score=1.00 identical=True wrong-decision-rejected=True
24 scenarios, 0 failures
```
