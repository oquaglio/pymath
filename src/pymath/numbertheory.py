"""Number work: primes, factors, fractions, bases, modular arithmetic.

The ClassWiz "Base-N" mode plus the number-theory tools that turn up in
extension maths and in programming interviews.
"""

from __future__ import annotations

import sympy as sp


def factorise_int(value: int) -> dict:
    """Prime factorisation and everything that follows from it.

    >>> factorise_int(360)["prime_factors"]
    {2: 3, 3: 2, 5: 1}
    """
    v = int(value)
    factors = sp.factorint(v)
    return {
        "prime_factors": factors,  # {prime: exponent}
        "written": " × ".join(f"{p}^{e}" if e > 1 else str(p) for p, e in factors.items()),
        "divisors": sp.divisors(v),
        "divisor_count": sp.divisor_count(v),
        "is_prime": sp.isprime(v),
    }


def gcd(*values: int) -> int:
    """Greatest common divisor.

    >>> gcd(12, 18, 24)
    6
    """
    return int(sp.igcd(*[int(v) for v in values]))


def lcm(*values: int) -> int:
    """Lowest common multiple.

    >>> lcm(4, 6)
    12
    """
    return int(sp.ilcm(*[int(v) for v in values]))


def primes_up_to(limit: int) -> list[int]:
    """All primes below a limit (sieve).

    >>> primes_up_to(20)
    [2, 3, 5, 7, 11, 13, 17, 19]
    """
    return list(sp.primerange(2, limit))


def nth_prime(index: int) -> int:
    """The nth prime, 1-indexed.

    >>> nth_prime(10)
    29
    """
    return int(sp.prime(index))


def fraction(value, max_denominator: int = 10**6) -> dict:
    """Turn a decimal into an exact fraction, with its mixed-number form.

    >>> fraction(0.375)["fraction"]
    3/8
    """
    exact = sp.nsimplify(value, rational=True).limit_denominator(max_denominator)
    whole = int(exact)
    return {
        "fraction": exact,
        "numerator": sp.numer(exact),
        "denominator": sp.denom(exact),
        "mixed": (whole, sp.simplify(exact - whole)),
        "decimal": float(exact),
        "recurring": sp.denom(exact) not in (1, 2, 4, 5, 8, 10, 16, 20, 25, 32, 40, 50),
    }


def to_base(value: int, base: int) -> str:
    """Convert an integer to another base (2-36).

    >>> to_base(255, 16)
    'ff'
    """
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    v, sign = abs(int(value)), "-" if value < 0 else ""
    if v == 0:
        return "0"
    out = []
    while v:
        v, rem = divmod(v, base)
        out.append(digits[rem])
    return sign + "".join(reversed(out))


def from_base(text: str, base: int) -> int:
    """Read a string in the given base back to an integer.

    >>> from_base("ff", 16)
    255
    """
    return int(str(text), base)


def mod_inverse(value: int, modulus: int) -> int:
    """The x with ``value·x ≡ 1 (mod modulus)``. Exists only when they're coprime.

    >>> mod_inverse(3, 11)
    4
    """
    return int(sp.mod_inverse(int(value), int(modulus)))


def modular(expr_value: int, modulus: int) -> int:
    """Least non-negative residue.

    >>> modular(-7, 3)
    2
    """
    return int(expr_value) % int(modulus)


def continued_fraction(value, depth: int = 10) -> list[int]:
    """Continued-fraction expansion — how good rational approximations are found.

    >>> continued_fraction(sp.pi, 4)
    [3, 7, 15, 1]
    """
    from sympy.ntheory.continued_fraction import continued_fraction_iterator

    it = continued_fraction_iterator(sp.nsimplify(value))
    return [int(next(it)) for _ in range(depth)]


def is_perfect_square(value: int) -> bool:
    """Is this integer a perfect square?

    >>> is_perfect_square(144)
    True
    >>> is_perfect_square(145)
    False
    """
    root = sp.integer_nthroot(int(value), 2)
    return bool(root[1])


def surd(expr: str | sp.Expr) -> sp.Expr:
    """Simplify a surd, rationalising any denominator.

    >>> surd("1/sqrt(2)")
    sqrt(2)/2
    """
    from .symbols import sym

    return sp.radsimp(sp.sqrtdenest(sp.simplify(sym(expr))))


__all__ = [
    "continued_fraction",
    "factorise_int",
    "fraction",
    "from_base",
    "gcd",
    "is_perfect_square",
    "lcm",
    "mod_inverse",
    "modular",
    "nth_prime",
    "primes_up_to",
    "surd",
    "to_base",
]
