import time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import BureauRisk, JourneyAction, RuleType, ScorecardDecision
from app.models.audit import ScorecardExecutionAudit
from app.models.rule import RuleMaster
from app.models.scorecard import ScorecardResult
from app.schemas.scorecard import ScorecardRequest, ScorecardResponse
from app.services.bureau import BureauRiskClassifier
from app.services.context import build_evaluation_context
from app.services.hash import stable_payload_hash
from app.services.rule_engine import RuleEngine
from app.services.rule_repository import RuleRepository


class ScorecardService:
    def __init__(self) -> None:
        self.rules = RuleRepository()
        self.engine = RuleEngine()
        self.bureau = BureauRiskClassifier()

    def _existing_result(
        self, db: Session, request: ScorecardRequest, request_hash: str
    ) -> ScorecardResult | None:
        stmt = (
            select(ScorecardResult)
            .where(
                ScorecardResult.lead_id == request.application.leadId,
                ScorecardResult.tenant_id == request.tenantId,
                ScorecardResult.product_type == request.productType,
                ScorecardResult.request_hash == request_hash,
            )
            .order_by(ScorecardResult.created_at.desc())
        )
        return db.scalars(stmt).first()

    def generate(self, db: Session, request: ScorecardRequest, persist: bool = True) -> ScorecardResponse:
        start = time.perf_counter()
        payload_hash = stable_payload_hash(request.model_dump())
        if persist and not request.forceRecalculate:
            existing = self._existing_result(db, request, payload_hash)
            if existing:
                return self._to_response(existing)

        audit = ScorecardExecutionAudit(
            lead_id=request.application.leadId,
            tenant_id=request.tenantId,
            product_type=request.productType,
            request_hash=payload_hash,
            matched_rules=[],
            skipped_rules=[],
            status="STARTED",
        )
        if persist:
            db.add(audit)
            db.flush()

        try:
            response = self._execute(db, request)
            if persist:
                result = ScorecardResult(
                    tenant_id=request.tenantId,
                    product_type=request.productType,
                    lead_id=response.leadId,
                    final_score=response.finalScore,
                    decision=response.decision,
                    underwriting_required=response.underwritingRequired,
                    reject_flag=response.rejectFlag,
                    journey_action=response.journeyAction,
                    bureau_risk=response.bureauRisk,
                    score_breakup={k: str(v) for k, v in response.scoreBreakup.items()},
                    triggered_rules=response.triggeredRules,
                    reason_codes=response.reasonCodes,
                    request_hash=payload_hash,
                )
                db.add(result)
                audit.matched_rules = response.triggeredRules
                audit.status = "SUCCESS"
                audit.latency_ms = int((time.perf_counter() - start) * 1000)
                db.commit()
                db.refresh(result)
                return self._to_response(result)
            return response
        except Exception as exc:
            if persist:
                audit.status = "FAILED"
                audit.error_message = str(exc)
                audit.latency_ms = int((time.perf_counter() - start) * 1000)
                db.commit()
            raise

    def _execute(self, db: Session, request: ScorecardRequest) -> ScorecardResponse:
        context = build_evaluation_context(request)
        rules = self.rules.get_active_rules(
            db, request.tenantId, request.productType, request.application.dealerId
        )

        hard_reject = self.engine.evaluate(
            [rule for rule in rules if rule.rule_type == RuleType.HARD_REJECT], context
        )
        score, breakup, score_eval = self.engine.score(rules, context)
        bureau_risk = self.bureau.classify(context)
        non_stp = self.engine.evaluate(
            [rule for rule in rules if rule.rule_type == RuleType.NON_STP], context
        )
        stp_eligibility_rules = [
            rule for rule in rules if rule.rule_type == RuleType.STP_ELIGIBILITY
        ]
        stp_eval = self.engine.evaluate(stp_eligibility_rules, context)

        decision = self._decide(
            score=score,
            hard_reject_rules=hard_reject.matched,
            non_stp_rules=non_stp.matched,
            stp_rules=stp_eligibility_rules,
            stp_matched=stp_eval.matched,
            bureau_risk=bureau_risk,
        )
        underwriting_required = decision in {
            ScorecardDecision.NON_STP,
            ScorecardDecision.CONDITIONAL_STP,
        }
        reject_flag = decision == ScorecardDecision.REJECT
        journey_action = self._journey_action(decision)

        triggered_rules = (
            hard_reject.codes + score_eval.codes + non_stp.codes + stp_eval.codes
        )
        reason_codes = list(
            dict.fromkeys(
                hard_reject.reason_codes
                + score_eval.reason_codes
                + non_stp.reason_codes
                + stp_eval.reason_codes
            )
        )

        return ScorecardResponse(
            leadId=request.application.leadId,
            finalScore=score,
            decision=decision,
            underwritingRequired=underwriting_required,
            rejectFlag=reject_flag,
            journeyAction=journey_action,
            bureauRisk=bureau_risk,
            reasonCodes=reason_codes,
            triggeredRules=triggered_rules,
            scoreBreakup=breakup,
        )

    def _decide(
        self,
        score: Decimal,
        hard_reject_rules: list[RuleMaster],
        non_stp_rules: list[RuleMaster],
        stp_rules: list[RuleMaster],
        stp_matched: list[RuleMaster],
        bureau_risk: BureauRisk,
    ) -> ScorecardDecision:
        if hard_reject_rules:
            return ScorecardDecision.REJECT
        all_stp_rules_match = bool(stp_rules) and len(stp_rules) == len(stp_matched)
        if (
            all_stp_rules_match
            and score >= Decimal("80")
            and not non_stp_rules
            and bureau_risk != BureauRisk.HIGH
        ):
            return ScorecardDecision.STP
        if non_stp_rules or bureau_risk == BureauRisk.HIGH:
            return ScorecardDecision.NON_STP
        if Decimal("65") <= score <= Decimal("79"):
            return ScorecardDecision.CONDITIONAL_STP
        return ScorecardDecision.NON_STP

    def _journey_action(self, decision: ScorecardDecision) -> JourneyAction:
        if decision == ScorecardDecision.STP:
            return JourneyAction.SKIP_UNDERWRITING
        if decision == ScorecardDecision.REJECT:
            return JourneyAction.REJECT_APPLICATION
        return JourneyAction.SEND_TO_UNDERWRITING

    def _to_response(self, result: ScorecardResult) -> ScorecardResponse:
        return ScorecardResponse(
            leadId=result.lead_id,
            finalScore=result.final_score,
            decision=result.decision,
            underwritingRequired=result.underwriting_required,
            rejectFlag=result.reject_flag,
            journeyAction=result.journey_action,
            bureauRisk=result.bureau_risk,
            reasonCodes=list(result.reason_codes or []),
            triggeredRules=list(result.triggered_rules or []),
            scoreBreakup={k: Decimal(str(v)) for k, v in (result.score_breakup or {}).items()},
        )
