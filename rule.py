from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import DecisionAction, RuleType


class RuleBase(BaseModel):
    tenant_id: str = "default"
    product_type: str = "TWO_WHEELER_LOAN"
    dealer_id: str | None = None
    rule_code: str = Field(min_length=2, max_length=100)
    rule_name: str = Field(min_length=2, max_length=255)
    rule_type: RuleType
    field_name: str = Field(min_length=1, max_length=100)
    operator: str = Field(min_length=1, max_length=20)
    field_value: str = Field(min_length=1, max_length=255)
    score_value: Decimal | None = None
    score_component: str | None = None
    decision_action: DecisionAction | None = None
    reason_code: str = Field(min_length=2, max_length=100)
    priority: int = 100
    is_active: bool = True


class RuleCreate(RuleBase):
    created_by: str | None = "system"


class RuleUpdate(BaseModel):
    rule_name: str | None = None
    field_name: str | None = None
    operator: str | None = None
    field_value: str | None = None
    score_value: Decimal | None = None
    score_component: str | None = None
    decision_action: DecisionAction | None = None
    reason_code: str | None = None
    priority: int | None = None
    is_active: bool | None = None
    actor: str | None = "system"


class RuleStatusUpdate(BaseModel):
    is_active: bool
    actor: str | None = "system"


class RuleResponse(RuleBase):
    id: int
    version: int
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

