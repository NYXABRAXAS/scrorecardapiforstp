from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApplicationDetails(BaseModel):
    leadId: str
    customerName: str | None = None
    mobile: str | None = None
    employmentType: str | None = None
    monthlyIncome: Decimal | None = None
    existingEMI: Decimal | None = None
    foir: Decimal | None = None
    loanAmount: Decimal | None = None
    assetCost: Decimal | None = None
    ltv: Decimal | None = None
    tenure: int | None = None
    dealerId: str | None = None
    state: str | None = None
    city: str | None = None
    pincode: str | None = None
    negativeArea: bool | None = None
    fraudFlag: bool | None = False
    blacklistMatch: bool | None = False
    fakeKyc: bool | None = False
    panMismatch: bool | None = False
    faceMatchScore: Decimal | None = None
    panVerified: bool | None = None
    aadhaarVerified: bool | None = None
    bankingSurrogate: bool | None = None
    coApplicant: bool | None = None


class BureauData(BaseModel):
    cibilScore: int | None = None
    creditVintageMonths: int | None = None
    activeAccounts: int | None = None
    closedAccounts: int | None = None
    overdueAmount: Decimal | None = None
    writtenOffAccounts: int | None = None
    settledAccounts: int | None = None
    suitFiledAccounts: int | None = 0
    active90PlusDpd: bool | None = False
    maxDPD: int | None = None
    dpd30Count: int | None = None
    dpd60Count: int | None = None
    dpd90Count: int | None = None
    creditEnquiries6M: int | None = None
    creditEnquiries12M: int | None = None
    activeUnsecuredLoans: int | None = None
    activeSecuredLoans: int | None = None
    jointAccounts: int | None = None
    creditUtilization: Decimal | None = None
    bureauRisk: str | None = None


class ScorecardRequest(BaseModel):
    application: ApplicationDetails
    bureau: BureauData
    tenantId: str = "default"
    productType: str = "TWO_WHEELER_LOAN"
    forceRecalculate: bool = False


class ScorecardResponse(BaseModel):
    leadId: str
    finalScore: Decimal
    decision: str
    underwritingRequired: bool
    rejectFlag: bool
    journeyAction: str
    bureauRisk: str
    reasonCodes: list[str]
    triggeredRules: list[str]
    scoreBreakup: dict[str, Decimal]

    model_config = ConfigDict(from_attributes=True)


class SimulationResponse(ScorecardResponse):
    persisted: bool = False


class StoredScorecardResponse(ScorecardResponse):
    tenantId: str
    productType: str
    createdAt: str


class HealthResponse(BaseModel):
    status: str
    database: str
    redis: str
    details: dict[str, Any] = Field(default_factory=dict)

