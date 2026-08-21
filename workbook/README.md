# Workbook

Your working. `lessons/` is reference material to read; this is where you do the
maths yourself.

## Starting a new problem set

```bash
cp workbook/_template.py workbook/calculus/quotient-rule.py
just workbook          # opens Jupyter Lab here
```

In Jupyter, right-click the `.py` → **Open With → Notebook**. Work in the
notebook; jupytext keeps the `.py` in sync automatically. Commit the `.py`, not
the `.ipynb` — the notebook is generated and gitignored, so your history stays
readable.

Name files by topic, not number. You'll jump around, and numbering fights you
when you do.

## The rule

**Write your working in the markdown cell before you run the verify cell.**

That's the whole discipline. A CAS sitting next to you makes it very easy to
call `solve()` and absorb nothing, so each problem is four cells in a fixed
order:

1. the question, and your working, in markdown — *written first*
2. your answer, as an expression
3. the check
4. a one-line verdict

Check with `simplify(mine - theirs) == 0`, never `==`. SymPy writes the same
expression several different ways and `==` fails on cosmetic differences —
`x*(x + 4)` and `x**2 + 4*x` are the same maths and unequal objects.

## mistakes.md

One line per error, **grouped by cause, not by topic**. Maths errors are
shockingly repetitive. After a month you'll find most of yours are three or four
recurring slips, and you can't see that pattern without writing it down.

The point isn't the log, it's the grouping.
