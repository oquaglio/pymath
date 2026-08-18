"""Matrices and linear algebra — the ClassWiz Matrix and Vector modes.

SymPy matrices for exact work, NumPy for large or numeric problems.
"""

from __future__ import annotations

import numpy as np
import sympy as sp


def matrix(rows) -> sp.Matrix:
    """Build an exact matrix from a list of rows.

    >>> matrix([[1, 2], [3, 4]])
    Matrix([
    [1, 2],
    [3, 4]])
    """
    return sp.Matrix([[sp.nsimplify(v) for v in row] for row in rows])


def determinant(m):
    """Determinant. Zero means the matrix is singular (no inverse).

    >>> determinant([[1, 2], [3, 4]])
    -2
    """
    return sp.simplify(sp.Matrix(m).det())


def inverse(m) -> sp.Matrix:
    """Matrix inverse, exactly. Raises if the determinant is zero."""
    mm = sp.Matrix(m)
    if mm.det() == 0:
        raise ValueError("matrix is singular (determinant 0), so it has no inverse")
    return sp.simplify(mm.inv())


def solve_linear(coefficients, constants) -> sp.Matrix:
    """Solve ``Ax = b`` — simultaneous equations in matrix form.

    >>> solve_linear([[2, 1], [1, -1]], [5, 1]).T
    Matrix([[2, 1]])
    """
    A = sp.Matrix(coefficients)
    b = sp.Matrix(constants)
    if A.det() != 0:
        return sp.simplify(A.solve(b))
    return sp.simplify(A.gauss_jordan_solve(b)[0])  # under/over-determined


def rref(m) -> dict:
    """Row-reduced echelon form, plus the pivot columns and rank.

    Reducing the augmented matrix is Gaussian elimination done for you.
    """
    reduced, pivots = sp.Matrix(m).rref()
    return {"rref": reduced, "pivots": pivots, "rank": len(pivots)}


def eigen(m) -> dict:
    """Eigenvalues, eigenvectors and diagonalisation.

    An eigenvector is a direction the matrix only stretches; the eigenvalue is
    the stretch factor.

    >>> eigen([[2, 0], [0, 3]])["eigenvalues"]
    {2: 1, 3: 1}
    """
    mm = sp.Matrix(m)
    result = {
        "eigenvalues": mm.eigenvals(),  # {value: multiplicity}
        "eigenvectors": mm.eigenvects(),  # [(value, multiplicity, [vectors])]
        "characteristic_polynomial": mm.charpoly().as_expr(),
        "trace": mm.trace(),
        "determinant": mm.det(),
    }
    try:
        P, D = mm.diagonalize()
        result["P"], result["D"] = P, D  # m == P * D * P^-1
    except sp.MatrixError:
        result["P"] = result["D"] = None
    return result


def transform_2d(kind: str, **params) -> sp.Matrix:
    """Standard 2D transformation matrices.

    Kinds: rotation(angle in degrees), reflection(axis="x"|"y"|"y=x"),
    scale(sx, sy), shear(kx, ky).

    >>> transform_2d("rotation", angle=90)
    Matrix([
    [0, -1],
    [1,  0]])
    """
    match kind:
        case "rotation":
            th = sp.rad(sp.nsimplify(params["angle"]))
            return sp.Matrix([[sp.cos(th), -sp.sin(th)], [sp.sin(th), sp.cos(th)]])
        case "reflection":
            axis = params.get("axis", "x")
            table = {
                "x": [[1, 0], [0, -1]],
                "y": [[-1, 0], [0, 1]],
                "y=x": [[0, 1], [1, 0]],
                "y=-x": [[0, -1], [-1, 0]],
            }
            return sp.Matrix(table[axis])
        case "scale":
            return sp.diag(sp.nsimplify(params.get("sx", 1)), sp.nsimplify(params.get("sy", 1)))
        case "shear":
            return sp.Matrix([[1, sp.nsimplify(params.get("kx", 0))],
                              [sp.nsimplify(params.get("ky", 0)), 1]])
        case _:
            raise ValueError(f"unknown transformation: {kind}")


def numeric(m) -> np.ndarray:
    """Convert to a NumPy array — needed for big or floating-point problems.

    >>> numeric([[1, 2], [3, 4]]).shape
    (2, 2)
    """
    return np.array(sp.Matrix(m).tolist(), dtype=float)


def lstsq(A, b) -> np.ndarray:
    """Least-squares solution of an over-determined system (more rows than unknowns).

    This is what linear regression is under the hood.
    """
    return np.linalg.lstsq(numeric(A), np.asarray(b, dtype=float), rcond=None)[0]


__all__ = [
    "determinant",
    "eigen",
    "inverse",
    "lstsq",
    "matrix",
    "numeric",
    "rref",
    "solve_linear",
    "transform_2d",
]
