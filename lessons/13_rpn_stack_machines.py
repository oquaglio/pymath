# %% [markdown]
# # 13. RPN and stack machines
#
# **Reverse Polish Notation** puts the operator *after* its operands:
#
# | Infix (what you write) | RPN (what machines run) |
# |---|---|
# | `3 + 4` | `3 4 +` |
# | `(3 + 4) * 2` | `3 4 + 2 *` |
# | `3 + 4 * 2` | `3 4 2 * +` |
#
# It's famous from HP calculators, but the notation has nothing to do with
# hardware. It's how **CPython evaluates every expression you write** — proved
# at the bottom of this lesson.
#
# The name honours Jan Łukasiewicz, the Polish logician who devised the *prefix*
# form (`+ 3 4`) in the 1920s. Reversing it puts operators last, which is what
# makes a stack work.

# %%
from pymath import *  # noqa: F403
from pymath import rpn

# %% [markdown]
# ## The rule: two lines, no exceptions
#
# 1. See a **number** → push it on the stack.
# 2. See an **operator** → pop what it needs, compute, push the result.
#
# That's the entire language. Watch `3 4 + 2 *` run:

# %%
def trace(expression):
    """Run an RPN expression, showing the stack after every token."""
    calc = rpn.Calculator()
    print(f"{'token':>8}  {'action':<22} stack")
    print(f"{'':>8}  {'':<22} []")
    for token in expression.split():
        before = len(calc.stack)
        calc.push(token)
        action = "push" if len(calc.stack) > before else f"apply {token}"
        print(f"{token:>8}  {action:<22} {[str(v) for v in calc.stack]}")
    return calc.result()


trace("3 4 + 2 *")

# %% [markdown]
# The same sum in infix, `(3 + 4) * 2`, needs brackets to stop `*` grabbing the
# 4 first. In RPN the `+` has already consumed 3 and 4 by the time `*` appears,
# so there is nothing left to disambiguate.
#
# **Parentheses are not "unnecessary" in RPN — they are inexpressible, because
# there is never any ambiguity for them to resolve.**

# %%
trace("3 4 2 * +")  # this is 3 + 4 * 2, the *other* reading

# %% [markdown]
# Same five tokens, different order, different answer. Order is the grammar.

# %% [markdown]
# ## Writing the evaluator
#
# The whole thing is a list and a dictionary:

# %%
import math
import operator

OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul,
       "/": operator.truediv, "^": operator.pow}


def tiny_rpn(expression):
    stack = []
    for token in expression.split():
        if token in OPS:
            b, a = stack.pop(), stack.pop()  # b comes off first — order matters
            stack.append(OPS[token](a, b))
        else:
            stack.append(float(token))
    return stack.pop()


for e in ["3 4 + 2 *", "5 1 2 + 4 * + 3 -", "2 10 ^"]:
    print(f"{e:22} = {tiny_rpn(e)}")

# %% [markdown]
# No parser. No precedence table. No parenthesis matching. Compare that with
# what infix needs — the shunting-yard algorithm below is *entirely* the cost of
# supporting infix notation.
#
# Note `b, a = stack.pop(), stack.pop()`. Getting that backwards is the classic
# RPN bug and it hides well, because it's invisible for `+` and `*`:

# %%
print("5 3 - should be 2:", rpn.evaluate("5 3 -"))
print("6 2 / should be 3:", rpn.evaluate("6 2 /"))

# %% [markdown]
# ## The project's version keeps values exact
#
# `pymath.rpn` pushes SymPy expressions rather than floats, so the stack holds
# surds and fractions — something no physical calculator does.

# %%
print(rpn.evaluate("2 sqrt"))
print(rpn.evaluate("1 2 / 1 3 / +"))
print(rpn.evaluate("pi 6 / sin"))
print(rpn.evaluate("2 sqrt 2 sqrt *"))  # √2 × √2 is exactly 2

# %% [markdown]
# Symbols work too, so the stack can hold algebra:

# %%
print(rpn.evaluate("x 2 ^ x 3 * + expand"))
print(rpn.evaluate("x 2 ^ 1 - factor"))

# %% [markdown]
# ## Stack operations
#
# HP calculators give you keys for rearranging the stack itself. The top four
# slots are named X, Y, Z, T, with X being the display.

# %%
calc = rpn.Calculator().push("1 2 3 4")
print(calc.display())

# %%
for op in ["dup", "swap", "drop", "over"]:
    c = rpn.Calculator().push("1 2 3").push(op)
    print(f"{op:6} 1 2 3 → {[str(v) for v in c.stack]}")

# %%
print("square a number:  3 dup *  →", rpn.evaluate("3 dup *"))
print("sum the stack:    1 2 3 4 sum →", rpn.evaluate("1 2 3 4 sum"))
print("product:          2 3 4 prod →", rpn.evaluate("2 3 4 prod"))

# %% [markdown]
# ## Shunting-yard: infix → RPN
#
# Dijkstra's algorithm, 1961. Operators wait in a holding area until an operator
# of lower or equal precedence arrives, which forces them out. That waiting is
# precisely what precedence rules and brackets encode.

# %%
for infix in ["3 + 4 * 2", "(3 + 4) * 2", "2 * 3 + 4", "1 + 2 + 3"]:
    print(f"{infix:14} → {rpn.to_rpn(infix)}")

# %% [markdown]
# ### Associativity is where it gets subtle
#
# `-` and `/` are **left**-associative: `10 - 2 - 3` means `(10 - 2) - 3`.
# `^` is **right**-associative: `2 ^ 3 ^ 2` means `2 ^ (3 ^ 2)`.

# %%
for infix in ["10 - 2 - 3", "10 - (2 - 3)", "2 ^ 3 ^ 2", "(2 ^ 3) ^ 2"]:
    converted = rpn.to_rpn(infix)
    print(f"{infix:14} → {converted:14} = {rpn.evaluate(converted)}")

# %% [markdown]
# Note `2 ^ 3 ^ 2 = 512` and `(2 ^ 3) ^ 2 = 64`. Get associativity wrong in a
# parser and this is how you find out.

# %% [markdown]
# ### And unary minus
#
# `-3 + 4` is `(-3) + 4 = 1`, not `-(3 + 4) = -7`. A prefix operator binds
# tighter than any binary one.

# %%
for infix in ["-3 + 4", "-3 * 4", "2 ^ -3", "-(2 + 3) * 4"]:
    converted = rpn.to_rpn(infix)
    print(f"{infix:14} → {converted:16} = {rpn.evaluate(converted)}")

# %% [markdown]
# ## Going back: RPN → infix
#
# The reverse direction shows exactly where parentheses come from. They appear
# only when a sub-expression's operator binds *looser* than the one above it.

# %%
for expr in ["3 4 + 2 *", "3 4 2 * +", "1 2 + 3 4 - *", "10 2 3 - -"]:
    print(f"{expr:14} → {rpn.to_infix(expr)}")

# %% [markdown]
# Round-tripping should be lossless in meaning, if not in spelling:

# %%
import sympy as sp

for infix in ["(3 + 4) * 2", "3 + 4 * 2", "2 * (3 + 4) / 7", "10 - (2 - 3)"]:
    back = rpn.to_infix(rpn.to_rpn(infix))
    same = sp.sympify(back.replace("^", "**")) == sp.sympify(infix.replace("^", "**"))
    print(f"{infix:18} → {back:18} equivalent: {same}")

# %% [markdown]
# ## The punchline: Python is a stack machine
#
# CPython compiles your infix source into stack bytecode. Disassemble an
# expression and you are looking at RPN:

# %%
print(rpn.bytecode("(a + b) * c"))

# %% [markdown]
# Read the opcodes: `LOAD a`, `LOAD b`, `BINARY_OP +`, `LOAD c`, `BINARY_OP *`.
#
# That is `a b + c *` — the RPN form, exactly what `to_rpn` produces:

# %%
print("to_rpn says:", rpn.to_rpn("(a + b) * c"))

# %% [markdown]
# `LOAD` pushes, `BINARY_OP` pops two and pushes one. The interpreter loop is
# `tiny_rpn` above, written in C with more opcodes.
#
# Try the other reading and watch the bytecode reorder itself:

# %%
print(rpn.bytecode("a + b * c"))

# %% [markdown]
# So infix is a **surface syntax for humans**. Underneath, the machine has been
# doing RPN the whole time. The parentheses you type are instructions to the
# compiler about what order to emit the opcodes in — they don't survive into the
# bytecode, because by then the order *is* the information.

# %% [markdown]
# ## Where else RPN lives
#
# * **PostScript** — every PDF is an RPN program. `72 72 moveto` is a stack op.
# * **Forth** — embedded firmware, Open Firmware boot ROMs, spacecraft.
# * **`dc(1)`** — the Unix desk calculator, older than Unix pipes. `bc` is just
#   an infix front-end that compiles down to `dc`.
# * **JVM bytecode / WebAssembly** — stack machines, same as CPython.
# * **Excel's calculation engine** — historically compiled formulas to RPN.
#
# `dc` ships on your machine. `p` prints the top of stack:

# %%
import shutil
import subprocess

# subprocess doesn't go through the shell, so a shell alias for `dc` can't
# shadow the real binary here.
dc_path = shutil.which("dc")
if dc_path:
    for program in ["3 4 + 2 * p", "2 10 ^ p", "10 2 - 3 - p"]:
        result = subprocess.run([dc_path], input=program, capture_output=True, text=True)
        print(f"dc: {program:16} → {result.stdout.strip() or result.stderr.strip()}")
else:
    print("dc not installed — try `sudo apt install dc` or `sudo dnf install bc`")

# %% [markdown]
# Same notation, same stack, a program from 1970.

# %% [markdown]
# ## Why anyone preferred it
#
# On a 1972 HP-35, RPN needed no parenthesis buffer and no precedence parser —
# a stack is a handful of registers and a pop. That saved transistors when
# transistors were the budget.
#
# The reason people *kept* using it after the constraint disappeared: you see
# every intermediate result as you go, and there's no "=" key committing you to
# a parse. For long chained calculations that's a real ergonomic win, which is
# why HP kept shipping RPN models for forty years.
#
# Try the interactive version:
#
# ```bash
# uv run pymath rpn                      # interactive stack calculator
# uv run pymath rpn "3 4 + 2 *"          # one-shot
# uv run pymath rpn --from-infix "(3 + 4) * 2"
# ```

# %% [markdown]
# ## Exercises
#
# 1. Convert `(1 + 2) * (3 + 4) - 5` to RPN by hand, then check with `to_rpn`.
# 2. What does `3 4 + 5 6 + *` evaluate to? Trace it before running it.
# 3. Extend `tiny_rpn` to support `sqrt` and `neg`.
# 4. `rpn.to_infix("2 3 4 + *")` — why does it need brackets when
#    `rpn.to_infix("2 3 4 * +")` doesn't?
# 5. Disassemble `(a + b) * (c + d)` and write out the RPN by reading the
#    opcodes.

# %%
print(rpn.to_rpn("(1 + 2) * (3 + 4) - 5"), "=", rpn.evaluate(rpn.to_rpn("(1 + 2) * (3 + 4) - 5")))
print(rpn.evaluate("3 4 + 5 6 + *"))
print(rpn.to_infix("2 3 4 + *"), "vs", rpn.to_infix("2 3 4 * +"))
