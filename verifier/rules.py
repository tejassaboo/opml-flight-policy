"""The answer key's rules for the OPM Travel Policy (Oxford Policy Management, March 2024, version 4.0), as
exact integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it imports only modules a
verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. This handbook has no flight-duration threshold at all: its cabin rule turns on the client
contract, the client's or donor's written approval and, for corporate travel, the CFO and the Board or Senior
Management Team (lines 253-262), never on hours in the air. DURATION_RULES is empty and ``over`` knows no rule.

The fare. Line 253: "OPM's policy is to book flexible economy class flights." In this world the flexible fare
is the one whose ``refundable`` flag is true (refunded or changed without a fee); line 248 adds "the most
cost-effective, direct route available", so the economy answer is the cheapest flexible economy fare that can
be bought. A premium-cabin answer is the cheapest seat of that cabin, and every such scenario makes that seat a
flexible one, so the answer does not depend on whether "flexible" reaches beyond economy.
"""

from contract import (
    Approver,
    Cabin,
    Clause,
    Decision,
    Passenger,
    Purpose,
    ReasonCode,
    Seniority,
    SignOffSubject,
    TravelKind,
)

from .world import days_between

HANDBOOK = "OPM Travel Policy, Oxford Policy Management, March 2024 (version 4.0)"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.DEFINITIONS: "Definitions",
    Clause.DOCUMENT_INFORMATION: "1. Document Information",
    Clause.PURPOSE: "1.1 Purpose",
    Clause.SCOPE_OF_POLICY: "1.2 Scope of Policy",
    Clause.PRINCIPLES: "1.3 Principles",
    Clause.BOOKING_TRAVEL: "2 Booking Travel",
    Clause.PROJECT_TRAVEL: "2.1 Project Travel",
    Clause.CORPORATE_TRAVEL: "2.2 Corporate Travel",
    Clause.PERSONAL_TRAVEL: "2.3 Personal Travel",
    Clause.FINANCIAL_RESPONSIBILITY: "2.3.1 Financial Responsibility",
    Clause.DUTY_OF_CARE: "2.3.2 Duty of Care and Insurance Cover",
    Clause.SERVICE_PROVIDERS: "2.4 Travel Service Providers",
    Clause.RESPONSIBILITIES: "2.5 Responsibilities",
    Clause.GENERAL_PROVISIONS: "3 General Provisions",
    Clause.AIR_CLASS_AND_RATES: "3.1 Class of Air Travel / Rate Rules",
    Clause.FLIGHT_CARRIERS: "3.2 Flight Carriers",
    Clause.CAR_TRAVEL: "3.3 Car Travel",
    Clause.TRAINS: "3.4 Trains",
    Clause.HOTEL_BOOKINGS: "3.5 Hotel Bookings",
    Clause.PER_DIEM: "3.6 Per Diem Rates",
    Clause.INSURANCE: "3.7 Travel insurance",
    Clause.EMERGENCY: "3.8 In Case of Emergency",
    Clause.FITNESS_AND_VACCINATIONS: "3.9 Fitness to Travel / Vaccinations",
    Clause.SECURITY: "3.10 Security",
    Clause.VISAS: "3.11 Visas",
    Clause.BOARDING_PASSES: "3.12 Retention of Boarding Passes / Receipts",
    Clause.FURTHER_INFORMATION: "5.0 Further Information",
}

# No duration threshold in this handbook (see the module docstring).
DURATION_RULES = ()

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Line 117: "Travel requests must be submitted at least five days prior to Travel" (inclusive), counted in
# calendar days from the day the request went in to the day of travel.
LEAD_DAYS = 5
# Line 272: "For projects funded by USAID, US Flag Carrier Rules apply." The airlines of the shared world that
# are US carriers, by the name search_flights gives.
US_CARRIERS = ("American Airlines", "Delta Air Lines", "United Airlines", "Alaska Airlines", "JetBlue",
               "Southwest Airlines")
USAID = "USAID"
# Line 250 and line 297: Eurostar between the UK and the EU.
UK = ("GB",)
EU = ("FR", "NL", "DE", "ES", "IT", "DK", "IE")
RANK = {Cabin.ECONOMY: 1, Cabin.PREMIUM_ECONOMY: 2, Cabin.BUSINESS: 3, Cabin.FIRST: 4}

SMT_PHRASE = ("the OPM Board and members of the Senior Management Team may be permitted to Travel in a class "
              "other than economy")

FARE = [Clause.AIR_CLASS_AND_RATES, Clause.GENERAL_PROVISIONS, Clause.PRINCIPLES]
CLASS = [Clause.AIR_CLASS_AND_RATES, Clause.GENERAL_PROVISIONS]
# A hold over unclear words: the handbook names no one to settle them; line 161 puts overall accountability for
# the policy with the COO (the policy owner, line 407), and the CFO gives the internal approval of line 256.
UNCLEAR_ROLES = [Approver.NOT_NAMED, Approver.CHIEF_OPERATING_OFFICER, Approver.CHIEF_FINANCIAL_OFFICER]


def over(rule, offer):
    """The duration hook: this handbook has no duration rule, so every name is unknown."""
    raise ValueError(f"unknown duration rule {rule!r}: this handbook has none")


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def signed(trip, subject, roles=None):
    return [record for record in trip.sign_offs if record.subject == subject and (roles is None or record.role in roles)]


def on_file(trip):
    return [record.role for record in trip.sign_offs]


def refuse(trip, reasons, clauses, why):
    # SYNC_NOTES 4(b): a sign-off on file that a refusal does not use is accepted beside NONE.
    return answer(Decision.REFUSE, [], reasons, [Approver.NONE, *on_file(trip)], clauses, why)


def commute(trip):
    """Lines 65-67 and 89-92: Travel "does not relate to a commute, or travel between a person's normal place of
    residence and normal place of work"."""
    home, work = trip.home_airport.code, trip.workplace_airport.code
    return home != work and {trip.origin.code, trip.destination.code} == {home, work}


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers on its route and date: the decision, and every accepted
    offer id, cabin, reason, approver and section. ``hidden`` (answer_key_inputs) is unused by this handbook."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if any(offer.return_segments for offer in offers):
        raise ValueError("round-trip fares are not modelled: every case buys the one-way fare out")
    if trip.purpose_kind == Purpose.PERSONAL:
        return refuse(trip, [ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      [Clause.BOOKING_TRAVEL, Clause.PERSONAL_TRAVEL, Clause.FINANCIAL_RESPONSIBILITY],
                      "Lines 114-115: the use of the OPM business account and/or Project funds to book personal travel "
                      "is strictly prohibited (and lines 142-144: no personal-travel cost is reimbursed). No ticket.")
    if commute(trip):
        return refuse(trip, [ReasonCode.COMMUTE_NOT_TRAVEL, ReasonCode.OUTSIDE_POLICY_SCOPE,
                             ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                      [Clause.DEFINITIONS, Clause.SCOPE_OF_POLICY],
                      "Lines 65-67 and 89-92: Travel is travelling outside the normal place of work for business; it does "
                      "not relate to travel between a person's normal place of residence and normal place of work. "
                      "This flight is the traveller's commute from home to their usual office: not Travel, no ticket.")
    if trip.passenger == Passenger.SUBCONTRACTOR:
        if not trip.contract_end:
            raise ValueError("a subcontractor with no contract end on file is not modelled")
        if days_between(trip.contract_end, trip.trip_end) > 0:
            return refuse(trip, [ReasonCode.SUBCONTRACT_NOT_COVERING_TRIP, ReasonCode.OUTSIDE_POLICY_SCOPE],
                          [Clause.PROJECT_TRAVEL],
                          f"Line 127: subcontractors must have a valid contract covering the duration of their trip. The "
                          f"contract ends {trip.contract_end} and the trip runs to {trip.trip_end}: no ticket.")
    elif trip.contract_end:
        raise ValueError("a contract end on file for a member of staff is not modelled")
    return business_trip(trip, offers)


def business_trip(trip, offers):
    manager = Approver.PROJECT_MANAGER if trip.travel_kind == TravelKind.PROJECT else Approver.LINE_MANAGER
    if trip.travel_kind == TravelKind.PROJECT:
        if not trip.funder or trip.contract_cabin == Cabin.NONE:
            raise ValueError("project travel names its funder and its contract's cabin")
    elif trip.funder or trip.contract_cabin != Cabin.NONE:
        raise ValueError("corporate travel has no funder and no client contract")
    if len(signed(trip, SignOffSubject.TRIP, [manager])) != 1:
        raise ValueError("every business trip carries the relevant manager's approval (lines 122-123): no scenario lacks it")
    usaid = trip.funder == USAID
    seated = [offer for offer in offers if offer.seats_available]
    pool = [offer for offer in seated if offer.carrier in US_CARRIERS] if usaid else seated
    flexible = [offer for offer in pool if offer.cabin == Cabin.ECONOMY and offer.refundable]
    if not flexible:
        raise ValueError("no flexible economy fare can be bought")
    decision, chosen, reasons, relied, clauses, notes, phrase = choose(trip, pool, flexible)
    if usaid:
        everyone = cheapest([offer for offer in seated if offer.cabin == Cabin.ECONOMY and offer.refundable])
        if any(offer.carrier in US_CARRIERS for offer in everyone) or decision != Decision.BOOK:
            raise ValueError("a USAID case whose cheapest flexible fare is already a US carrier's is not modelled")
        reasons += [ReasonCode.FLY_AMERICA_US_CARRIER_REQUIRED, ReasonCode.NATIONAL_CARRIER_REQUIRED,
                    ReasonCode.PREFERRED_CARRIER_REQUIRED]
        clauses += [Clause.FLIGHT_CARRIERS]
        notes.append("line 272: the project is funded by USAID, so US Flag Carrier Rules apply: a US carrier only")
        if not signed(trip, SignOffSubject.TRIP, [Approver.CLIENT_OR_DONOR]):
            return answer(Decision.FLAG_FOR_APPROVAL, chosen, [ReasonCode.APPROVAL_REQUIRED], [Approver.CLIENT_OR_DONOR],
                          [Clause.PROJECT_TRAVEL],
                          "Lines 128-131: all travel undertaken on USAID projects must be approved in writing in advance "
                          "by the client, and no such approval is on file: hold the ticket the trip would otherwise get "
                          f"({'; '.join(notes)}).")
        relied.append(Approver.CLIENT_OR_DONOR)
        clauses.append(Clause.PROJECT_TRAVEL)
    days = days_between(trip.request_submitted, trip.travel_date)
    if days < LEAD_DAYS:
        urgent = signed(trip, SignOffSubject.SHORT_NOTICE, [Approver.TSSM])
        if decision != Decision.BOOK:
            raise ValueError("a late request on a case that is not otherwise a booking is not modelled")
        if not urgent:
            return answer(Decision.FLAG_FOR_APPROVAL, chosen,
                          [ReasonCode.APPROVAL_REQUIRED, ReasonCode.ADVANCE_PURCHASE_TOO_LATE], [Approver.TSSM],
                          [Clause.BOOKING_TRAVEL],
                          f"Line 117: travel requests must be submitted at least five days prior to travel; this one went "
                          f"in {days} days before. Line 123: in cases of urgent travel, contact the TSSM, and no TSSM "
                          "sign-off is on file: hold the ticket the trip would otherwise get.")
        reasons.append(ReasonCode.URGENT_TRAVEL_APPROVED)
        relied.append(Approver.TSSM)
        clauses.append(Clause.BOOKING_TRAVEL)
        notes.append(f"line 117: the request went in {days} days before travel, under five, and the TSSM approved the "
                     "urgent travel (line 123)")
    elif days == LEAD_DAYS:
        clauses.append(Clause.BOOKING_TRAVEL)
        notes.append("line 117: the request went in exactly five days before travel, which is at least five (the day "
                     "of booking does not count)")
    elif signed(trip, SignOffSubject.SHORT_NOTICE):
        raise ValueError("a short-notice sign-off on a request made in time is not modelled")
    if trip.rail_fare_cents:
        if decision != Decision.BOOK or not (trip.origin.country in UK and trip.destination.country in EU):
            raise ValueError("a rail quote outside a UK-EU booking is not modelled")
        if any(trip.rail_fare_cents < offer.fare_cents for offer in chosen):
            raise ValueError("a train cheaper than the flight is not modelled")
        reasons.append(ReasonCode.RAIL_NOT_CHEAPER)
        clauses.append(Clause.TRAINS)
        notes.append(f"lines 250-252 and 297-299: Eurostar is used where it is cheaper; the quoted train costs "
                     f"{trip.rail_fare_cents} pence, more than the flight, so the flight")
    if decision == Decision.FLAG_FOR_APPROVAL:
        approvers = list(UNCLEAR_ROLES)
    else:
        # SYNC_NOTES 4': a BOOK whose needed sign-offs are on file accepts those roles and NONE; 4(b): a sign-off
        # on file the booking does not use is accepted too.
        approvers = [Approver.NONE, manager, *relied, *on_file(trip)]
    notes.append(f"lines 122-123: the {manager.value} approved the travel and its costs before booking")
    return answer(decision, chosen, reasons, approvers, clauses, "; ".join(notes) + ".", phrase)


def choose(trip, pool, flexible):
    """(decision, offers, reasons, roles relied on beyond the manager, clauses, notes, unclear phrase)."""
    if trip.requested_cabin == Cabin.ECONOMY:
        decision, chosen, reasons, clauses, notes = economy(trip, flexible)
        if trip.contract_cabin in (Cabin.PREMIUM_ECONOMY, Cabin.BUSINESS):
            notes.append(f"the client contract allows {trip.contract_cabin.value}, but the traveller asks for economy")
        return decision, chosen, reasons, [], clauses, notes, ""
    if trip.requested_cabin not in (Cabin.PREMIUM_ECONOMY, Cabin.BUSINESS) or trip.wants_nonstop:
        raise ValueError(f"a {trip.requested_cabin.value} request, or one with a routing wish, is not modelled")
    if trip.travel_kind == TravelKind.PROJECT:
        return project_cabin(trip, pool, flexible)
    return corporate_cabin(trip, pool, flexible)


def economy(trip, flexible):
    """Lines 248-253: the cheapest flexible economy fare; a nonstop the traveller asks for when it is within the
    budget set for the fare ("this option may be selected over a cheaper less direct route")."""
    lowest = cheapest(flexible)
    direct = cheapest([offer for offer in flexible if not offer.layover_minutes])
    if not trip.wants_nonstop:
        if trip.fare_budget_cents:
            raise ValueError("a fare budget with no nonstop wish is not modelled")
        if any(offer.layover_minutes for offer in lowest) and direct:
            raise ValueError("a cheaper connection beside a flexible nonstop, with no stated wish, is not modelled")
        return (Decision.BOOK, lowest, [ReasonCode.LOWEST_FARE, ReasonCode.FLEXIBLE_ECONOMY_POLICY], list(FARE),
                [("line 253: the policy is to book flexible economy; line 248: the most cost-effective route: the "
                 "cheapest flexible economy fare")])
    if not direct or not trip.fare_budget_cents or not all(offer.layover_minutes for offer in lowest):
        raise ValueError("a nonstop wish needs a flexible nonstop, a fare budget and a cheaper connection")
    fare = direct[0].fare_cents
    if fare <= trip.fare_budget_cents:
        return (Decision.BOOK, direct, [ReasonCode.DIRECT_OPTION_WITHIN_BUDGET, ReasonCode.ALTERNATE_ROUTE_WITHIN_MARGIN],
                list(FARE),
                [(f"lines 249-250: the flexible nonstop at {fare} pence is within the {trip.fare_budget_cents} pence "
                 "budget, so it may be selected over the cheaper connection, as the traveller asks")])
    # The nonstop is declined on the handbook's own budget test, part of its cost-effective route rule: LOWEST_FARE
    # is accepted beside the specific codes (lead's decision, the same in every plugin).
    return (Decision.BOOK, lowest, [ReasonCode.DIRECT_OPTION_OVER_BUDGET, ReasonCode.ALTERNATE_ROUTE_TOO_EXPENSIVE,
                                    ReasonCode.LOWEST_FARE], list(FARE),
            [(f"lines 248-250: the flexible nonstop at {fare} pence is over the {trip.fare_budget_cents} pence budget, "
             "so the most cost-effective route: the cheapest flexible economy fare, a connection")])


def premium_offer(pool, cabin):
    best = cheapest([offer for offer in pool if offer.cabin == cabin])
    if not best or not all(offer.refundable for offer in best):
        raise ValueError(f"the cheapest {cabin.value} seat must be a flexible one (module docstring)")
    return best


def project_cabin(trip, pool, flexible):
    """Lines 253-255: flexible economy unless expressly permitted by a client contract, or where specific written
    approval of the client/donor has been received. The CFO's approval (lines 255-257) is for corporate travel."""
    wanted = trip.requested_cabin
    by_contract = RANK.get(trip.contract_cabin, 0) >= RANK[wanted]
    donor = [record for record in signed(trip, SignOffSubject.CABIN, [Approver.CLIENT_OR_DONOR])
             if RANK.get(record.cabin, 0) >= RANK[wanted]]
    if by_contract and donor:
        raise ValueError("a donor approval for a cabin the contract already allows is not modelled")
    if by_contract or donor:
        reasons = [ReasonCode.CLIENT_PERMITS_PREMIUM_CABIN, ReasonCode.CLIENT_REIMBURSABLE]
        relied, notes = [], []
        if by_contract:
            notes.append(f"lines 253-255: the client contract expressly permits {trip.contract_cabin.value}")
        else:
            reasons.append(ReasonCode.PREMIUM_CABIN_APPROVED)
            relied.append(Approver.CLIENT_OR_DONOR)
            notes.append(f"lines 253-255: the contract allows only economy, but the client/donor's specific written "
                         f"approval of {donor[0].cabin.value} is on file")
        notes.append(f"project travel needs no CFO approval (line 255 is for corporate travel): the cheapest "
                     f"{wanted.value} seat")
        return Decision.BOOK, premium_offer(pool, wanted), reasons, relied, list(CLASS), notes, ""
    decision, chosen, _, clauses, notes = economy(trip, flexible)
    notes.append(f"lines 253-255: neither the client contract nor a written client/donor approval allows "
                 f"{wanted.value}, so quotes stay in flexible economy")
    return (decision, chosen, [ReasonCode.PREMIUM_CABIN_NOT_PERMITTED, ReasonCode.UPGRADE_NOT_ELIGIBLE], [], clauses,
            notes, "")


def corporate_cabin(trip, pool, flexible):
    """Lines 255-262: for corporate travel the CFO's internal approval is required before a business or premium
    economy booking is finalised; the Board and the Senior Management Team may be permitted a class other than
    economy following approval from the COO, CFO and/or CEO; other staff may upgrade at their own cost."""
    wanted = trip.requested_cabin
    cfo = [record for record in signed(trip, SignOffSubject.CABIN, [Approver.CHIEF_FINANCIAL_OFFICER])
           if RANK.get(record.cabin, 0) >= RANK[wanted]]
    if signed(trip, SignOffSubject.CABIN) and not cfo:
        raise ValueError("a corporate cabin sign-off other than the CFO's is not modelled")
    if trip.seniority in (Seniority.SENIOR_MANAGEMENT_TEAM, Seniority.BOARD):
        if not cfo:
            raise ValueError("a Board or SMT member without the CFO's cabin approval is not modelled")
        return (Decision.BOOK, premium_offer(pool, wanted),
                [ReasonCode.PREMIUM_CABIN_APPROVED, ReasonCode.SENIOR_ROLE_ENTITLEMENT], [Approver.CHIEF_FINANCIAL_OFFICER],
                list(CLASS),
                [(f"lines 255-260: a member of the {trip.seniority.value} on corporate travel, with the CFO's approval of "
                 f"{wanted.value} on file: the cheapest {wanted.value} seat")], "")
    decision, chosen, _, clauses, notes = economy(trip, flexible)
    if cfo:
        held = premium_offer(pool, wanted) + chosen
        return (Decision.FLAG_FOR_APPROVAL, held, [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED], [],
                list(CLASS),
                [(f"lines 255-257 require the CFO's approval for a corporate {wanted.value} booking, and it is on file; "
                 "but lines 258-262 permit a class other than economy to the Board and the Senior Management Team and "
                 "let other staff upgrade only by repaying the extra cost. Whether the CFO's approval alone lets a "
                 "member of staff fly above economy at OPM's cost is open: hold either fare")], SMT_PHRASE)
    notes.append(f"lines 255-262: corporate {wanted.value} needs the CFO's approval and is for the Board and the Senior "
                 "Management Team; no approval is on file, so flexible economy")
    return (decision, chosen, [ReasonCode.PREMIUM_CABIN_NOT_PERMITTED, ReasonCode.UPGRADE_NOT_ELIGIBLE], [], clauses,
            notes, "")
