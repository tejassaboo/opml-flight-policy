# Independent audit: opml-flight-policy (2026-11-25)

I audited the builder's commit cad846d against `pilot_work/tier_plan/build/WAVE3_AUDIT_BRIEF.md`, the 12 lessons in
`WAVE3_BUILD_BRIEF.md`, MASTER_PLAN section 4 and EDGE_CASES sections 1-3 and 5. No money was spent and nothing
was pushed. Line numbers refer to the frozen handbook (`src/plugin/data/policy.txt`).

## Method

I printed every scenario's `get_trip` record and every pinned `search_flights` listing through the plugin's own
tools, then answered each case from the handbook text alone, before reading `rules.py`. After that I compared my
answers with every accept set: decision, offer, cabin, reason, approver and clause.

## Verdict

**Pass after fixes.** My decision and offer agree with the key on all 21 non-flag cases. The three flags are sound:

- `gossamer-hatch` and `umber-spindle` are holds for a missing sign-off.
- `vesper-lattice` is a real two-reading clause, and it accepts the held offer of each reading.

Twin pairs differ in one fact. Requests carry no rule wording, and the decline sentence is in the instructions.
The defects were in how one handbook word reaches the agent and in a few accept sets. No world fact that decides a
key changed.

## Defects found and fixed

1. **"Flexible economy" was not tied to the world's fares (affects every economy answer: 14 BOOKs and 3 holds).**
   - Line 253 says "OPM's policy is to book flexible economy class flights". The key reads that as the refundable
     fare.
   - The agent only sees the offer field `refundable` ("refunded or changed without a fee"). Its tools are
     `get_trip` and `search_flights`; it cannot see `booking_requirements`.
   - A careful reader could take "flexible economy class" to mean plain economy, with "flexible" a loose adjective.
     Lines 107-108 ("most economical") push the same way. That reader books the saver and fails every economy case.
   - Accepting both fares was ruled out: the always-cheapest agent would then pass most economy bookings, far over
     40%.
   - Fix: every trip record now carries a neutral note on what the fare types are called:

     > In OPM's booking tool, an economy fare marked refundable (changed or refunded without a fee) is the fare
     > OPM's travel service providers sell as flexible economy; an economy fare that is not refundable is a
     > restricted saver fare.

     It names the fare types and says nothing about which one to book. It is on all 24 records, so it is not a
     signal in itself, and the twins stay one fact apart.
2. **`heron-quill`: the cheaper flexible connection was refused.**
   - Lines 249-250 say a direct option within budget "may be selected over a cheaper less direct route". That
     permits the nonstop but does not require it.
   - Line 248 and lines 107-108 make the cheapest flexible fare (Emirates via Dubai, £720) compliant too. This
     follows the georgia-sao precedent (`cypress-knob`, `oriole-shoal`).
   - Fix: `dubai-flex` is now accepted beside `british-flex`, and `LOWEST_FARE` and `FLEXIBLE_ECONOMY_POLICY` are
     added to the reasons. Lesson 12 allows this, because the ground for passing over the nonstop is the
     lowest-fare rule itself. The twin still splits: `pewter-rill` accepts only the connection.
3. **`garnet-thistle`, `tansy-ledger`: a specific decline ground was missing.**
   - Line 253 ("book flexible economy ... within this class range only") is a ground for declining a premium cabin
     in its own right.
   - Fix: `FLEXIBLE_ECONOMY_POLICY` is added beside `PREMIUM_CABIN_NOT_PERMITTED` and `UPGRADE_NOT_ELIGIBLE`.
4. **`pewter-rill`: the same specific ground was missing.**
   - The only nonstop within budget is the British Airways saver (£610). It is not flexible economy, and that is
     part of why the nonstop is declined.
   - Fix: `FLEXIBLE_ECONOMY_POLICY` is added beside the over-budget codes and `LOWEST_FARE`.
5. **`bracken-tarn`: a reader could hold the ticket "until the contract is extended" instead of refusing.**
   - Fix: both twins (`bracken-tarn` and `fennel-cairn`) now carry the note "No extension or renewal of this
     subcontract is pending or planned."
   - With that note, nothing can cure the gap and no sign-off is awaited, so REFUSE is the only reading. The note is
     identical in both twins, so they still differ only in the contract end date.

## The builder's unsure list, settled

- **Flexible = refundable.** Settled by defect 1. With the note, "book flexible economy ... within this class range
  only" (253-255) leaves no saver-fare reading.
- **`gossamer-hatch`: hold for the TSSM, not refuse.** Kept as a hold.
  - Line 117's "must be submitted at least five days prior" is followed at once, in the same section, by the route
    for urgent travel: "In cases of urgent travel, please contact the TSSM" (123).
  - Lines 353-354 ("act immediately and OPM will manage necessary approvals retrospectively") sits under "In Case of
    Emergency" and is about changing plans during an emergency. A ministry moving a meeting is not an emergency, so
    it does not license booking now.
  - The traveller says it is short notice forced by the ministry, so this is urgent travel with a named channel.
    REFUSE ("no ticket at all") would ignore that channel. BOOK would skip the "must" with no TSSM sign-off on file.
  - The twin `wicket-moraine`, with the TSSM's short-notice sign-off on file, shows what clears it.
  - The accept set is APPROVAL_REQUIRED or ADVANCE_PURCHASE_TOO_LATE, approver TSSM only (lesson 1), clause
    BOOKING_TRAVEL.
- **`bracken-tarn`: refuse, not hold.** Settled by defect 5.
- **`tansy-ledger`: book economy, not hold for the CFO.**
  - Business needs the CFO's approval on either reading of lines 255-262.
  - The request says to book economy if business needs any extra sign-off, and says "I don't want to chase
    approvals". So the answer is BOOK economy on every reading.
- **`heron-quill` / `pewter-rill`: never the non-refundable nonstop within budget.** Kept, now on solid ground.
  - The British Airways saver nonstop (£610) is within budget and cheaper than any flexible fare, but it is a saver,
    not flexible economy. Line 253 and the trip record's note put it outside "this class range".
  - Lines 249-250 choose between flexible options by budget. They do not override the fare class.
  - Neither key accepts the saver, and the always-cheapest agent still fails both.
- **Fly America.** Kept.
  - United and Delta are US carriers by name.
  - Emirates and Qatar fall under no Open Skies exception to the Act, which covers EU, Swiss, Australian and
    Japanese carriers. So outside knowledge gives the same answer.

## Seen and kept

- **Manager approval.** The Project Manager's or line manager's approval is on file in every business trip, and
  every BOOK accepts NONE and that role (4').
- **`quartz-heddle` written-approval sign-off.** Its "Prime contractor's agreement officer" sign-off on an FCDO trip
  is a harmless distractor: it is accepted beside NONE.
- **`cobble-larch` lead time.** 27 November to 2 December is 5 calendar days, and the instructions say days are
  calendar days. "At least five" is met.
- **`saltmarsh-vigil`.** The sold-out British Airways flexible fare is correctly skipped.
- **`pallas-weir`.** The train (£248) costs more than every flexible flight, so the flight is booked.
- **`drover-paddock`.** Home in Edinburgh and the office in London makes this a commute, so it is not Travel (65-67).

## Degenerate agents

- `MAX_PASS_ALWAYS_LOWEST`: **0 -> 0** of 24. The always-cheapest agent's seat is a saver fare in every case,
  including `heron-quill` (Emirates saver, £520).
- `MAX_PASS_ALWAYS_FLAG`: 1, unchanged (`vesper-lattice`).

## Files changed

- `src/plugin/rules.py` and `verifier/rules.py` (byte-identical): the `heron-quill` connection, and the extra
  `FLEXIBLE_ECONOMY_POLICY` reasons.
- `tests/build_scenarios.py`: `FARE_NOTE` on every trip, the subcontract note, and the accept sets.
- All 24 scenario JSON files, regenerated.
- `README.md`: four rows.

## Check outputs

- `uv run pytest -q`: 196 passed, 3 skipped (the duration tests, which have no duration rule to test).
- `uv run ruff check .`: all checks passed.
- `uv lock --check`: ok.
- `python3 ../_template/check_shared.py .`: ok.
- `stock_verify.py .`: 24 scenarios, 0 failures.
- `nanoagent plugin inspect .`: exit 0.
