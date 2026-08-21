# %% [markdown]
# # 12. High-precision arithmetic
#
# A Python `float` is a hardware IEEE 754 double: 53 bits of mantissa, about
# **15–17 significant decimal digits**, and that's the ceiling. It's fast because
# the CPU does it in one instruction.
#
# When 17 digits isn't enough — or when the *decimal* digits specifically have to
# be exact — you swap the hardware for a library. This lesson covers the five
# options, what each is for, and how much speed you give up.
#
# | Tool | Kind | Precision | Backed by |
# |---|---|---|---|
# | `int` | exact integers | unlimited | CPython (C) |
# | `fractions.Fraction` | exact rationals | unlimited, no rounding *ever* | CPython |
# | `decimal` | decimal floats | up to ~10¹⁸ digits | **libmpdec (C)** |
# | `mpmath` | binary floats + full maths library | arbitrary | Python, **C via gmpy2** |
# | `gmpy2` | binary floats/ints/complex | arbitrary | **GMP / MPFR / MPC (C)** |
# | `numpy.longdouble` | extended float | 64-bit mantissa (~18–19 digits) | hardware |

# %%
import math
from decimal import Decimal, getcontext, localcontext
from fractions import Fraction

# %% [markdown]
# ## Why floats lie
#
# The classic. `0.1` cannot be written exactly in binary, any more than `1/3`
# can be written exactly in decimal — so it's stored as the nearest double, and
# the error shows up when you add.

# %%
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(f"0.1 is really: {Decimal(0.1)}")  # the exact value of the stored double

# %% [markdown]
# Nothing is broken — that's the correct answer for binary floating point. The
# fix is to choose a number type whose *base* matches your problem: base 10 for
# money, exact rationals for algebra, or simply more digits.

# %% [markdown]
# ## 1. Integers are already unlimited
#
# Python's `int` is arbitrary precision out of the box, implemented in C. No
# library needed, no overflow — ever.

# %%
print(2**1000)
print(math.factorial(100))
print(len(str(math.factorial(1000))), "digits in 1000!")

# %% [markdown]
# The catch: dividing drops you back to floats. Use `//` to stay exact, or
# `Fraction`.

# %%
print(type(10 / 3), 10 / 3)  # float — precision lost here
print(type(10 // 3), 10 // 3)  # int — exact

# %% [markdown]
# ## 2. `decimal` — base-10 arithmetic, in C
#
# The stdlib `decimal` module is a binding to **libmpdec**, a C implementation of
# the IEEE 754 decimal arithmetic spec. It's the right tool whenever the decimal
# digits are the point: money, tax, invoices, anything audited.

# %%
import _decimal
import _pydecimal
from decimal import Decimal

print("using the C implementation:", Decimal is _decimal.Decimal)
print("pure-Python fallback exists:", _pydecimal.Decimal is not Decimal)

# %% [markdown]
# Base 10 means what you'd expect happens:

# %%
print(Decimal("0.1") + Decimal("0.2"))
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))

# %% [markdown]
# **Always build a Decimal from a string.** `Decimal(0.1)` inherits the float's
# error before you start — you've precision-upgraded a wrong number:

# %%
print("from string:", Decimal("0.1"))
print("from float: ", Decimal(0.1))

# %% [markdown]
# ### Setting the precision
#
# You asked about 34 digits — that's exactly **IEEE 754 decimal128**, the
# standard's 128-bit decimal format. Set it with `prec`:

# %%
getcontext().prec = 34  # decimal128
print(Decimal(1) / Decimal(7))

# %% [markdown]
# The other named formats: decimal32 is 7 digits, decimal64 is 16, decimal128 is
# 34. But Python isn't limited to them — `prec` takes any value up to `MAX_PREC`,
# which on a 64-bit build is:

# %%
import decimal

print(f"{decimal.MAX_PREC:,} digits")

# %% [markdown]
# That's 10¹⁸ digits — you'll exhaust your RAM long before the limit. So the
# practical answer to "what's the maximum?" is **however much memory you have**.

# %%
with localcontext() as ctx:  # a temporary precision change
    ctx.prec = 100
    print(Decimal(1) / Decimal(7))
    print(Decimal(2).sqrt())

print("back to", getcontext().prec, "digits outside the block")

# %% [markdown]
# ### Rounding modes
#
# This is the other half of why finance uses `decimal`: you control rounding
# explicitly rather than inheriting whatever the hardware does.

# %%
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP

cent = Decimal("0.01")
print(f"{'value':>8}  {'HALF_UP':>8}  {'HALF_EVEN':>9}  {'DOWN':>6}")
for value in ("2.665", "2.675", "0.125", "0.135"):
    d = Decimal(value)
    print(f"{value:>8}  {d.quantize(cent, rounding=ROUND_HALF_UP):>8}"
          f"  {d.quantize(cent, rounding=ROUND_HALF_EVEN):>9}"
          f"  {d.quantize(cent, rounding=ROUND_DOWN):>6}")

# %% [markdown]
# `ROUND_HALF_EVEN` (banker's rounding) is the default, because always rounding
# halves up introduces a systematic upward bias over many transactions. It
# breaks ties toward the *even* digit instead — so `2.665 → 2.66` (6 is even)
# but `2.675 → 2.68` (7 is odd, so it goes up). Half the ties go each way, and
# the bias cancels.
#
# Compare with the float version, which can't even represent 2.675 correctly:

# %%
print("float round(2.675, 2) =", round(2.675, 2), "← surprising, but correct for binary")

# %% [markdown]
# ### The cost of C
#
# `decimal` is fast *because* it's C. Here's the same work through the
# pure-Python fallback:

# %%
import timeit

setup_c = "from decimal import Decimal, getcontext; getcontext().prec=34; a=Decimal(1)/Decimal(7)"
setup_py = "from _pydecimal import Decimal, getcontext; getcontext().prec=34; a=Decimal(1)/Decimal(7)"
c_time = timeit.timeit("a*a", setup=setup_c, number=100_000)
py_time = timeit.timeit("a*a", setup=setup_py, number=100_000)
print(f"C libmpdec:  {c_time:.4f}s")
print(f"pure Python: {py_time:.4f}s   ({py_time / c_time:.0f}× slower)")

# %% [markdown]
# ## 3. `fractions.Fraction` — no rounding at all
#
# `decimal` still rounds, just at a precision you choose. `Fraction` never
# rounds: it keeps a numerator and denominator as exact integers.

# %%
third = Fraction(1, 3)
print(third + third + third, "← exactly 1, not 0.9999...")
print(sum([Fraction(1, 10)] * 10) == 1, "← ten tenths is exactly one")
print(sum([0.1] * 10) == 1.0, "← in floats, it isn't")

# %%
print(Fraction("0.1") + Fraction("0.2") == Fraction("0.3"))
print(Fraction(math.pi).limit_denominator(1000), "≈ pi")

# %% [markdown]
# The trade-off: denominators grow. Add a hundred fractions with different
# denominators and they multiply out into enormous integers.

# %%
total = sum(Fraction(1, k) for k in range(1, 51))  # harmonic series
print("H₅₀ =", total)
print("denominator has", len(str(total.denominator)), "digits")

# %% [markdown]
# ## 4. `mpmath` — arbitrary precision *mathematics*
#
# `decimal` gives you arithmetic. `mpmath` gives you the whole maths library —
# trig, logs, integrals, ODEs, root-finding, special functions — at any
# precision. You already have it: SymPy depends on it.
#
# Precision is set as `mp.dps` (decimal places) or `mp.prec` (bits).

# %%
from mpmath import mp, mpf

mp.dps = 50
print("π  =", mp.pi)
print("e  =", mp.e)
print("√2 =", mp.sqrt(2))
print("sin(1) =", mp.sin(1))

# %%
mp.dps = 1000  # dps counts *significant* digits, so "3." plus 999 decimals
pi_1000 = str(mp.pi)
print("π to 1000 significant digits, last 50 shown:", pi_1000[-50:])
print("significant digits:", len(pi_1000.replace(".", "")))

# %% [markdown]
# Worth checking against a known value rather than trusting it. π's first 1000
# *decimal* places famously end `...1989` — index carefully, since the string
# starts `3.` and so decimal place *k* sits at index *k+1*:

# %%
mp.dps = 1005
digits = str(mp.pi)
print("first 12 chars: ", digits[:12])
print("decimals 996-1000:", digits[997:1002], "← ends in 1989 as it should")

# %% [markdown]
# ### Calculus at arbitrary precision
#
# This is what makes mpmath more than a big-number type:

# %%
mp.dps = 40
print("∫₀^∞ e^(-x²) dx =", mp.quad(lambda v: mp.exp(-(v**2)), [0, mp.inf]))
print("√π / 2          =", mp.sqrt(mp.pi) / 2)
print("root of cos x = x:", mp.findroot(lambda v: mp.cos(v) - v, 1))

# %% [markdown]
# ### mpmath quietly uses C if it can
#
# Pure Python by default — but if `gmpy2` is installed, mpmath switches its
# backend to GMP automatically and everything above gets faster with no code
# change.

# %%
import mpmath

print("mpmath backend:", mpmath.libmp.BACKEND)
print("('gmpy' means the C libraries are doing the work; 'python' means they aren't)")

# %% [markdown]
# ## 5. `gmpy2` — the C libraries directly
#
# `gmpy2` binds three of the most heavily optimised numeric libraries in
# existence:
#
# * **GMP** — arbitrary precision integers and rationals
# * **MPFR** — arbitrary precision floats, *correctly rounded* (every result is
#   the exact answer rounded once, which IEEE doubles don't guarantee for
#   transcendental functions)
# * **MPC** — the same for complex numbers
#
# Install it with `uv sync --extra precision`.

# %%
try:
    import gmpy2

    print("gmpy2", gmpy2.version())
    print("GMP ", gmpy2.mp_version())
    print("MPFR", gmpy2.mpfr_version())
    print("MPC ", gmpy2.mpc_version())
    HAVE_GMPY2 = True
except ImportError:
    print("gmpy2 not installed — run: uv sync --extra precision")
    HAVE_GMPY2 = False

# %% [markdown]
# Note that gmpy2 counts precision in **bits**, not decimal digits.
# Roughly `digits = bits × log₁₀(2) ≈ bits × 0.301`, so 34 digits needs about
# 113 bits.

# %%
if HAVE_GMPY2:
    ctx = gmpy2.get_context()
    ctx.precision = 113  # ≈ 34 decimal digits, i.e. decimal128 territory
    print("113 bits ≈", int(113 * math.log10(2)), "digits")
    print(gmpy2.sqrt(gmpy2.mpfr(2)))

    ctx.precision = 350  # ≈ 105 digits
    print()
    print(gmpy2.const_pi())
    print(gmpy2.exp(gmpy2.mpfr(1)))

# %% [markdown]
# GMP integers beat CPython's for very large values — this is the library
# CPython's own developers benchmark against:

# %%
if HAVE_GMPY2:
    py_time = timeit.timeit(lambda: math.factorial(20_000), number=5)
    gmp_time = timeit.timeit(lambda: gmpy2.fac(20_000), number=5)
    print(f"CPython int  20000!: {py_time:.4f}s")
    print(f"GMP (gmpy2)  20000!: {gmp_time:.4f}s   ({py_time / gmp_time:.1f}× faster)")

# %% [markdown]
# ## 6. `numpy.longdouble` — the last stop before software
#
# On x86 Linux this is the 80-bit x87 extended format: a 64-bit mantissa, about
# 18–19 digits. Still hardware, so still fast — but it's the end of the road, and
# it isn't portable (on ARM and Windows it's often just a plain double).

# %%
import numpy as np

info = np.finfo(np.longdouble)
print("longdouble mantissa bits:", info.nmant + 1)
print("≈ decimal digits:", int((info.nmant + 1) * math.log10(2)))
print("double mantissa bits:    ", np.finfo(np.float64).nmant + 1)
print()
print("float64:    ", np.float64(1) / np.float64(3))
print("longdouble: ", np.longdouble(1) / np.longdouble(3))

# %% [markdown]
# ## 7. SymPy: exact first, digits later
#
# The approach used everywhere else in this project. Keep the expression exact
# and symbolic, then ask for however many digits you want at the very end —
# there's no accumulated error to worry about, because no arithmetic happened
# until now.

# %%
from pymath import *  # noqa: F403

import sympy as sp

exact = sp.sqrt(2) + sp.pi
print("exact:      ", exact)
print("20 digits:  ", sp.N(exact, 20))
print("60 digits:  ", sp.N(exact, 60))

# %%
value = integrate("exp(-x^2)", lower=0, upper="oo")
print("∫₀^∞ e^(-x²) dx =", value, "=", sp.N(value, 40))

# %% [markdown]
# ## When this actually matters
#
# ### Catastrophic cancellation
#
# Subtracting two nearly-equal numbers annihilates the significant digits. Watch
# `(1 - cos x)/x²`, which should approach 0.5:

# %%
for exponent in (-2, -4, -6, -8):
    v = 10.0**exponent
    naive = (1 - math.cos(v)) / v**2
    mp.dps = 30
    good = (1 - mp.cos(mpf(10) ** exponent)) / mpf(10) ** (2 * exponent)
    print(f"x=1e{exponent:<3}  float: {naive:<22} mpmath: {mp.nstr(good, 8)}")

# %% [markdown]
# By `x = 1e-8` the float answer is **0.0** — every significant digit is gone.
# The true answer is still 0.5.
#
# ### The quadratic formula
#
# Straight from lesson 02, and it breaks the same way. For `x² + 10⁸x + 1 = 0`,
# `-b + √(b² - 4ac)` subtracts two numbers that agree to 16 digits:

# %%
a_, b_, c_ = 1.0, 1e8, 1.0
naive = (-b_ + math.sqrt(b_**2 - 4 * a_ * c_)) / (2 * a_)

mp.dps = 40
B = mpf(10) ** 8
exact_root = (-B + mp.sqrt(B**2 - 4)) / 2

print("naive float :", naive)
print("40 digits   :", mp.nstr(exact_root, 20))
print(f"relative error: {abs(naive - float(exact_root)) / abs(float(exact_root)):.1%}")

# %% [markdown]
# A 25% error from a formula every Year 12 student can write down. Two fixes:
# use more precision, or **rearrange the algebra** so the subtraction never
# happens — multiply through by the conjugate to get `2c / (-b - √(b²-4ac))`:

# %%
stable = (2 * c_) / (-b_ - math.sqrt(b_**2 - 4 * a_ * c_))
print("stable float:", stable, "← plain doubles, correct answer")

# %% [markdown]
# The second fix is better. **More precision hides a bad algorithm; it doesn't
# repair it.** Reach for the algebra first and the big-number library second.
#
# ### Money

# %%
price, qty, tax = Decimal("19.99"), 3, Decimal("0.10")
subtotal = price * qty
total = (subtotal * (1 + tax)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
print(f"exact: {subtotal} + tax = {total}")

float_total = round(19.99 * 3 * 1.10, 2)
print(f"float: {float_total}  (fine here — but the error compounds over millions of rows)")

# %% [markdown]
# ## Choosing
#
# * **Money, invoices, anything audited** → `decimal`, with an explicit rounding mode
# * **Exact algebra, no rounding at any point** → `Fraction` or SymPy
# * **Serious numeric work at high precision** → `mpmath` (+ `gmpy2` for speed)
# * **Huge integers** → `int`, or `gmpy2` when they get very large
# * **A few extra digits, still fast** → `numpy.longdouble`
# * **Symbolic, digits only at the end** → SymPy (what the rest of this project does)
#
# And before any of them: check whether the algorithm is the problem. The
# quadratic formula above needed better algebra, not better arithmetic.

# %% [markdown]
# ## Benchmark: the cost of each step up
#
# Same calculation — a square root — at each level:

# %%
mp.dps = 50
setups = [
    ("float (hardware)", lambda: math.sqrt(2)),
    ("numpy longdouble", lambda: np.sqrt(np.longdouble(2))),
    ("decimal, 34 digits", lambda: Decimal(2).sqrt()),
    ("mpmath, 50 digits", lambda: mp.sqrt(2)),
]
if HAVE_GMPY2:
    gmpy2.get_context().precision = 166  # ≈ 50 digits
    setups.append(("gmpy2/MPFR, 50 digits", lambda: gmpy2.sqrt(gmpy2.mpfr(2))))

getcontext().prec = 34
baseline = None
for name, fn in setups:
    elapsed = timeit.timeit(fn, number=100_000)
    baseline = baseline or elapsed
    print(f"{name:24} {elapsed:.4f}s   {elapsed / baseline:6.1f}× hardware float")

# %% [markdown]
# Hardware floats win by one to two orders of magnitude — which is exactly why
# they're the default, and why you should reach for these libraries only where
# the precision genuinely earns its cost.
