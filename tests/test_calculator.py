import math

import pytest

from Calculator import InvalidExpression, evaluate_expression


def test_supported_arithmetic_and_functions() -> None:
    assert evaluate_expression("2 + 3 * 4") == 14
    assert evaluate_expression("sqrt(81) + log(e)") == 10
    assert evaluate_expression("pi") == pytest.approx(math.pi)
    assert evaluate_expression("10 % 4") == 2


@pytest.mark.parametrize(
    "expression",
    [
        "",
        "__import__('os').getcwd()",
        "open('file')",
        "(1).__class__",
        "2 ** 101",
        "(-1) ** 0.5",
        "1 / 0",
        "True + 1",
    ],
)
def test_rejects_unsafe_or_invalid_expressions(expression: str) -> None:
    with pytest.raises(InvalidExpression):
        evaluate_expression(expression)
