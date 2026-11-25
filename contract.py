"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-opml-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    FLEXIBLE_ECONOMY_POLICY = "FLEXIBLE_ECONOMY_POLICY"
    DIRECT_OPTION_WITHIN_BUDGET = "DIRECT_OPTION_WITHIN_BUDGET"
    DIRECT_OPTION_OVER_BUDGET = "DIRECT_OPTION_OVER_BUDGET"
    CLIENT_PERMITS_PREMIUM_CABIN = "CLIENT_PERMITS_PREMIUM_CABIN"
    PREMIUM_CABIN_NOT_PERMITTED = "PREMIUM_CABIN_NOT_PERMITTED"
    PREMIUM_CABIN_APPROVED = "PREMIUM_CABIN_APPROVED"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    PIA_INTERNATIONAL_NOT_PERMITTED = "PIA_INTERNATIONAL_NOT_PERMITTED"
    CARRIER_NOT_APPROVED = "CARRIER_NOT_APPROVED"
    URGENT_TRAVEL_APPROVED = "URGENT_TRAVEL_APPROVED"
    COMMUTE_NOT_TRAVEL = "COMMUTE_NOT_TRAVEL"
    SUBCONTRACT_NOT_COVERING_TRIP = "SUBCONTRACT_NOT_COVERING_TRIP"
    RAIL_NOT_CHEAPER = "RAIL_NOT_CHEAPER"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    WEEKEND_TRAVEL_HOME = "WEEKEND_TRAVEL_HOME"
    WEEKEND_TRIP_NOT_EARNED = "WEEKEND_TRIP_NOT_EARNED"
    NEXT_OF_KIN_TRAVEL = "NEXT_OF_KIN_TRAVEL"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    EXTENDED_TRAVEL_SAVINGS = "EXTENDED_TRAVEL_SAVINGS"
    DENIED_BOARDING_NOT_ALLOWED = "DENIED_BOARDING_NOT_ALLOWED"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    CANDIDATE_TRIP_NOT_COVERED = "CANDIDATE_TRIP_NOT_COVERED"
    SAME_CLASS_AS_CUSTOMER = "SAME_CLASS_AS_CUSTOMER"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: OPM Travel Policy (Oxford Policy Management, March 2024, version 4.0).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    BASALT_ORRERY = "basalt-orrery"
    BRACKEN_TARN = "bracken-tarn"
    COBBLE_LARCH = "cobble-larch"
    COPPER_LAGOON = "copper-lagoon"
    DROVER_PADDOCK = "drover-paddock"
    EMBER_CISTERN = "ember-cistern"
    FENNEL_CAIRN = "fennel-cairn"
    GARNET_THISTLE = "garnet-thistle"
    GOSSAMER_HATCH = "gossamer-hatch"
    HERON_QUILL = "heron-quill"
    LINNET_GABLE = "linnet-gable"
    LUMEN_THICKET = "lumen-thicket"
    MARRAM_KITE = "marram-kite"
    MISTRAL_QUAY = "mistral-quay"
    ORCHARD_TIDE = "orchard-tide"
    PALLAS_WEIR = "pallas-weir"
    PEWTER_RILL = "pewter-rill"
    QUARTZ_HEDDLE = "quartz-heddle"
    SALTMARSH_VIGIL = "saltmarsh-vigil"
    SORREL_BEACON = "sorrel-beacon"
    TANSY_LEDGER = "tansy-ledger"
    UMBER_SPINDLE = "umber-spindle"
    VESPER_LATTICE = "vesper-lattice"
    WICKET_MORAINE = "wicket-moraine"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    PROJECT_MANAGER = "PROJECT_MANAGER"
    LINE_MANAGER = "LINE_MANAGER"
    PRACTICE_LEAD = "PRACTICE_LEAD"
    ACCOUNTABLE_MANAGER = "ACCOUNTABLE_MANAGER"
    OFFICE_ADMINISTRATOR = "OFFICE_ADMINISTRATOR"
    TSSM = "TSSM"
    CLIENT_OR_DONOR = "CLIENT_OR_DONOR"
    CHIEF_FINANCIAL_OFFICER = "CHIEF_FINANCIAL_OFFICER"
    CHIEF_OPERATING_OFFICER = "CHIEF_OPERATING_OFFICER"
    CHIEF_EXECUTIVE = "CHIEF_EXECUTIVE"
    HUMAN_RESOURCES = "HUMAN_RESOURCES"
    DIRECTOR = "DIRECTOR"
    VICE_PRESIDENT = "VICE_PRESIDENT"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    TRAVEL_DEPARTMENT = "TRAVEL_DEPARTMENT"


class Clause(Enum):
    """The handbook's sections, by heading."""

    DEFINITIONS = "DEFINITIONS"
    DOCUMENT_INFORMATION = "DOCUMENT_INFORMATION"
    PURPOSE = "PURPOSE"
    SCOPE_OF_POLICY = "SCOPE_OF_POLICY"
    PRINCIPLES = "PRINCIPLES"
    BOOKING_TRAVEL = "BOOKING_TRAVEL"
    PROJECT_TRAVEL = "PROJECT_TRAVEL"
    CORPORATE_TRAVEL = "CORPORATE_TRAVEL"
    PERSONAL_TRAVEL = "PERSONAL_TRAVEL"
    FINANCIAL_RESPONSIBILITY = "FINANCIAL_RESPONSIBILITY"
    DUTY_OF_CARE = "DUTY_OF_CARE"
    SERVICE_PROVIDERS = "SERVICE_PROVIDERS"
    RESPONSIBILITIES = "RESPONSIBILITIES"
    GENERAL_PROVISIONS = "GENERAL_PROVISIONS"
    AIR_CLASS_AND_RATES = "AIR_CLASS_AND_RATES"
    FLIGHT_CARRIERS = "FLIGHT_CARRIERS"
    CAR_TRAVEL = "CAR_TRAVEL"
    TRAINS = "TRAINS"
    HOTEL_BOOKINGS = "HOTEL_BOOKINGS"
    PER_DIEM = "PER_DIEM"
    INSURANCE = "INSURANCE"
    EMERGENCY = "EMERGENCY"
    FITNESS_AND_VACCINATIONS = "FITNESS_AND_VACCINATIONS"
    SECURITY = "SECURITY"
    VISAS = "VISAS"
    BOARDING_PASSES = "BOARDING_PASSES"
    FURTHER_INFORMATION = "FURTHER_INFORMATION"


class Passenger(Enum):
    STAFF = "STAFF"
    SUBCONTRACTOR = "SUBCONTRACTOR"


class Seniority(Enum):
    STAFF = "STAFF"
    SENIOR_MANAGEMENT_TEAM = "SENIOR_MANAGEMENT_TEAM"
    BOARD = "BOARD"


class TravelKind(Enum):
    PROJECT = "PROJECT"
    CORPORATE = "CORPORATE"


class Purpose(Enum):
    PROJECT_WORK = "PROJECT_WORK"
    BUSINESS_DEVELOPMENT = "BUSINESS_DEVELOPMENT"
    MARKETING = "MARKETING"
    TRAINING_SEMINAR = "TRAINING_SEMINAR"
    INTERNAL_MEETING = "INTERNAL_MEETING"
    OFFICE_WORK = "OFFICE_WORK"
    PERSONAL = "PERSONAL"


class SignOffSubject(Enum):
    TRIP = "TRIP"
    CABIN = "CABIN"
    SHORT_NOTICE = "SHORT_NOTICE"


@dataclass
class SignOff(Output):
    role: Annotated[Approver, "The signer's role"]
    name: Annotated[str, "Their name"]
    subject: Annotated[
        SignOffSubject,
        "What they signed off: the trip and its costs, a cabin better than economy, or a request made close "
        "to the day of travel",
    ]
    cabin: Annotated[Cabin, "For a cabin sign-off, the best cabin it allows; NONE for any other sign-off"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title"]
    passenger: Annotated[Passenger, "What the person flying is to the organisation: a member of staff or a subcontractor"]
    seniority: Annotated[Seniority, "Whether the traveller is a Board member, a Senior Management Team (SMT) member, or neither"]
    home_airport: Annotated[Airport, "The airport nearest the traveller's home"]
    workplace_airport: Annotated[Airport, "The airport nearest the office where the traveller normally works"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where it goes"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    trip_end: Annotated[
        str, "The last day of the trip away, YYYY-MM-DD; the flight back is booked separately and is not part of this decision"
    ]
    request_submitted: Annotated[str, "The day the traveller's request went in on the approval portal, YYYY-MM-DD"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    travel_kind: Annotated[TravelKind, "PROJECT for work on a client's or donor's project; CORPORATE for the organisation's own business"]
    funder: Annotated[str, "The client or donor paying for the project, as its contract names them; empty for corporate trips"]
    contract_cabin: Annotated[
        Cabin,
        "The best cabin that the project's client contract itself allows for flights; ECONOMY when it allows nothing "
        "better; NONE for corporate trips, which have no client contract",
    ]
    contract_end: Annotated[str, "For a subcontractor, the last day their contract with the organisation runs, YYYY-MM-DD; empty for staff"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    purpose_kind: Annotated[Purpose, "The kind of trip"]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    wants_nonstop: Annotated[bool, "Whether the traveller asks for a flight with no connection"]
    fare_budget_cents: Annotated[int, "The most the trip's budget sets aside for this one-way fare, in cents (pence); zero when no figure is set"]
    rail_fare_cents: Annotated[int, "The fare, in cents, that the booking agency quoted for the same journey by train; zero when none was quoted"]
    rail_arrival: Annotated[str, "When that train arrives, YYYY-MM-DD HH:MM local; empty when none was quoted"]
    sign_offs: Annotated[list[SignOff], "Sign-offs already on file for this trip, each given before today"]
    notes: Annotated[list[str], "Other facts on file about the trip, in plain words; empty when none"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
