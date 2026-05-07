from enum import StrEnum


class RuleType(StrEnum):
    SCORE = "SCORE"
    HARD_REJECT = "HARD_REJECT"
    NON_STP = "NON_STP"
    STP_ELIGIBILITY = "STP_ELIGIBILITY"


class DecisionAction(StrEnum):
    STP = "STP"
    CONDITIONAL_STP = "CONDITIONAL_STP"
    NON_STP = "NON_STP"
    UW = "UW"
    REJECT = "REJECT"
    SCORE = "SCORE"


class ScorecardDecision(StrEnum):
    STP = "STP"
    CONDITIONAL_STP = "CONDITIONAL_STP"
    NON_STP = "NON_STP"
    REJECT = "REJECT"


class JourneyAction(StrEnum):
    SKIP_UNDERWRITING = "SKIP_UNDERWRITING"
    SEND_TO_UNDERWRITING = "SEND_TO_UNDERWRITING"
    REJECT_APPLICATION = "REJECT_APPLICATION"


class BureauRisk(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

