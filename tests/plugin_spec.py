"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "opml" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 24-scenario row).
MIX = {"easy": 5, "boundary_twin": 6, "multi_rule": 4, "hidden_clause": 2, "distractor": 2, "refusal": 2, "flag": 3}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. It has no rule on several travellers
# on one flight and no overnight-stop rule, so neither is required.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1,
    "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "personal", "partner", "holiday", "leave", "commute", "home", "residence", "desk", "usaid", "america", "american",
    "flag", "carrier", "carriers", "faa", "pia", "pakistan", "flexible", "flex", "refundable", "budget", "direct",
    "nonstop", "route", "connection", "urgent", "notice", "late", "lead", "client", "donor", "contract",
    "subcontractor", "cfo", "coo", "ceo", "smt", "board", "senior", "executive", "eurostar", "rail", "train",
    "premium", "manager", "project", "corporate", "portal", "tssm", "risk", "visa", "insurance", "funder", "prime",
    "written", "fly", "economy", "class", "upgrade", "miles", "security", "staff",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.Passenger, contract.Seniority, contract.TravelKind, contract.Purpose,
                     contract.SignOffSubject]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section and approver NONE). Every booking here is a
# flexible fare or a premium seat dearer than the cheapest listed seat, so the always-cheapest agent passes none;
# the always-flag agent passes only the unclear hold (vesper-lattice), whose approver set holds NOT_NAMED.
MAX_PASS_ALWAYS_FLAG = 1
MAX_PASS_ALWAYS_LOWEST = 0

# Hand-built duration cases: none, since this handbook has no duration threshold (rules.DURATION_RULES is empty).
DURATION_CASES = []
