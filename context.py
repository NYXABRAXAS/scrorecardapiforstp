from typing import Any

from pydantic import BaseModel

from app.schemas.scorecard import ScorecardRequest


ALIASES = {
    "leadId": "leadId",
    "dealerId": "dealerId",
    "enquiries6M": "creditEnquiries6M",
    "creditEnquiries6M": "creditEnquiries6M",
    "enquiries12M": "creditEnquiries12M",
    "creditEnquiries12M": "creditEnquiries12M",
    "fraudFlag": "fraudFlag",
    "writtenOffAccounts": "writtenOffAccounts",
    "settledAccounts": "settledAccounts",
}


def _dump(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(by_alias=False)


def build_evaluation_context(request: ScorecardRequest) -> dict[str, Any]:
    context = {}
    context.update(_dump(request.application))
    context.update(_dump(request.bureau))
    context["tenantId"] = request.tenantId
    context["productType"] = request.productType
    for alias, target in ALIASES.items():
        if target in context:
            context[alias] = context[target]
    context["kycVerified"] = bool(context.get("panVerified")) and bool(context.get("aadhaarVerified"))
    context["stableEmployment"] = context.get("employmentType") in {"SALARIED", "SELF_EMPLOYED"}
    context["noDpd"] = (
        (context.get("maxDPD") or 0) <= 0
        and (context.get("dpd30Count") or 0) <= 0
        and (context.get("dpd60Count") or 0) <= 0
        and (context.get("dpd90Count") or 0) <= 0
    )
    context["noFraud"] = not bool(context.get("fraudFlag") or context.get("blacklistMatch"))
    context["noOverdue"] = (context.get("overdueAmount") or 0) <= 0
    return context

