from dataclasses import dataclass, field
from decimal import Decimal

from app.core.enums import RuleType
from app.models.rule import RuleMaster
from app.services.operators import evaluate_operator


@dataclass
class RuleEvaluation:
    matched: list[RuleMaster] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)

    @property
    def codes(self) -> list[str]:
        return [rule.rule_code for rule in self.matched]

    @property
    def reason_codes(self) -> list[str]:
        return [rule.reason_code for rule in self.matched]


class RuleEngine:
    def evaluate(self, rules: list[RuleMaster], context: dict) -> RuleEvaluation:
        result = RuleEvaluation()
        for rule in sorted(rules, key=lambda item: item.priority):
            try:
                if evaluate_operator(context.get(rule.field_name), rule.operator, rule.field_value):
                    result.matched.append(rule)
                else:
                    result.skipped.append(rule.rule_code)
            except ValueError:
                result.skipped.append(rule.rule_code)
        return result

    def score(self, rules: list[RuleMaster], context: dict) -> tuple[Decimal, dict[str, Decimal], RuleEvaluation]:
        score_rules = [rule for rule in rules if rule.rule_type == RuleType.SCORE]
        evaluation = self.evaluate(score_rules, context)
        total = Decimal("0")
        breakup: dict[str, Decimal] = {}
        for rule in evaluation.matched:
            value = Decimal(rule.score_value or 0)
            component = rule.score_component or "other"
            breakup[component] = breakup.get(component, Decimal("0")) + value
            total += value
        capped = max(Decimal("0"), min(Decimal("100"), total))
        return capped, breakup, evaluation

