from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import require_auth
from app.db.session import get_db
from app.models.rule import RuleMaster
from app.schemas.rule import RuleCreate, RuleResponse, RuleStatusUpdate, RuleUpdate
from app.services.audit import rule_to_dict, write_rule_audit
from app.services.rule_repository import RuleRepository

router = APIRouter(prefix="/rules", tags=["Rule Management"], dependencies=[Depends(require_auth)])
repo = RuleRepository()


@router.get("", response_model=list[RuleResponse])
def list_rules(
    tenant_id: str | None = None,
    product_type: str | None = None,
    dealer_id: str | None = None,
    rule_type: str | None = None,
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[RuleMaster]:
    return repo.list_rules(db, tenant_id, product_type, dealer_id, rule_type, is_active)


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(payload: RuleCreate, db: Session = Depends(get_db)) -> RuleMaster:
    dealer_filter = (
        RuleMaster.dealer_id.is_(None)
        if payload.dealer_id is None
        else RuleMaster.dealer_id == payload.dealer_id
    )
    latest_version = db.scalar(
        select(func.max(RuleMaster.version)).where(
            RuleMaster.rule_code == payload.rule_code,
            RuleMaster.tenant_id == payload.tenant_id,
            RuleMaster.product_type == payload.product_type,
            dealer_filter,
        )
    )
    rule = RuleMaster(**payload.model_dump(), version=(latest_version or 0) + 1)
    db.add(rule)
    db.flush()
    write_rule_audit(db, rule.id, "CREATE", payload.created_by, None, rule_to_dict(rule))
    db.commit()
    db.refresh(rule)
    repo.invalidate(rule.tenant_id, rule.product_type, rule.dealer_id)
    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, payload: RuleUpdate, db: Session = Depends(get_db)) -> RuleMaster:
    rule = db.get(RuleMaster, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    before = rule_to_dict(rule)
    updates = payload.model_dump(exclude_unset=True)
    actor = updates.pop("actor", "system")
    for field, value in updates.items():
        setattr(rule, field, value)
    write_rule_audit(db, rule.id, "UPDATE", actor, before, rule_to_dict(rule))
    db.commit()
    db.refresh(rule)
    repo.invalidate(rule.tenant_id, rule.product_type, rule.dealer_id)
    return rule


@router.patch("/{rule_id}/status", response_model=RuleResponse)
def update_rule_status(
    rule_id: int, payload: RuleStatusUpdate, db: Session = Depends(get_db)
) -> RuleMaster:
    rule = db.get(RuleMaster, rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    before = rule_to_dict(rule)
    rule.is_active = payload.is_active
    write_rule_audit(db, rule.id, "STATUS_UPDATE", payload.actor, before, rule_to_dict(rule))
    db.commit()
    db.refresh(rule)
    repo.invalidate(rule.tenant_id, rule.product_type, rule.dealer_id)
    return rule
