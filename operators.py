from decimal import Decimal, InvalidOperation
from typing import Any


def _to_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
    return None


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _split_values(expected: str) -> list[str]:
    return [item.strip() for item in expected.split(",") if item.strip()]


def evaluate_operator(actual: Any, operator: str, expected: str) -> bool:
    op = operator.strip().upper()
    if actual is None:
        return False

    actual_bool = _to_bool(actual)
    expected_bool = _to_bool(expected)
    if actual_bool is not None and expected_bool is not None and op in {"=", "==", "!=", "<>"}:
        return actual_bool == expected_bool if op in {"=", "=="} else actual_bool != expected_bool

    actual_num = _to_decimal(actual)
    if op == "BETWEEN":
        bounds = _split_values(expected)
        if actual_num is None or len(bounds) != 2:
            return False
        low = _to_decimal(bounds[0])
        high = _to_decimal(bounds[1])
        return low is not None and high is not None and low <= actual_num <= high

    expected_num = _to_decimal(expected)
    if actual_num is not None and expected_num is not None:
        if op in {"=", "=="}:
            return actual_num == expected_num
        if op in {"!=", "<>"}:
            return actual_num != expected_num
        if op == ">":
            return actual_num > expected_num
        if op == ">=":
            return actual_num >= expected_num
        if op == "<":
            return actual_num < expected_num
        if op == "<=":
            return actual_num <= expected_num

    actual_str = str(actual).strip().upper()
    expected_str = str(expected).strip().upper()
    if op in {"=", "=="}:
        return actual_str == expected_str
    if op in {"!=", "<>"}:
        return actual_str != expected_str
    if op in {"IN", "NOT_IN"}:
        values = {value.upper() for value in _split_values(expected)}
        matched = actual_str in values
        return matched if op == "IN" else not matched

    raise ValueError(f"Unsupported operator: {operator}")

