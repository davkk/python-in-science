import numpy as np
from bokeh.io import curdoc, show
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from scipy.integrate import odeint


def sir(y, t, beta, gamma):
    S, I, R = y
    dS_dt = -beta * S * I
    dI_dt = beta * S * I - gamma * I
    dR_dt = gamma * I
    return [dS_dt, dI_dt, dR_dt]


N = 1.0
I0 = 0.01
S0 = N - I0
R0 = 0.0
y0 = [S0, I0, R0]

t = np.linspace(0, 100, 1000)

source = ColumnDataSource(data=dict(t=[], S=[], I=[], R=[]))

p = figure(
    width=1280,
    height=720,
    title="SIR Model Simulation",
    x_axis_label="Time",
    y_axis_label="Population Proportion",
)

p.line(
    "t",
    "S",
    line_color="blue",
    line_width=2,
    legend_label="Susceptible",
    source=source,
)
p.line(
    "t",
    "I",
    line_color="red",
    line_width=2,
    legend_label="Infected",
    source=source,
)
p.line(
    "t",
    "R",
    line_color="green",
    line_width=2,
    legend_label="Recovered",
    source=source,
)

beta_slider = Slider(
    title=r"$$\beta$$ (Infection Rate)",
    value=0.3,
    start=0.1,
    end=1.0,
    step=0.01,
)

gamma_slider = Slider(
    title=r"$$\gamma$$ (Recovery Rate)",
    value=0.1,
    start=0.01,
    end=0.5,
    step=0.01,
)


def update_data(attrname, old, new):
    beta = beta_slider.value
    gamma = gamma_slider.value

    solution = odeint(sir, y0, t, args=(beta, gamma))
    S, I, R = solution.T

    source.data = dict(t=t, S=S, I=I, R=R)


beta_slider.on_change("value", update_data)
gamma_slider.on_change("value", update_data)
update_data("value", None, None)

inputs = column(beta_slider, gamma_slider)
layout = column(row(inputs, p))

curdoc().add_root(layout)
show(layout)
