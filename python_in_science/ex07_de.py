from pathlib import Path

import numpy as np
import scienceplots
from matplotlib import pyplot as plt
from scipy.integrate import odeint

plt.style.use(["science", "ieee"])


def sir(y, t, beta, gamma):
    S, I, R = y
    dS_dt = -beta * S * I
    dI_dt = beta * S * I - gamma * I
    dR_dt = gamma * I
    return [dS_dt, dI_dt, dR_dt]


N = 1
I0 = 0.01
S0 = N - I0
R0 = 0
y0 = [S0, I0, R0]

params = [(0.3, 0.01), (0.3, 0.1), (0.3, 1.0)]

time = np.linspace(0, 100, 1000)
sols = [odeint(sir, y0, time, args=(beta, gamma)) for beta, gamma in params]

fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(15, 5))

for ax, sol, (beta, gamma) in zip(axs, sols, params):
    S, I, R = sol.T

    ax.plot(time, S, label="Susceptible")
    ax.plot(time, I, label="Infected")
    ax.plot(time, R, label="Recovered")

    ax.set_title(f"$\\beta={beta}$, $\\gamma={gamma}$")
    ax.set_xlabel("Time")
    ax.set_ylabel("Population Proportion")
    ax.legend()

plt.tight_layout()
plt.savefig(Path(__file__).stem + ".pdf")
# plt.show()
