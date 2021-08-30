"""
Dedalus script computing the eigenmodes of waves on a clamped string.
This script demonstrates solving a 1D eigenvalue problem and produces
a plot of the relative error of the eigenvalues.  It should be ran serially
and take just a few seconds to complete.

We use a Chebyshev basis to solve the EVP:
    s*u + dx(dx(u)) = 0
where s is the eigenvalue.
"""

import numpy as np
import matplotlib.pyplot as plt
import dedalus.public as d3
import logging
logger = logging.getLogger(__name__)


# Parameters
Nx = 128
Lx = 1
dtype = np.complex128

# Bases
xcoord = d3.Coordinate('x')
dist = d3.Distributor(xcoord, dtype=dtype)
xbasis = d3.Chebyshev(xcoord, size=Nx, bounds=(0, Lx))

# Fields
u = dist.Field(name='u', bases=xbasis)
tau1 = dist.Field(name='tau1')
tau2 = dist.Field(name='tau2')
s = dist.Field(name='s')

# Substitutions
dx = lambda A: d3.Differentiate(A, xcoord)
lift = lambda A, n: d3.LiftTau(A, xbasis.clone_with(a=1/2, b=1/2), n)
ux = dx(u) + lift(tau1, -1) # First-order reduction

# Problem
problem = d3.EVP(variables=[u, tau1, tau2], eigenvalue=s)
problem.add_equation((s*u + dx(ux) + lift(tau2,-1), 0))
problem.add_equation((u(x=0), 0))
problem.add_equation((u(x=Lx), 0))

# Solve
solver = problem.build_solver()
solver.solve_dense(solver.subproblems[0])
evals = np.sort(solver.eigenvalues)
n = 1 + np.arange(evals.size)
true_evals = (n * np.pi / Lx)**2
relative_error = np.abs(evals - true_evals) / true_evals

# Plot
plt.figure(figsize=(6, 4))
plt.semilogy(n, relative_error, '.')
plt.xlabel("eigenvalue number")
plt.ylabel("relative eigenvalue error")
plt.tight_layout()
plt.savefig('eigenvalue_error.pdf')