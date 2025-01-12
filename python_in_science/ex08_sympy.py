from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

m, t, omega, omega0 = sp.symbols("m t omega omega0", positive=True, real=True)
gamma, F0 = sp.symbols("gamma F0", real=True)

x = sp.Function("x")(t)

# x'' + 2 * gamma * omega0 * x' + omega0^2 * x = 0
damped_eq = sp.Eq(
    x.diff(t, t) + 2 * gamma * x.diff(t) + omega0 * omega0 * x,
    0,
)
sp.pprint(damped_eq)
sp.pprint(sp.dsolve(damped_eq, x))

# x'' + omega0 * omega0 * x = 1/m * F0 * cos(omega * t)
forced_eq = sp.Eq(
    x.diff(t, t) + omega0 * omega0 * x,
    F0 * sp.cos(omega * t) / m,
)
sp.pprint(forced_eq)
sp.pprint(sp.dsolve(forced_eq, x))

# x'' + 2 * gamma * x' + omega0^2 * x = F0/m * cos(omega * t)
damped_forced_eq = sp.Eq(
    x.diff(t, t) + 2 * gamma * x.diff(t) + omega0 * omega0 * x,
    F0 * sp.cos(omega * t) / m,
)
sp.pprint(damped_forced_eq)
damped_forced_sol = sp.dsolve(
    damped_forced_eq, x, ics={x.subs(t, 0): 1, x.diff(t).subs(t, 0): 0}
)
sp.pprint(damped_forced_sol)

ics = {x.subs(t, 0): 1, x.diff(t).subs(t, 0): 0}
consts = {m: 1, omega0: 0.9, F0: 2}

damped_func = [
    (
        gamma_val,
        sp.lambdify(
            t,
            sp.dsolve(damped_eq, x, ics=ics).subs(consts).subs({gamma: gamma_val}).rhs,
            "numpy",
        ),
    )
    for gamma_val in [0.5, 0.25, 0.1]
]

forced_func = [
    (
        omega_val,
        sp.lambdify(
            t,
            sp.dsolve(forced_eq, x, ics=ics).subs(consts).subs({omega: omega_val}).rhs,
            "numpy",
        ),
    )
    for omega_val in [1.0, 1.5, 2.0]
]

damped_forced_func = [
    (
        (gamma_val, omega_val),
        sp.lambdify(
            t,
            damped_forced_sol.subs(consts)
            .subs({gamma: gamma_val, omega: omega_val})
            .rhs,
            "numpy",
        ),
    )
    for gamma_val, omega_val in [(0.5, 1.0), (0.25, 1.5), (0.1, 2.0)]
]

fig, [ax_d, ax_f, ax_df] = plt.subplots(nrows=3, figsize=(8, 12))
time = np.linspace(0, 20, 1000)

ax_d.set_title("Damped Harmonic Oscillator")
ax_d.set_xlabel("Time (t)")
ax_d.set_ylabel("Displacement (x)")

for gamma_val, func in damped_func:
    ax_d.plot(time, func(time), label=f"$\\gamma = {gamma_val}$")

ax_d.legend()
ax_d.grid()

ax_f.set_title("Forced Harmonic Oscillator")
ax_f.set_xlabel("Time (t)")
ax_f.set_ylabel("Displacement (x)")

for omega_val, func in forced_func:
    ax_f.plot(time, func(time), label=f"$\\omega = {omega_val}$")

ax_f.legend()
ax_f.grid()

ax_df.set_title("Damped + Forced Harmonic Oscillator")
ax_df.set_xlabel("Time (t)")
ax_df.set_ylabel("Displacement (x)")

for (gamma_val, omega_val), func in damped_forced_func:
    ax_df.plot(
        time,
        func(time),
        label=f"$\\gamma = {gamma_val}, \\omega = {omega_val}$",
    )

ax_df.legend()
ax_df.grid()

fig.tight_layout()
fig.savefig(Path(__file__).with_suffix(".pdf"))
# plt.show()
