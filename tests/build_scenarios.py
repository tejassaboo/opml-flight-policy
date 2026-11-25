"""Writes the OPM Travel Policy scenario JSON files (an authoring aid, not a test; the JSON files are the truth).

    uv run python tests/build_scenarios.py

Expected answers are hand-written here; tests/test_scenarios.py checks them against rules.solve. Every fare is in
pence (cents of GBP, handbook.json currency).
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = (ROOT / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = ROOT / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def aside(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- clauses -----
TRAVEL_DEF = keep(65, 67, None, "Travel is not a commute between home and the normal place of work")
SCOPE_DEF = keep(89, 92, "It does not relate to a commute, or travel between a person's normal place of residence and "
                 "normal place of work.", "the scope repeats the definition")
PRINCIPLE = keep(107, 108, "must use the most economical and direct route available.", "the value-for-money principle")
PERSONAL_BAN = keep(114, 115, "The use of the OPM business account and/or Project funds to book personal travel is "
                    "strictly prohibited.", "no personal travel on the business account")
NO_PERSONAL_COSTS = keep(142, 144, None, "no cost of personal travel is reimbursed")
LEAD = keep(117, 117, "Travel requests must be submitted at least five days prior to Travel", "the request lead time")
MANAGER = keep(122, 123, "All Travel and associated costs must be approved by the relevant Project Manager or Line "
               "Manager prior to booking.", "the manager approves every trip before booking")
URGENT = keep(123, 123, "In cases of urgent travel, please contact the TSSM.", "urgent travel goes to the TSSM")
SUBCONTRACT = keep(127, 127, "Subcontractors must have a valid contract covering the duration of their trip.",
                   "a subcontractor's contract must cover the whole trip")
USAID_APPROVAL = keep(128, 131, None, "USAID travel needs the client's written approval in advance")
ROUTE = keep(248, 250, "All flight bookings made will take account of the most cost-effective, direct route available. "
             "Where the most direct option available is within budget parameters, this option may be selected over a "
             "cheaper less direct route.", "the cost-effective direct route; a direct option within budget")
FLEX = keep(253, 255, "OPM's policy is to book flexible economy class flights. Unless expressly permitted by a client "
            "contract, or where specific written approval of the client/donor has been received, quotes provided for "
            "Travel bookings will be within this class range only.", "flexible economy unless the client allows more")
CFO = keep(255, 257, "For corporate travel, internal approval will be required from the Chief Financial Officer prior "
           "to any bookings in Business or Premium Economy being finalised.", "corporate premium cabins need the CFO")
SMT = keep(258, 262, None, "Board and SMT may travel above economy with approval; other staff upgrade at their own cost")
FLY_AMERICA = keep(272, 274, None, "USAID projects: US Flag Carrier Rules (Fly America)")
EUROSTAR_AIR = keep(250, 252, "For Travel between the UK and the EU, Eurostar may present a more optimal route/fare/price, "
                    "and this should be examined in addition to flights.", "Eurostar is examined beside flights")
TRAINS = keep(297, 299, None, "Eurostar where it is cheaper, unless its timings are prohibitive")
OWNER = keep(161, 161, None, "the COO is accountable for the policy")

ADVANCE_SOFT = aside(120, 121, "travel/logistical arrangements should be booked as far in advance as possible.",
                     "a soft wish, not a booking condition")
INSURANCE = aside(339, 340, "Travellers booking Travel for more than 6 weeks duration must email James Warton",
                  "an insurance step, not a booking condition")
DOCTOR = aside(364, 366, "of less than 60 days must provide a written statement from their doctor",
               "a traveller's document for USAID trips, not a booking condition")
AIR_MILES = aside(260, 261, "Where feasible, the use of Air Miles should be explored for any corporate-related Travel.",
                  "a soft suggestion that does not choose the ticket")
VISA = aside(378, 381, "If a business visa is not available to purchase upon arrival, the visa must be received",
             "the visa is already received")
EXPENSES = aside(391, 392, "Expense claims must be submitted within 90 days of the cost being incurred",
                 "a claims deadline, not a booking rule")
UPGRADE_SELF = aside(261, 262, "Should other Staff wish to upgrade their Travel from economy, they may do so, provided "
                     "that the Staff member reimburses OPM for any additional costs.", "about upgrades, not personal trips")

# ----- builders -----


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "passenger": "STAFF", "seniority": "STAFF",
        "home_airport": "LHR", "workplace_airport": "LHR", "origin": "LHR", "destination": "", "travel_date": "",
        "trip_end": "", "request_submitted": "", "booking_date": "", "travel_kind": "PROJECT", "funder": "",
        "contract_cabin": "ECONOMY", "contract_end": "", "purpose": "", "purpose_kind": "PROJECT_WORK",
        "requested_cabin": "ECONOMY", "wants_nonstop": False, "fare_budget_cents": 0, "rail_fare_cents": 0,
        "rail_arrival": "", "sign_offs": [], "notes": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    if base["travel_kind"] == "CORPORATE":
        base["contract_cabin"] = fields.get("contract_cabin", "NONE")
    return base


def sign(role, name, subject="TRIP", cabin="NONE"):
    return {"role": role, "name": name, "subject": subject, "cabin": cabin}


def offer(slot, flight, cabin, pence, refundable=False, seats=True):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": pence}
    if refundable:
        data["refundable"] = True
    if not seats:
        data["seats"] = False
    return data


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": slots, "cabins": cabins, "reason_codes": sorted(reasons),
            "approvers": sorted(approvers), "clauses": sorted(clauses), "unclear_phrase": phrase}


def search(origin, destination, date, flights, offers, background=0):
    # handbook.json background_offers is 0, so a search the scenario does not pin lists nothing; each pinned
    # search sets its own number.
    return {"name": "main", "origin": origin, "destination": destination, "date": date, "return_date": "",
            "background": background, "flights": flights, "offers": offers}


S = []


def scenario(id, category, overlays, request, trip_, search_spec, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": list(overlays), "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": [search_spec]}, "expected": exp, "must_keep": list(must_keep),
        "distractors": list(distractors), "design_notes": notes,
    })


FARE = ["AIR_CLASS_AND_RATES", "GENERAL_PROVISIONS", "PRINCIPLES"]
CLASS = ["AIR_CLASS_AND_RATES", "GENERAL_PROVISIONS"]
FLEX_CODES = ["LOWEST_FARE", "FLEXIBLE_ECONOMY_POLICY"]
NOT_PERMITTED = ["PREMIUM_CABIN_NOT_PERMITTED", "UPGRADE_NOT_ELIGIBLE"]
CLIENT_CABIN = ["CLIENT_PERMITS_PREMIUM_CABIN", "CLIENT_REIMBURSABLE"]
US_CODES = ["FLY_AMERICA_US_CARRIER_REQUIRED", "NATIONAL_CARRIER_REQUIRED", "PREFERRED_CARRIER_REQUIRED"]
PM = sign("PROJECT_MANAGER", "Helen Achterberg")
LM = sign("LINE_MANAGER", "Sarah Clarke")


def on_file(*roles):
    """SYNC_NOTES 4': a booking whose sign-offs are on file accepts those roles and NONE."""
    return ["NONE", *roles]


# ===== easy (5) =====

scenario(
    "copper-lagoon", "easy", [],
    "I need to get to Nairobi on 19 January for the county health financing review, economy please. The review starts "
    "two days after I land.",
    trip(traveller_name="Amara Okafor", traveller_title="Senior Consultant, Health Systems", destination="NBO",
         travel_date="2027-01-19", trip_end="2027-01-30", request_submitted="2026-12-14", booking_date="2026-12-16",
         funder="FCDO", purpose="County health financing review for an FCDO-funded programme", sign_offs=[PM]),
    search("LHR", "NBO", "2027-01-19", {
        "kenya": {"carrier": "KQ", "depart": "19:25"},
        "british": {"carrier": "BA", "depart": "20:40"},
    }, [
        offer("kenya-saver", "kenya", "ECONOMY", 46_800),
        offer("kenya-flex", "kenya", "ECONOMY", 61_200, refundable=True),
        offer("british-saver", "british", "ECONOMY", 50_500),
        offer("british-flex", "british", "ECONOMY", 65_500, refundable=True),
        offer("british-business", "british", "BUSINESS", 294_000, refundable=True),
    ], background=2),
    expected("BOOK", ["kenya-flex"], ["ECONOMY"], FLEX_CODES, on_file("PROJECT_MANAGER"), FARE),
    [FLEX, ROUTE, MANAGER],
    "Line 253: the policy is to book flexible economy, so the cheapest refundable economy fare: Kenya Airways at "
    "612 pounds (the two non-refundable fares are cheaper but are not flexible). The Project Manager approved the "
    "trip before booking (lines 122-123). Request 36 days ahead.")

scenario(
    "mistral-quay", "easy", [],
    "Please book me economy to Dubai on 9 February. We're running a stand at the education donors' forum and setup is "
    "the day after I arrive.",
    trip(traveller_name="Tom Hargreaves", traveller_title="Business Development Manager", destination="DXB",
         travel_date="2027-02-09", trip_end="2027-02-13", request_submitted="2027-01-11", booking_date="2027-01-12",
         travel_kind="CORPORATE", purpose="Marketing stand at an education donors' forum", purpose_kind="MARKETING",
         sign_offs=[LM]),
    search("LHR", "DXB", "2027-02-09", {
        "emirates": {"carrier": "EK", "depart": "08:15"},
        "british": {"carrier": "BA", "depart": "09:50"},
    }, [
        offer("emirates-saver", "emirates", "ECONOMY", 31_800),
        offer("emirates-flex", "emirates", "ECONOMY", 44_600, refundable=True),
        offer("british-saver", "british", "ECONOMY", 34_900),
        offer("british-flex", "british", "ECONOMY", 47_200, refundable=True),
    ], background=2),
    expected("BOOK", ["emirates-flex"], ["ECONOMY"], FLEX_CODES, on_file("LINE_MANAGER"), FARE),
    [FLEX, ROUTE, MANAGER],
    "Corporate marketing trip: flexible economy (line 253), the cheapest refundable economy fare is Emirates at 446 "
    "pounds. The line manager approved it (lines 122-123). No premium cabin is asked, so the CFO line does not arise.",
    distractors=[AIR_MILES])

scenario(
    "orchard-tide", "easy", ["upgrade_not_taken"],
    "Economy to Delhi on 2 March is fine for me; I'd rather keep the travel budget for the field visits. The inception "
    "meeting is the day after I land.",
    trip(traveller_name="Rohan Mehta", traveller_title="Principal Consultant, Education", destination="DEL",
         travel_date="2027-03-02", trip_end="2027-03-20", request_submitted="2027-01-25", booking_date="2027-01-27",
         funder="World Bank", contract_cabin="BUSINESS",
         purpose="Inception mission for a World Bank-funded school finance programme", sign_offs=[PM]),
    search("LHR", "DEL", "2027-03-02", {
        "india": {"carrier": "AI", "depart": "11:40"},
        "british": {"carrier": "BA", "depart": "13:05"},
    }, [
        offer("india-saver", "india", "ECONOMY", 38_400),
        offer("india-flex", "india", "ECONOMY", 52_900, refundable=True),
        offer("india-business", "india", "BUSINESS", 218_000, refundable=True),
        offer("british-saver", "british", "ECONOMY", 41_200),
        offer("british-flex", "british", "ECONOMY", 57_800, refundable=True),
        offer("british-business", "british", "BUSINESS", 236_000, refundable=True),
    ], background=2),
    expected("BOOK", ["india-flex"], ["ECONOMY"], FLEX_CODES, on_file("PROJECT_MANAGER"), FARE),
    [FLEX, ROUTE, MANAGER],
    "The client contract permits business (lines 253-255), but that is a permission and the traveller asks for "
    "economy, so the cheapest flexible economy fare: Air India at 529 pounds.")

FENNEL_REQUEST = ("I fly out to Nairobi from Edinburgh on 28 December for the endline evaluation fieldwork, and I'm out "
                  "there until 8 January. Economy, please.")
FENNEL_FLIGHTS = {
    "london": {"carrier": "BA", "via": ["LHR"], "depart": "06:40", "layovers": [125]},
    "amsterdam": {"carrier": "KL", "via": ["AMS"], "depart": "07:10", "layovers": [150]},
    "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "08:30", "layovers": [175]},
}
FENNEL_OFFERS = [
    offer("london-saver", "london", "ECONOMY", 52_000),
    offer("london-flex", "london", "ECONOMY", 69_800, refundable=True),
    offer("amsterdam-saver", "amsterdam", "ECONOMY", 49_500),
    offer("amsterdam-flex", "amsterdam", "ECONOMY", 66_300, refundable=True),
    offer("dubai-saver", "dubai", "ECONOMY", 47_900),
    offer("dubai-flex", "dubai", "ECONOMY", 71_500, refundable=True),
]


def fennel_trip(name, contract_end):
    return trip(traveller_name=name, traveller_title="Independent evaluation consultant", passenger="SUBCONTRACTOR",
                home_airport="EDI", workplace_airport="EDI", origin="EDI", destination="NBO",
                travel_date="2026-12-28", trip_end="2027-01-08", request_submitted="2026-11-30",
                booking_date="2026-12-02", funder="FCDO", contract_end=contract_end,
                purpose="Endline evaluation fieldwork for an FCDO-funded water programme",
                sign_offs=[sign("PROJECT_MANAGER", "Helen Achterberg")])


scenario(
    "fennel-cairn", "easy", ["multi_leg", "date_arithmetic", "month_end", "outside_air_section"],
    FENNEL_REQUEST, fennel_trip("Iain Ross", "2027-01-31"),
    search("EDI", "NBO", "2026-12-28", FENNEL_FLIGHTS, FENNEL_OFFERS),
    expected("BOOK", ["amsterdam-flex"], ["ECONOMY"], FLEX_CODES, on_file("PROJECT_MANAGER"), FARE),
    [SUBCONTRACT, FLEX, ROUTE, MANAGER],
    "A subcontractor's contract must cover the trip (line 127): it runs to 31 January and the trip ends 8 January, "
    "so it does. No nonstop flies Edinburgh-Nairobi; the cheapest flexible economy fare is KLM via Amsterdam at 663 "
    "pounds.",
    twin_of="bracken-tarn", twin_fact="contract ends 31 January 2027 or 31 December 2026")

scenario(
    "saltmarsh-vigil", "easy", ["upgrade_not_taken"],
    "Economy to New York on 16 February please; a daytime flight is fine in the back. The consultation starts the "
    "following morning.",
    trip(traveller_name="Hannah Lewis", traveller_title="Consultant, Social Protection", destination="JFK",
         travel_date="2027-02-16", trip_end="2027-02-20", request_submitted="2027-01-18", booking_date="2027-01-19",
         funder="UNICEF", contract_cabin="PREMIUM_ECONOMY",
         purpose="Stakeholder consultation for a UNICEF-funded cash transfer review", sign_offs=[PM]),
    search("LHR", "JFK", "2027-02-16", {
        "british": {"carrier": "BA", "depart": "09:15"},
        "american": {"carrier": "AA", "depart": "11:05"},
        "virgin": {"carrier": "VS", "depart": "13:30"},
        "delta": {"carrier": "DL", "depart": "08:20"},
    }, [
        offer("delta-saver", "delta", "ECONOMY", 41_000),
        offer("british-saver", "british", "ECONOMY", 43_500),
        offer("british-flex", "british", "ECONOMY", 54_000, refundable=True, seats=False),
        offer("british-premium", "british", "PREMIUM_ECONOMY", 112_000, refundable=True),
        offer("american-flex", "american", "ECONOMY", 57_500, refundable=True),
        offer("virgin-flex", "virgin", "ECONOMY", 59_000, refundable=True),
    ], background=2),
    expected("BOOK", ["american-flex"], ["ECONOMY"], FLEX_CODES, on_file("PROJECT_MANAGER"), FARE),
    [FLEX, ROUTE, MANAGER],
    "Flexible economy (line 253). British Airways' 540-pound flexible fare is sold out, so American at 575 pounds. "
    "The contract would allow premium economy, but the traveller asks for economy.")

# ===== boundary twins (6) =====

JNB_REQUEST = ("Could you book the direct overnight flight to Johannesburg on 26 January if possible? The workshop with "
               "the Treasury starts on the 28th.")


def jnb_trip(name):
    return trip(traveller_name=name, traveller_title="Senior Consultant, Public Financial Management",
                destination="JNB", travel_date="2027-01-26", trip_end="2027-02-05", request_submitted="2026-12-21",
                booking_date="2026-12-22", funder="FCDO", wants_nonstop=True, fare_budget_cents=90_000,
                purpose="Budget reform workshop with the Treasury for an FCDO-funded programme", sign_offs=[PM])


def jnb_offers(british_flex):
    return [
        offer("british-saver", "british", "ECONOMY", 61_000),
        offer("british-flex", "british", "ECONOMY", british_flex, refundable=True),
        offer("african-saver", "african", "ECONOMY", 64_000),
        offer("african-flex", "african", "ECONOMY", 93_000, refundable=True),
        offer("dubai-saver", "dubai", "ECONOMY", 52_000),
        offer("dubai-flex", "dubai", "ECONOMY", 72_000, refundable=True),
        offer("amsterdam-flex", "amsterdam", "ECONOMY", 76_000, refundable=True),
    ]


JNB_FLIGHTS = {
    "british": {"carrier": "BA", "depart": "19:05"},
    "african": {"carrier": "SA", "depart": "21:15"},
    "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "13:40", "layovers": [155]},
    "amsterdam": {"carrier": "KL", "via": ["AMS"], "depart": "09:10", "layovers": [110]},
}

scenario(
    "heron-quill", "boundary_twin", ["dearer_option"], JNB_REQUEST, jnb_trip("Grace Mensah"),
    search("LHR", "JNB", "2027-01-26", JNB_FLIGHTS, jnb_offers(88_500)),
    expected("BOOK", ["british-flex"], ["ECONOMY"], ["DIRECT_OPTION_WITHIN_BUDGET", "ALTERNATE_ROUTE_WITHIN_MARGIN"],
             on_file("PROJECT_MANAGER"), FARE),
    [ROUTE, FLEX, MANAGER],
    "Lines 249-250: the most direct option within budget may be selected over a cheaper less direct route. The "
    "British Airways flexible nonstop is 885 pounds, within the 900-pound fare budget, so it is booked as asked; the "
    "Emirates connection (720) is cheaper but need not be taken. The SAA flexible nonstop (930) is over budget.",
    twin_of="pewter-rill", twin_fact="British Airways flexible nonstop fare 885 or 915 pounds against a 900-pound budget")

scenario(
    "pewter-rill", "boundary_twin", ["multi_leg"], JNB_REQUEST, jnb_trip("Grace Mensah"),
    search("LHR", "JNB", "2027-01-26", JNB_FLIGHTS, jnb_offers(91_500)),
    expected("BOOK", ["dubai-flex"], ["ECONOMY"],
             ["DIRECT_OPTION_OVER_BUDGET", "ALTERNATE_ROUTE_TOO_EXPENSIVE", "LOWEST_FARE"], on_file("PROJECT_MANAGER"),
             FARE),
    [ROUTE, FLEX, PRINCIPLE, MANAGER],
    "Every flexible nonstop is over the 900-pound fare budget (BA 915, SAA 930), so lines 248-250 give the most "
    "cost-effective route: the cheapest flexible economy fare, Emirates via Dubai at 720 pounds. All flights land on "
    "the 27th and the workshop is on the 28th.",
    twin_of="heron-quill", twin_fact="British Airways flexible nonstop fare 885 or 915 pounds against a 900-pound budget")

SIN_REQUEST = ("Premium economy to Singapore on 23 February, if the contract allows it; if not, book what the policy "
               "allows. I have to be at the regional inception workshop on the 25th.")
SIN_FLIGHTS = {
    "singapore": {"carrier": "SQ", "depart": "11:30"},
    "british": {"carrier": "BA", "depart": "21:20"},
}
SIN_OFFERS = [
    offer("singapore-saver", "singapore", "ECONOMY", 49_000),
    offer("singapore-flex", "singapore", "ECONOMY", 66_000, refundable=True),
    offer("singapore-premium", "singapore", "PREMIUM_ECONOMY", 128_000, refundable=True),
    offer("british-saver", "british", "ECONOMY", 51_500),
    offer("british-flex", "british", "ECONOMY", 69_000, refundable=True),
    offer("british-premium", "british", "PREMIUM_ECONOMY", 134_000),
    offer("british-business", "british", "BUSINESS", 310_000, refundable=True),
]


def sin_trip(cabin):
    return trip(traveller_name="Wei Ling Tan", traveller_title="Senior Consultant, Climate Finance", destination="SIN",
                travel_date="2027-02-23", trip_end="2027-03-05", request_submitted="2027-01-20",
                booking_date="2027-01-21", funder="Asian Development Bank", contract_cabin=cabin,
                requested_cabin="PREMIUM_ECONOMY",
                purpose="Regional inception workshop for an Asian Development Bank climate finance project",
                sign_offs=[PM])


scenario(
    "lumen-thicket", "boundary_twin", ["dearer_option"], SIN_REQUEST, sin_trip("PREMIUM_ECONOMY"),
    search("LHR", "SIN", "2027-02-23", SIN_FLIGHTS, SIN_OFFERS),
    expected("BOOK", ["singapore-premium"], ["PREMIUM_ECONOMY"], CLIENT_CABIN, on_file("PROJECT_MANAGER"), CLASS),
    [FLEX, MANAGER],
    "Lines 253-255: flexible economy unless expressly permitted by a client contract. This contract permits premium "
    "economy and the traveller asks for it: the cheapest premium economy seat, Singapore Airlines at 1,280 pounds "
    "(also a flexible fare). The CFO line (255-257) is for corporate travel only.",
    twin_of="garnet-thistle", twin_fact="client contract allows premium economy or only economy",
    distractors=[aside(255, 257, "For corporate travel, internal approval will be required from the Chief Financial "
                       "Officer", "this is project travel")])

scenario(
    "garnet-thistle", "boundary_twin", [], SIN_REQUEST, sin_trip("ECONOMY"),
    search("LHR", "SIN", "2027-02-23", SIN_FLIGHTS, SIN_OFFERS),
    expected("BOOK", ["singapore-flex"], ["ECONOMY"], NOT_PERMITTED, on_file("PROJECT_MANAGER"), FARE),
    [FLEX, MANAGER],
    "The contract allows only economy and no written client approval of a better cabin is on file, so quotes stay in "
    "flexible economy (lines 253-255): Singapore Airlines at 660 pounds. The request says to book what the policy "
    "allows.",
    twin_of="lumen-thicket", twin_fact="client contract allows premium economy or only economy")

NBO_US_REQUEST = ("Economy to Nairobi on 9 March for the nutrition programme's mid-term review, please. The review opens "
                  "on the 11th.")
NBO_US_FLIGHTS = {
    "newark": {"carrier": "UA", "via": ["EWR"], "depart": "17:50", "layovers": [95]},
    "kennedy": {"carrier": "DL", "via": ["JFK"], "depart": "16:30", "layovers": [120]},
    "dubai": {"carrier": "EK", "via": ["DXB"], "depart": "10:15", "layovers": [160]},
    "doha": {"carrier": "QR", "via": ["DOH"], "depart": "18:40", "layovers": [140]},
}
NBO_US_OFFERS = [
    offer("newark-saver", "newark", "ECONOMY", 89_000),
    offer("newark-flex", "newark", "ECONOMY", 109_000, refundable=True),
    offer("kennedy-saver", "kennedy", "ECONOMY", 93_000),
    offer("kennedy-flex", "kennedy", "ECONOMY", 115_000, refundable=True),
    offer("dubai-saver", "dubai", "ECONOMY", 72_000),
    offer("dubai-flex", "dubai", "ECONOMY", 96_000, refundable=True),
    offer("doha-flex", "doha", "ECONOMY", 99_000, refundable=True),
]
CLIENT_OK = sign("CLIENT_OR_DONOR", "Prime contractor's agreement officer, in writing")


def nbo_us_trip(funder, sign_offs):
    return trip(traveller_name="Daniel Price", traveller_title="Senior Consultant, Nutrition (Washington DC office)",
                home_airport="IAD", workplace_airport="IAD", origin="IAD", destination="NBO",
                travel_date="2027-03-09", trip_end="2027-03-19", request_submitted="2027-02-08",
                booking_date="2027-02-10", funder=funder,
                purpose=f"Mid-term review of a {funder}-funded nutrition programme in Kenya",
                sign_offs=[sign("PROJECT_MANAGER", "Helen Achterberg"), *sign_offs])


scenario(
    "basalt-orrery", "boundary_twin", ["multi_leg", "dearer_option"], NBO_US_REQUEST,
    nbo_us_trip("USAID", [CLIENT_OK]),
    search("IAD", "NBO", "2027-03-09", NBO_US_FLIGHTS, NBO_US_OFFERS),
    expected("BOOK", ["newark-flex"], ["ECONOMY"], [*US_CODES, *FLEX_CODES],
             on_file("PROJECT_MANAGER", "CLIENT_OR_DONOR"), [*FARE, "FLIGHT_CARRIERS", "PROJECT_TRAVEL"]),
    [FLY_AMERICA, FLEX, USAID_APPROVAL, MANAGER],
    "USAID funds the project, so US Flag Carrier Rules apply (line 272): only United and Delta qualify. The cheapest "
    "flexible economy fare on a US carrier is United via Newark at 1,090 pounds, though Emirates (960) and Qatar (990) "
    "are cheaper. The client's written approval, which USAID travel needs (lines 128-131), is on file.",
    twin_of="quartz-heddle", twin_fact="the project is funded by USAID or by FCDO",
    distractors=[DOCTOR])

scenario(
    "quartz-heddle", "boundary_twin", ["multi_leg"], NBO_US_REQUEST, nbo_us_trip("FCDO", [CLIENT_OK]),
    search("IAD", "NBO", "2027-03-09", NBO_US_FLIGHTS, NBO_US_OFFERS),
    expected("BOOK", ["dubai-flex"], ["ECONOMY"], FLEX_CODES, on_file("PROJECT_MANAGER", "CLIENT_OR_DONOR"), FARE),
    [FLEX, ROUTE, MANAGER],
    "An FCDO project: no US Flag Carrier rule (line 272 is for USAID projects), so the cheapest flexible economy "
    "fare, Emirates via Dubai at 960 pounds. No nonstop flies the route. The client's written approval on file is not "
    "needed (4(b): accepted beside NONE).",
    twin_of="basalt-orrery", twin_fact="the project is funded by USAID or by FCDO")

# ===== multi-rule (4) =====

JNB_APRIL_FLIGHTS = {
    "british": {"carrier": "BA", "depart": "19:05"},
    "african": {"carrier": "SA", "depart": "21:15"},
}
JNB_APRIL_OFFERS = [
    offer("british-saver", "british", "ECONOMY", 59_000),
    offer("british-flex", "british", "ECONOMY", 84_000, refundable=True),
    offer("british-business", "british", "BUSINESS", 342_000, refundable=True),
    offer("african-saver", "african", "ECONOMY", 62_000),
    offer("african-flex", "african", "ECONOMY", 86_000, refundable=True),
    offer("african-business", "african", "BUSINESS", 318_000, refundable=True),
]
CFO_BUSINESS = sign("CHIEF_FINANCIAL_OFFICER", "Martin Okonjo", "CABIN", "BUSINESS")


def jnb_april_trip(name, title, seniority, purpose, kind, sign_offs, cabin="BUSINESS"):
    return trip(traveller_name=name, traveller_title=title, seniority=seniority, destination="JNB",
                travel_date="2027-04-13", trip_end="2027-04-18", request_submitted="2027-03-08",
                booking_date="2027-03-10", travel_kind="CORPORATE", purpose=purpose, purpose_kind=kind,
                requested_cabin=cabin, sign_offs=[LM, *sign_offs])


scenario(
    "sorrel-beacon", "multi_rule", ["dearer_option"],
    "Business class to Johannesburg on 13 April, please; the CFO has signed it off. I'm meeting the foundation's board "
    "on the 15th.",
    jnb_april_trip("Catherine Hale", "Director of Business Development", "SENIOR_MANAGEMENT_TEAM",
                   "Partnership meeting with a foundation's board", "BUSINESS_DEVELOPMENT", [CFO_BUSINESS]),
    search("LHR", "JNB", "2027-04-13", JNB_APRIL_FLIGHTS, JNB_APRIL_OFFERS),
    expected("BOOK", ["african-business"], ["BUSINESS"], ["PREMIUM_CABIN_APPROVED", "SENIOR_ROLE_ENTITLEMENT"],
             on_file("LINE_MANAGER", "CHIEF_FINANCIAL_OFFICER"), CLASS),
    [CFO, SMT, MANAGER],
    "Corporate travel by a member of the Senior Management Team: lines 258-260 permit a class other than economy "
    "following approval from the COO, CFO and/or CEO, and lines 255-257 need the CFO's approval before a business "
    "booking: both met. The cheapest business seat is SAA at 3,180 pounds.",
    distractors=[AIR_MILES])

scenario(
    "tansy-ledger", "multi_rule", [],
    "Business class to Johannesburg on 13 April if it's allowed without any extra sign-off; otherwise just book "
    "economy, I don't want to chase approvals. I have to be at the opening session on the 15th.",
    jnb_april_trip("Joseph Banda", "Senior Consultant, Governance", "STAFF", "Regional training seminar for staff",
                   "TRAINING_SEMINAR", []),
    search("LHR", "JNB", "2027-04-13", JNB_APRIL_FLIGHTS, JNB_APRIL_OFFERS),
    expected("BOOK", ["british-flex"], ["ECONOMY"], NOT_PERMITTED, on_file("LINE_MANAGER"), FARE),
    [FLEX, CFO, SMT, MANAGER],
    "Corporate travel by a member of staff who is not on the Board or SMT, with no CFO approval: business is not "
    "allowed without a sign-off on any reading of lines 255-262, and the traveller asks for economy in that case. The "
    "cheapest flexible economy fare is British Airways at 840 pounds.",
    distractors=[UPGRADE_SELF])

scenario(
    "wicket-moraine", "multi_rule", ["date_arithmetic", "outside_air_section"],
    "Sorry for the short notice: the ministry moved the validation workshop in Istanbul to 9 February, so I need to fly "
    "on the 8th. Economy, please.",
    trip(traveller_name="Selin Arslan", traveller_title="Consultant, Public Sector Governance", destination="IST",
         travel_date="2027-02-08", trip_end="2027-02-11", request_submitted="2027-02-05", booking_date="2027-02-05",
         funder="World Bank", purpose="Validation workshop for a World Bank-funded civil service reform project",
         sign_offs=[PM, sign("TSSM", "Mark Ellison", "SHORT_NOTICE")]),
    search("LHR", "IST", "2027-02-08", {
        "turkish": {"carrier": "TK", "depart": "07:45"},
        "british": {"carrier": "BA", "depart": "10:20"},
    }, [
        offer("turkish-saver", "turkish", "ECONOMY", 14_800),
        offer("turkish-flex", "turkish", "ECONOMY", 23_900, refundable=True),
        offer("british-saver", "british", "ECONOMY", 16_200),
        offer("british-flex", "british", "ECONOMY", 26_400, refundable=True),
    ]),
    expected("BOOK", ["turkish-flex"], ["ECONOMY"], [*FLEX_CODES, "URGENT_TRAVEL_APPROVED"],
             on_file("PROJECT_MANAGER", "TSSM"), [*FARE, "BOOKING_TRAVEL"]),
    [LEAD, URGENT, FLEX, MANAGER],
    "The request went in on 5 February for travel on the 8th: three days, under the five of line 117. Line 123 sends "
    "urgent travel to the TSSM, whose sign-off for the short notice is on file, so book: the cheapest flexible economy "
    "fare, Turkish at 239 pounds.",
    distractors=[ADVANCE_SOFT])

scenario(
    "ember-cistern", "multi_rule", ["dearer_option"],
    "The World Bank contract covers business class for this assignment, so please book business to Bogota on 16 March. "
    "The ministry workshop is on the 18th.",
    trip(traveller_name="Lucia Fernandez", traveller_title="Principal Consultant, Fiscal Policy", destination="BOG",
         travel_date="2027-03-16", trip_end="2027-03-26", request_submitted="2027-02-12", booking_date="2027-02-15",
         funder="World Bank", contract_cabin="BUSINESS", requested_cabin="BUSINESS",
         purpose="Tax policy workshop with the finance ministry for a World Bank-funded project", sign_offs=[PM]),
    search("LHR", "BOG", "2027-03-16", {
        "british": {"carrier": "BA", "depart": "13:05"},
        "avianca": {"carrier": "AV", "depart": "21:30"},
        "madrid": {"carrier": "IB", "via": ["MAD"], "depart": "07:15", "layovers": [140]},
    }, [
        offer("british-saver", "british", "ECONOMY", 47_000),
        offer("british-flex", "british", "ECONOMY", 63_500, refundable=True),
        offer("british-business", "british", "BUSINESS", 268_000, refundable=True),
        offer("avianca-saver", "avianca", "ECONOMY", 44_500),
        offer("avianca-flex", "avianca", "ECONOMY", 60_200, refundable=True),
        offer("avianca-business", "avianca", "BUSINESS", 241_000, refundable=True),
        offer("madrid-business", "madrid", "BUSINESS", 255_000, refundable=True),
    ]),
    expected("BOOK", ["avianca-business"], ["BUSINESS"], CLIENT_CABIN, on_file("PROJECT_MANAGER"), CLASS),
    [FLEX, MANAGER],
    "Project travel whose client contract expressly permits business (lines 253-255); the CFO's approval (lines "
    "255-257) is only for corporate travel, so none is needed. The cheapest business seat is Avianca at 2,410 pounds.",
    distractors=[aside(255, 257, "For corporate travel, internal approval will be required from the Chief Financial "
                       "Officer", "project travel needs no CFO approval")])

# ===== hidden clause (2) =====

scenario(
    "drover-paddock", "hidden_clause", ["outside_air_section"],
    "I live in Edinburgh but my desk is at the London office. Please book my usual Monday morning flight down on 11 "
    "January, economy.",
    trip(traveller_name="Callum Fraser", traveller_title="Consultant, Data and Evaluation", home_airport="EDI",
         workplace_airport="LHR", origin="EDI", destination="LHR", travel_date="2027-01-11", trip_end="2027-01-15",
         request_submitted="2026-12-28", booking_date="2026-12-29", travel_kind="CORPORATE",
         purpose="A week working at the London office, where he is based", purpose_kind="OFFICE_WORK"),
    search("EDI", "LHR", "2027-01-11", {
        "early": {"carrier": "BA", "depart": "06:45"},
        "mid": {"carrier": "BA", "depart": "08:10"},
    }, [
        offer("early-saver", "early", "ECONOMY", 8_900),
        offer("early-flex", "early", "ECONOMY", 15_400, refundable=True),
        offer("mid-flex", "mid", "ECONOMY", 16_900, refundable=True),
    ]),
    expected("REFUSE", [], ["NONE"], ["COMMUTE_NOT_TRAVEL", "OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"],
             ["NONE"], ["DEFINITIONS", "SCOPE_OF_POLICY"]),
    [TRAVEL_DEF, SCOPE_DEF],
    "The Definitions table and section 1.2: Travel is travelling outside the normal place of work for business, and "
    "does not relate to a commute between the normal place of residence and the normal place of work. Edinburgh home "
    "to the London office, where he is based, is that commute: OPM books no ticket.")

scenario(
    "linnet-gable", "hidden_clause", ["dearer_option", "synonym"],
    "The funder has okayed premium economy for this trip in writing, and their email is on file. Please book premium "
    "economy to Mumbai on 12 January; the state workshop is on the 14th.",
    trip(traveller_name="Kavita Rao", traveller_title="Senior Consultant, Child Protection", destination="BOM",
         travel_date="2027-01-12", trip_end="2027-01-22", request_submitted="2026-12-07", booking_date="2026-12-09",
         funder="UNICEF", requested_cabin="PREMIUM_ECONOMY",
         purpose="State workshop for a UNICEF-funded child protection programme",
         sign_offs=[PM, sign("CLIENT_OR_DONOR", "UNICEF programme officer, by email", "CABIN", "PREMIUM_ECONOMY")]),
    search("LHR", "BOM", "2027-01-12", {
        "india": {"carrier": "AI", "depart": "13:15"},
        "british": {"carrier": "BA", "depart": "20:55"},
    }, [
        offer("india-saver", "india", "ECONOMY", 36_500),
        offer("india-flex", "india", "ECONOMY", 49_800, refundable=True),
        offer("india-premium", "india", "PREMIUM_ECONOMY", 96_000, refundable=True),
        offer("british-saver", "british", "ECONOMY", 39_000),
        offer("british-flex", "british", "ECONOMY", 52_400, refundable=True),
        offer("british-premium", "british", "PREMIUM_ECONOMY", 104_000, refundable=True),
        offer("british-business", "british", "BUSINESS", 245_000, refundable=True),
    ]),
    expected("BOOK", ["india-premium"], ["PREMIUM_ECONOMY"], [*CLIENT_CABIN, "PREMIUM_CABIN_APPROVED"],
             on_file("PROJECT_MANAGER", "CLIENT_OR_DONOR"), CLASS),
    [FLEX, MANAGER],
    "The contract allows only economy, but lines 253-255 also lift the economy rule 'where specific written approval "
    "of the client/donor has been received': the donor's written approval of premium economy is on file (the request "
    "says 'okayed in writing'). The cheapest premium economy seat is Air India at 960 pounds.")

# ===== distractor (2) =====

CAIRO_REQUEST = ("Short notice, I know: the ministry brought the review mission in Cairo forward to 3 December. Please "
                 "book economy out on 2 December.")
CAIRO_FLIGHTS = {
    "egypt": {"carrier": "MS", "depart": "09:40"},
    "british": {"carrier": "BA", "depart": "12:25"},
}
CAIRO_OFFERS = [
    offer("egypt-saver", "egypt", "ECONOMY", 18_900),
    offer("egypt-flex", "egypt", "ECONOMY", 29_600, refundable=True),
    offer("british-saver", "british", "ECONOMY", 21_300),
    offer("british-flex", "british", "ECONOMY", 31_800, refundable=True),
]


def cairo_trip(submitted):
    return trip(traveller_name="Youssef Haddad", traveller_title="Consultant, Social Policy", destination="CAI",
                travel_date="2026-12-02", trip_end="2026-12-09", request_submitted=submitted,
                booking_date="2026-11-30", funder="FCDO",
                purpose="Review mission for an FCDO-funded social protection programme", sign_offs=[PM],
                notes=["The Project Manager approved the trip and its costs on 29 November."])


scenario(
    "cobble-larch", "distractor", ["date_arithmetic", "month_end", "outside_air_section"],
    CAIRO_REQUEST, cairo_trip("2026-11-27"),
    search("LHR", "CAI", "2026-12-02", CAIRO_FLIGHTS, CAIRO_OFFERS),
    expected("BOOK", ["egypt-flex"], ["ECONOMY"], FLEX_CODES, on_file("PROJECT_MANAGER"), [*FARE, "BOOKING_TRAVEL"]),
    [LEAD, FLEX, MANAGER],
    "The request went in on 27 November for travel on 2 December: five days, and line 117 asks for at least five. "
    "Today is only two days before travel, but the rule is about when the request is submitted; 'as far in advance "
    "as possible' (lines 120-121) is a wish. Book the cheapest flexible economy fare, EgyptAir at 296 pounds.",
    twin_of="gossamer-hatch", twin_fact="request submitted on 27 or 28 November",
    distractors=[ADVANCE_SOFT, aside(123, 123, "In cases of urgent travel, please contact the TSSM.",
                                     "the request is in time, so no TSSM sign-off is needed")])

scenario(
    "pallas-weir", "distractor", ["outside_air_section"],
    "Please book economy to Paris on 4 March for our report launch that afternoon.",
    trip(traveller_name="Sophie Laurent", traveller_title="Communications Manager", destination="CDG",
         travel_date="2027-03-04", trip_end="2027-03-05", request_submitted="2027-02-08", booking_date="2027-02-09",
         travel_kind="CORPORATE", purpose="Launch event for OPM's evaluation report in Paris", purpose_kind="MARKETING",
         rail_fare_cents=24_800, rail_arrival="2027-03-04 11:47", sign_offs=[LM]),
    search("LHR", "CDG", "2027-03-04", {
        "france": {"carrier": "AF", "depart": "07:05"},
        "british": {"carrier": "BA", "depart": "08:40"},
    }, [
        offer("british-saver", "british", "ECONOMY", 9_800),
        offer("france-saver", "france", "ECONOMY", 10_900),
        offer("france-flex", "france", "ECONOMY", 19_800, refundable=True),
        offer("british-flex", "british", "ECONOMY", 21_500, refundable=True),
    ]),
    expected("BOOK", ["france-flex"], ["ECONOMY"], [*FLEX_CODES, "RAIL_NOT_CHEAPER"], on_file("LINE_MANAGER"),
             [*FARE, "TRAINS"]),
    [EUROSTAR_AIR, TRAINS, FLEX, MANAGER],
    "UK to France: Eurostar is examined beside flights (lines 250-252) and used where it is cheaper (297-299). The "
    "quoted train is 248 pounds, dearer than every flight, so fly: the cheapest flexible economy fare, Air France at "
    "198 pounds.")

# ===== refusal (2) =====

scenario(
    "marram-kite", "refusal", ["personal_travel", "outside_air_section"],
    "Could you put my flight to Barcelona on 1 April on the OPM account? It's a long weekend away with my partner. "
    "I'll pay it back from my salary.",
    trip(traveller_name="Priya Nair", traveller_title="Consultant, Health Systems", destination="BCN",
         travel_date="2027-04-01", trip_end="2027-04-05", request_submitted="2027-02-22", booking_date="2027-02-23",
         travel_kind="CORPORATE", purpose="A long weekend in Barcelona with her partner", purpose_kind="PERSONAL"),
    search("LHR", "BCN", "2027-04-01", {
        "british": {"carrier": "BA", "depart": "07:30"},
        "madrid": {"carrier": "IB", "via": ["MAD"], "depart": "09:10", "layovers": [80]},
    }, [
        offer("british-saver", "british", "ECONOMY", 7_900),
        offer("british-flex", "british", "ECONOMY", 14_200, refundable=True),
        offer("madrid-saver", "madrid", "ECONOMY", 11_300),
    ]),
    expected("REFUSE", [], ["NONE"], ["PERSONAL_TRAVEL_NOT_COVERED", "OUTSIDE_POLICY_SCOPE"], ["NONE"],
             ["BOOKING_TRAVEL", "PERSONAL_TRAVEL", "FINANCIAL_RESPONSIBILITY"]),
    [PERSONAL_BAN, NO_PERSONAL_COSTS],
    "Lines 114-115: using the OPM business account to book personal travel is strictly prohibited, repaid or not "
    "(the repayment of lines 261-262 is for upgrades on business travel). No ticket.",
    distractors=[UPGRADE_SELF])

scenario(
    "bracken-tarn", "refusal", ["multi_leg", "date_arithmetic", "month_end", "outside_air_section"],
    FENNEL_REQUEST, fennel_trip("Iain Ross", "2026-12-31"),
    search("EDI", "NBO", "2026-12-28", FENNEL_FLIGHTS, FENNEL_OFFERS),
    expected("REFUSE", [], ["NONE"], ["SUBCONTRACT_NOT_COVERING_TRIP", "OUTSIDE_POLICY_SCOPE"],
             ["NONE", "PROJECT_MANAGER"], ["PROJECT_TRAVEL"]),
    [SUBCONTRACT],
    "Line 127: subcontractors must have a valid contract covering the duration of their trip. The contract ends 31 "
    "December and the trip runs to 8 January: no ticket. The Project Manager's approval on file does not change the "
    "contract rule (4(b): accepted beside NONE).",
    twin_of="fennel-cairn", twin_fact="contract ends 31 January 2027 or 31 December 2026")

# ===== flag (3) =====

scenario(
    "gossamer-hatch", "flag", ["date_arithmetic", "month_end", "approval_required", "outside_air_section"],
    CAIRO_REQUEST, cairo_trip("2026-11-28"),
    search("LHR", "CAI", "2026-12-02", CAIRO_FLIGHTS, CAIRO_OFFERS),
    expected("FLAG_FOR_APPROVAL", ["egypt-flex"], ["ECONOMY"], ["APPROVAL_REQUIRED", "ADVANCE_PURCHASE_TOO_LATE"],
             ["TSSM"], ["BOOKING_TRAVEL"]),
    [LEAD, URGENT, FLEX],
    "The request went in on 28 November for travel on 2 December: four days, under the five of line 117. The "
    "traveller calls it short notice; line 123 says urgent travel goes to the TSSM, and no TSSM sign-off is on file. "
    "Hold the flexible EgyptAir fare (296 pounds) for the TSSM: approval required, not 'no compliant offer'.",
    twin_of="cobble-larch", twin_fact="request submitted on 27 or 28 November",
    flag_twins=["cobble-larch", "wicket-moraine"],
    ambiguity="none: the TSSM's sign-off for urgent travel is required and missing; the text is clear")

scenario(
    "umber-spindle", "flag", ["multi_leg", "approval_required"],
    NBO_US_REQUEST, nbo_us_trip("USAID", []),
    search("IAD", "NBO", "2027-03-09", NBO_US_FLIGHTS, NBO_US_OFFERS),
    expected("FLAG_FOR_APPROVAL", ["newark-flex"], ["ECONOMY"], ["APPROVAL_REQUIRED"], ["CLIENT_OR_DONOR"],
             ["PROJECT_TRAVEL"]),
    [USAID_APPROVAL, FLY_AMERICA, FLEX],
    "Lines 128-131: all travel on USAID projects must be approved in writing in advance by the client, through the "
    "prime or directly, and no such approval is on file. Hold the ticket the trip would get: United via Newark at "
    "1,090 pounds (US carriers only, line 272; flexible economy, line 253).",
    twin_of="basalt-orrery", twin_fact="the client's written approval is or is not on file",
    flag_twins=["basalt-orrery", "quartz-heddle"],
    ambiguity="none: the client's written approval is required and missing; the text is clear")

SMT_PHRASE = ("the OPM Board and members of the Senior Management Team may be permitted to Travel in a class other "
              "than economy")

scenario(
    "vesper-lattice", "flag", ["unclear_phrase"],
    "The CFO has signed off business class for me for this trip, so please book business to Johannesburg on 13 April. "
    "I'm presenting to the foundation's board on the 15th.",
    jnb_april_trip("Michael Adeyemi", "Principal Consultant, Partnerships", "STAFF",
                   "Presentation to a foundation's board", "BUSINESS_DEVELOPMENT", [CFO_BUSINESS]),
    search("LHR", "JNB", "2027-04-13", JNB_APRIL_FLIGHTS, JNB_APRIL_OFFERS),
    expected("FLAG_FOR_APPROVAL", ["african-business", "british-flex"], ["BUSINESS", "ECONOMY"],
             ["UNCLEAR_POLICY_TEXT", "APPROVAL_REQUIRED"],
             ["NOT_NAMED", "CHIEF_OPERATING_OFFICER", "CHIEF_FINANCIAL_OFFICER"], CLASS, SMT_PHRASE),
    [CFO, SMT, OWNER],
    "Lines 255-257 require the CFO's approval before a corporate business booking, and it is on file. But lines "
    "258-262 say the Board and SMT 'may be permitted' a class other than economy with COO/CFO/CEO approval, and that "
    "other staff may upgrade by repaying the extra cost. This traveller is not on the Board or SMT. Read one way, the "
    "CFO's approval lets any corporate traveller fly business (book SAA business, 3,180); read the other, business at "
    "OPM's cost is for the Board and SMT only (book flexible economy, BA 840). Hold either; the COO is accountable "
    "for the policy (line 161).",
    flag_twins=["sorrel-beacon", "tansy-ledger"],
    ambiguity={"phrase": SMT_PHRASE, "readings": [
        "the CFO's internal approval (lines 255-257) is enough for any corporate traveller, so business is booked",
        ("a class other than economy at OPM's cost is for the Board and the Senior Management Team; other staff fly "
        "economy unless they repay the upgrade, so flexible economy is booked"),
    ]})


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
