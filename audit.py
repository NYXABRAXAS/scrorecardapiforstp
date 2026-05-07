from typing import Any

from sqlalchemy.orm import Session

from app.models.audit import RuleAuditLog
from app.models.rule import RuleMaster


def rule_to_dict(rule: RuleMaster | None) -> dict[str, Any] | None:
    if not rule:
        return None
    return {
        "id": rule.id,
        "tenant_id": rule.tenant_id,
        "product_type": rule.product_type,
        "dealer_id": rule.dealer_id,
        "rule_code": rule.rule_code,
        "rule_name": rule.rule_name,
        "rule_type": rule.rule_type,
        "field_name": rule.field_name,
        "operator": rule.operator,
        "field_value": rule.field_value,
        "score_value": str(rule.score_value) if rule.score_value is not None else None,
        "score_component": rule.score_component,
        "decision_action": rule.decision_action,
        "reason_code": rule.reason_code,
        "priority": rule.priority,
        "version": rule.version,
        "is_active": rule.is_active,
    }


def write_rule_audit(
    db: Session,
    rule_id: int | None,
    action: str,
    actor: str | None,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
) -> None:
    db.add(
        RuleAuditLog(
            rule_id=rule_id,
            action=action,
            actor=actor,
            before=before,
            after=after,
        )
    )

