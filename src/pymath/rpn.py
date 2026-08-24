"""Reverse Polish Notation — a stack calculator over exact SymPy values.

RPN is a notation, not a hardware quirk. Operators come *after* their operands
(``3 4 +`` rather than ``3 + 4``), which means precedence is encoded in the
token order and parentheses become unnecessary.

Python itself works this way underneath: ``(a + b) * c`` compiles to the
bytecode ``LOAD a, LOAD b, BINARY_OP +, LOAD c, BINARY_OP *`` — which is
``a b + c *``, the RPN form. See :func:`bytecode` below.

Unlike a physical HP calculator, the stack here holds exact SymPy expressions,
so ``2 sqrt`` leaves ``sqrt(2)`` rather than 1.4142135623730951.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field

import sympy as sp

from .symbols import sym

# Binary operators: (function, precedence, right-associative?)
BINARY = {
    "+": (operator.add, 2, False),
    "-": (operator.sub, 2, False),
    "*": (operator.mul, 3, False),
    "/": (operator.truediv, 3, False),
    "^": (operator.pow, 4, True),  # 2^3^2 is 2^(3^2), so right-associative
    "**": (operator.pow, 4, True),
    "%": (sp.Mod, 3, False),
}

# Unary functions. Named as you'd find them on a calculator's keys.
UNARY = {
    "sqrt": sp.sqrt,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "ln": sp.log, "log": lambda v: sp.log(v, 10), "exp": sp.exp,
    "abs": sp.Abs, "neg": operator.neg, "inv": lambda v: 1 / v,
    "square": lambda v: v**2, "fact": sp.factorial,
    "floor": sp.floor, "ceil": sp.ceiling,
    "simplify": sp.simplify, "expand": sp.expand, "factor": sp.factor,
}

CONSTANTS = {"pi": sp.pi, "e": sp.E, "i": sp.I, "inf": sp.oo}

# Stack manipulation, borrowed from HP's RPN keys.
STACK_OPS = {"dup", "drop", "swap", "over", "roll", "clear", "sum", "prod"}


class RPNError(ValueError):
    """Raised when an expression is malformed or the stack runs dry."""


@dataclass
class Calculator:
    """An RPN stack machine. The top of the stack is HP's "X register".

    >>> c = Calculator().push("3", "4", "+")
    >>> c.x
    7
    """

    stack: list = field(default_factory=list)
    last_x: object = None

    # --- the stack ----------------------------------------------------------

    @property
    def x(self):
        """Top of stack — the value a calculator would show on its display."""
        return self.stack[-1] if self.stack else None

    @property
    def y(self):
        """Second from top."""
        return self.stack[-2] if len(self.stack) > 1 else None

    def _pop(self):
        if not self.stack:
            raise RPNError("stack is empty — not enough operands")
        return self.stack.pop()

    # --- evaluation ---------------------------------------------------------

    def push(self, *tokens: str) -> Calculator:
        """Feed tokens in, one at a time. Returns self so calls can chain.

        A token is a number, a constant, a symbol, an operator, a function, or
        a stack command.

        >>> Calculator().push("2", "sqrt").x
        sqrt(2)
        """
        for token in tokens:
            for part in str(token).split():
                self._step(part)
        return self

    def _step(self, token: str) -> None:
        if token in BINARY:
            b = self._pop()
            a = self._pop()  # order matters: "5 3 -" is 5 - 3, not 3 - 5
            self.last_x = b
            self.stack.append(_tidy(BINARY[token][0](a, b)))
        elif token in UNARY:
            a = self._pop()
            self.last_x = a
            self.stack.append(_tidy(UNARY[token](a)))
        elif token in STACK_OPS:
            self._stack_op(token)
        elif token in CONSTANTS:
            self.stack.append(CONSTANTS[token])
        else:
            self.stack.append(_parse_value(token))

    def _stack_op(self, token: str) -> None:
        match token:
            case "dup":  # copy X
                self.stack.append(self.x if self.stack else None)
            case "drop":
                self._pop()
            case "swap":  # exchange X and Y
                b, a = self._pop(), self._pop()
                self.stack.extend([b, a])
            case "over":  # copy Y to the top
                if len(self.stack) < 2:
                    raise RPNError("`over` needs two values on the stack")
                self.stack.append(self.stack[-2])
            case "roll":  # rotate the whole stack up
                if self.stack:
                    self.stack.insert(0, self._pop())
            case "clear":
                self.stack.clear()
            case "sum":
                self.stack = [_tidy(sp.Add(*self.stack))]
            case "prod":
                self.stack = [_tidy(sp.Mul(*self.stack))]

    def result(self):
        """The final value, insisting the stack ended with exactly one item."""
        if len(self.stack) != 1:
            raise RPNError(
                f"expected one value at the end, found {len(self.stack)}: {self.stack}"
            )
        return self.stack[0]

    def display(self, depth: int = 4) -> str:
        """The stack as a calculator would show it — X on the bottom line.

        >>> print(Calculator().push("1 2 3").display(3))
        Z: 1
        Y: 2
        X: 3
        """
        names = ["X", "Y", "Z", "T", *[f"S{i}" for i in range(4, 40)]]
        shown = self.stack[-depth:] if depth else self.stack
        lines = [
            f"{names[len(shown) - 1 - idx]}: {sp.sstr(value)}"
            for idx, value in enumerate(shown)
        ]
        return "\n".join(lines) if lines else "(empty)"


def _parse_value(token: str):
    """Read a token as an exact number, or fall back to a symbolic expression."""
    try:
        return sp.Integer(token) if _looks_int(token) else sp.Rational(token)
    except (TypeError, ValueError, sp.SympifyError):
        pass
    try:
        return sym(token)
    except Exception as err:
        raise RPNError(f"cannot understand token: {token!r}") from err


def _looks_int(token: str) -> bool:
    return token.lstrip("+-").isdigit()


def _tidy(value):
    """Keep results exact but tidy — SymPy leaves some results unevaluated."""
    return sp.nsimplify(value) if isinstance(value, float) else value


def evaluate(expression: str):
    """Evaluate a whole RPN expression exactly.

    >>> evaluate("3 4 + 2 *")
    14
    >>> evaluate("2 sqrt")
    sqrt(2)
    >>> evaluate("5 1 2 + 4 * + 3 -")
    14
    """
    return Calculator().push(expression).result()


# --- converting between the two notations ------------------------------------

def to_rpn(infix: str) -> str:
    """Convert infix to RPN using Dijkstra's shunting-yard algorithm.

    Operators wait on a holding stack until something of lower precedence
    arrives, which is exactly what parentheses would otherwise tell you.

    >>> to_rpn("(3 + 4) * 2")
    '3 4 + 2 *'
    >>> to_rpn("3 + 4 * 2")
    '3 4 2 * +'
    >>> to_rpn("2 ^ 3 ^ 2")
    '2 3 2 ^ ^'
    """
    output: list[str] = []
    holding: list[str] = []

    for token in _tokenize(infix):
        if token in BINARY:
            _, precedence, right_assoc = BINARY[token]
            # A prefix operator like `neg` binds tighter than any binary one,
            # so it must come off first: -3 + 4 is (-3) + 4, not -(3 + 4).
            while holding and holding[-1] in UNARY:
                output.append(holding.pop())
            while holding and holding[-1] in BINARY:
                top_precedence = BINARY[holding[-1]][1]
                if top_precedence > precedence or (
                    top_precedence == precedence and not right_assoc
                ):
                    output.append(holding.pop())
                else:
                    break
            holding.append(token)
        elif token in UNARY or token == "(":
            holding.append(token)
        elif token == ")":
            while holding and holding[-1] != "(":
                output.append(holding.pop())
            if not holding:
                raise RPNError("unbalanced parentheses")
            holding.pop()  # discard the "("
            if holding and holding[-1] in UNARY:
                output.append(holding.pop())
        else:
            output.append(token)

    while holding:
        token = holding.pop()
        if token == "(":
            raise RPNError("unbalanced parentheses")
        output.append(token)
    return " ".join(output)


def to_infix(rpn_expression: str) -> str:
    """Rebuild infix notation from RPN, adding only the parentheses needed.

    >>> to_infix("3 4 + 2 *")
    '(3 + 4) * 2'
    >>> to_infix("3 4 2 * +")
    '3 + 4 * 2'
    """
    # Each entry is (rendered text, precedence of its outermost operator).
    stack: list[tuple[str, int]] = []
    for token in rpn_expression.split():
        if token in BINARY:
            _, precedence, right_assoc = BINARY[token]
            if len(stack) < 2:
                raise RPNError(f"not enough operands for {token!r}")
            right_text, right_prec = stack.pop()
            left_text, left_prec = stack.pop()
            if left_prec < precedence:
                left_text = f"({left_text})"
            # The right operand also needs brackets at equal precedence, since
            # a - (b - c) differs from a - b - c.
            if right_prec < precedence or (right_prec == precedence and not right_assoc):
                right_text = f"({right_text})"
            stack.append((f"{left_text} {token} {right_text}", precedence))
        elif token in UNARY:
            if not stack:
                raise RPNError(f"not enough operands for {token!r}")
            inner, inner_prec = stack.pop()
            if token == "neg":  # render as a minus sign, not neg(...)
                stack.append((f"-{inner}" if inner_prec >= 10 else f"-({inner})", 5))
            else:
                stack.append((f"{token}({inner})", 10))
        else:
            stack.append((token, 10))

    if len(stack) != 1:
        raise RPNError(f"malformed RPN: {len(stack)} values left on the stack")
    return stack[0][0]


def _tokenize(infix: str) -> list[str]:
    """Split infix text into tokens, treating a leading minus as `neg`."""
    tokens: list[str] = []
    buffer = ""
    for char in infix.replace("**", "^"):
        if char.isalnum() or char == ".":
            buffer += char
            continue
        if buffer:
            tokens.append(buffer)
            buffer = ""
        if char.isspace():
            continue
        if char in "()":
            tokens.append(char)
        else:
            # A minus is unary when nothing subtractable precedes it.
            previous = tokens[-1] if tokens else None
            if char == "-" and (previous is None or previous == "(" or previous in BINARY):
                tokens.append("neg")
            else:
                tokens.append(char)
    if buffer:
        tokens.append(buffer)
    return tokens


def bytecode(expression: str) -> str:
    """Show that CPython evaluates in RPN too, by disassembling an expression.

    The `LOAD`/`BINARY_OP` sequence is the RPN form of what you wrote.
    """
    import dis
    import io

    out = io.StringIO()
    dis.dis(compile(expression, "<rpn>", "eval"), file=out)
    return out.getvalue()


__all__ = [
    "Calculator", "RPNError", "evaluate", "to_rpn", "to_infix", "bytecode",
    "BINARY", "UNARY", "CONSTANTS", "STACK_OPS",
]
