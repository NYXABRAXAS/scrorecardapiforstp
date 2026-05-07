import json
from decimal import Decimal
from typing import Any

from redis import Redis
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.rule import RuleMaster


def _serialize_rule(rule: RuleMaster) -> dict[str, Any]:
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
        "created_by": rule.created_by,
        "created_at": rule.created_at.isoformat(),
        "updated_at": rule.updated_at.isoformat(),
    }


def _hydrate_rule(data: dict[str, Any]) -> RuleMaster:
    rule = RuleMaster(**{k: v for k, v in data.items() if k not in {"created_at", "updated_at"}})
    if data.get("score_value") is not None:
        rule.score_value = Decimal(data["score_value"])
    return rule


class RuleRepository:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.redis: Redis | None = None
        if self.settings.redis_url:
            try:
                self.redis = Redis.from_url(self.settings.redis_url, decode_responses=True)
            except Exception:
                self.redis = None

    def cache_key(self, tenant_id: str, product_type: str, dealer_id: str | None) -> str:
        dealer = dealer_id or "ALL"
        return f"rules:{tenant_id}:{product_type}:{dealer}"

    def get_active_rules(
        self, db: Session, tenant_id: str, product_type: str, dealer_id: str | None
    ) -> list[RuleMaster]:
        key = self.cache_key(tenant_id, product_type, dealer_id)
        if self.redis:
            try:
                cached = self.redis.get(key)
                if cached:
                    return [_hydrate_rule(item) for item in json.loads(cached)]
            except Exception:
                pass

        stmt = (
            select(RuleMaster)
            .where(
                RuleMaster.is_active.is_(True),
                RuleMaster.tenant_id == tenant_id,
                RuleMaster.product_type == product_type,
                or_(RuleMaster.dealer_id.is_(None), RuleMaster.dealer_id == dealer_id),
            )
            .order_by(RuleMaster.priority.asc(), RuleMaster.id.asc())
        )
        rules = list(db.scalars(stmt).all())
        if self.redis:
            try:
                self.redis.setex(key, 300, json.dumps([_serialize_rule(rule) for rule in rules]))
            except Exception:
                pass
        return rules

    def invalidate(self, tenant_id: str, product_type: str, dealer_id: str | None = None) -> None:
        if not self.redis:
            return
        keys = [
            self.cache_key(tenant_id, product_type, dealer_id),
            self.cache_key(tenant_id, product_type, None),
        ]
        try:
            self.redis.delete(*set(keys))
        except Exception:
            pass

    def list_rules(
        self,
        db: Session,
        tenant_id: str | None = None,
        product_type: str | None = None,
        dealer_id: str | None = None,
        rule_type: str | None = None,
        is_active: bool | None = None,
    ) -> list[RuleMaster]:
        filters = []
        if tenant_id:
            filters.append(RuleMaster.tenant_id == tenant_id)
        if product_type:
            filters.append(RuleMaster.product_type == product_type)
        if dealer_id:
            filters.append(RuleMaster.dealer_id == dealer_id)
        if rule_type:
            filters.append(RuleMaster.rule_type == rule_type)
        if is_active is not None:
            filters.append(RuleMaster.is_active.is_(is_active))
        stmt = select(RuleMaster).order_by(RuleMaster.priority.asc(), RuleMaster.id.asc())
        if filters:
            stmt = stmt.where(and_(*filters))
        return list(db.scalars(stmt).all())

