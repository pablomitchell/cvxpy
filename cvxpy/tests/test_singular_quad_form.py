from __future__ import division, print_function, absolute_import

import numpy as np
from numpy.testing import assert_allclose, assert_equal
from scipy import linalg
import cvxpy

def test_singular_quad_form():
    # Solve a quadratic program.
    np.random.seed(1234)
    for n in (3, 4, 5):
        for i in range(5):

            # construct a random 1d finite distribution
            v = np.exp(np.random.randn(n))
            v = v / np.sum(v)

            # construct a random positive definite matrix
            A = np.random.randn(n, n)
            Q = np.dot(A, A.T)

            # Project onto the orthogonal complement of v.
            # This turns Q into a singular matrix with a known nullspace.
            E = np.identity(n) - np.outer(v, v) / np.inner(v, v)
            Q = np.dot(E, np.dot(Q, E.T))
            observed_rank = np.linalg.matrix_rank(Q)
            desired_rank = n-1
            yield assert_equal, observed_rank, desired_rank

            for action in 'minimize', 'maximize':

                # Look for the extremum of the quadratic form
                # under the simplex constraint.
                x = cvxpy.Variable(n)
                if action == 'minimize':
                    q = cvxpy.quad_form(x, Q)
                    objective = cvxpy.Minimize(q)
                elif action == 'maximize':
                    q = cvxpy.quad_form(x, -Q)
                    objective = cvxpy.Maximize(q)
                constraints = [0 <= x, sum(x) == 1]
                p = cvxpy.Problem(objective, constraints)
                p.solve()

                # check that cvxpy found the right answer
                xopt = x.value.A.flatten()
                yopt = np.dot(xopt, np.dot(Q, xopt))
                assert_allclose(yopt, 0, atol=1e-3)
                assert_allclose(xopt, v, atol=1e-3)
