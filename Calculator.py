"""A small Tkinter calculator with a restricted expression evaluator."""

from __future__ import annotations

import ast
import math
import operator
import tkinter as tk
from collections.abc import Callable

MAX_EXPRESSION_LENGTH = 256
MAX_AST_NODES = 64
MAX_EXPONENT = 100

_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
_FUNCTIONS: dict[str, Callable[[float], float]] = {
    "log": math.log,
    "sqrt": math.sqrt,
}
_CONSTANTS = {"e": math.e, "pi": math.pi}


class InvalidExpression(ValueError):
    """Raised when an expression contains unsupported or excessive input."""


def _ensure_reasonable_number(value: int | float) -> int | float:
    if type(value) not in (int, float):
        raise InvalidExpression("result must be a real number")
    if isinstance(value, int) and value.bit_length() > 4096:
        raise InvalidExpression("result is too large")
    if isinstance(value, float) and not math.isfinite(value):
        raise InvalidExpression("result must be finite")
    return value


def _evaluate_node(node: ast.AST) -> int | float:
    if isinstance(node, ast.Expression):
        return _evaluate_node(node.body)

    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return _ensure_reasonable_number(node.value)

    if isinstance(node, ast.Name) and node.id in _CONSTANTS:
        return _CONSTANTS[node.id]

    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise InvalidExpression("exponent is too large")
        try:
            result = _BINARY_OPERATORS[type(node.op)](left, right)
        except (ArithmeticError, OverflowError, ValueError) as exc:
            raise InvalidExpression(str(exc)) from exc
        return _ensure_reasonable_number(result)

    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _ensure_reasonable_number(
            _UNARY_OPERATORS[type(node.op)](_evaluate_node(node.operand))
        )

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _FUNCTIONS
        and len(node.args) == 1
        and not node.keywords
    ):
        try:
            result = _FUNCTIONS[node.func.id](_evaluate_node(node.args[0]))
        except (ArithmeticError, OverflowError, ValueError) as exc:
            raise InvalidExpression(str(exc)) from exc
        return _ensure_reasonable_number(result)

    raise InvalidExpression("unsupported expression")


def evaluate_expression(expression: str) -> int | float:
    """Evaluate the calculator's small arithmetic language safely."""
    if not expression or len(expression) > MAX_EXPRESSION_LENGTH:
        raise InvalidExpression("expression is empty or too long")

    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise InvalidExpression("invalid syntax") from exc

    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise InvalidExpression("expression is too complex")
    return _evaluate_node(tree)


def create_calculator(root: tk.Tk) -> None:
    """Build the calculator widgets in an existing Tk root."""
    root.title("CALCULADORA")
    root.geometry("392x600")
    root.configure(background="SkyBlue4")

    button_color = "gray77"
    button_width = 11
    button_height = 3
    display_text = tk.StringVar(root, value="0")
    expression = ""

    def append(value: str) -> None:
        nonlocal expression
        expression += value
        display_text.set(expression)

    def clear() -> None:
        nonlocal expression
        expression = ""
        display_text.set("0")

    def calculate() -> None:
        nonlocal expression
        try:
            result = evaluate_expression(expression)
        except (InvalidExpression, ArithmeticError):
            expression = ""
            display_text.set("ERROR")
        else:
            expression = str(result)
            display_text.set(expression)

    buttons = [
        ("0", "0", 107, 360),
        ("1", "1", 17, 180),
        ("2", "2", 107, 180),
        ("3", "3", 197, 180),
        ("4", "4", 17, 240),
        ("5", "5", 107, 240),
        ("6", "6", 197, 240),
        ("7", "7", 17, 300),
        ("8", "8", 107, 300),
        ("9", "9", 197, 300),
        ("+", "+", 287, 240),
        ("-", "-", 287, 300),
        ("π", "pi", 17, 360),
        (".", ".", 107, 420),
        ("×", "*", 287, 360),
        ("÷", "/", 287, 420),
        ("√", "sqrt(", 17, 420),
        ("(", "(", 17, 480),
        (")", ")", 107, 480),
        ("%", "%", 197, 480),
        ("ln", "log(", 197, 360),
        ("EXP", "**", 197, 420),
    ]
    for label, value, x, y in buttons:
        tk.Button(
            root,
            text=label,
            bg=button_color,
            width=button_width,
            height=button_height,
            command=lambda value=value: append(value),
        ).place(x=x, y=y)

    tk.Button(
        root,
        text="C",
        bg=button_color,
        width=button_width,
        height=button_height,
        command=clear,
    ).place(x=287, y=180)
    tk.Button(
        root,
        text="=",
        bg=button_color,
        width=button_width,
        height=button_height,
        command=calculate,
    ).place(x=287, y=480)

    tk.Entry(
        root,
        font=("arial", 20, "bold"),
        width=22,
        textvariable=display_text,
        bd=20,
        bg="powder blue",
        justify="right",
        state="readonly",
        readonlybackground="powder blue",
    ).place(x=10, y=60)


def main() -> None:
    root = tk.Tk()
    create_calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
