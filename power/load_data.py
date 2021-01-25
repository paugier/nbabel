from pathlib import Path

import numpy as np
import pandas as pd
import h5py
from scipy.integrate import trapz

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

here = Path(__file__).absolute().parent

dir_saved = here / "saved"

nb_particles_short = "1k"

paths_h5 = sorted(dir_saved.glob(f"{nb_particles_short}_*.h5"))

path_h5 = paths_h5[-1]

path_csv = path_h5.with_suffix(".csv")

assert path_csv.exists()
assert path_h5.exists()

df = pd.read_csv(path_csv)

with h5py.File(path_h5) as file:
    t_end = file.attrs["t_end"]
    node = file.attrs["node"]
    nb_particles_short = file.attrs["nb_particles_short"]
    time_julia_bench = file.attrs["time_julia_bench"]
    t_sleep_before = file.attrs["t_sleep_before"]

    times = file["times"][:]
    watts = file["watts"][:]

power_sleep = np.percentile(watts, 5)
nb_cores = 12
power_sleep_1core = power_sleep / nb_cores

# fig, ax0 = plt.subplots()
# ax0.plot(times, watts)

consommations = np.empty(df.shape[0])

deltat = 0.2
for index, row in df.iterrows():

    cond = (times > row.timestamp_start - deltat) & (
        times < row.timestamp_end + deltat
    )

    # ax0.vlines(row.timestamp_start, 0, 250, colors="g")
    # ax0.vlines(row.timestamp_end, 0, 250, colors="r")

    times_run = times[cond]
    watts_run = watts[cond]

    # fig, ax0 = plt.subplots()
    # ax0.plot(times_run, watts_run)
    # ax0.set_title(row.implementation)

    consommations[index] = trapz(watts_run, times_run)  # in J


df["consommation"] = consommations
df["power"] = df["consommation"] / df["elapsed_time"]

# print(df)

columns = [
    "implementation",
    "language",
    "elapsed_time",
    "consommation",
    "power",
]

df_out = df.loc[:, columns].groupby(["implementation", "language"]).mean()
df_out.drop("sleep(t_sleep_before)", inplace=True)

print(df_out)

elapsed_max = df["elapsed_time"].max()

df_out["consommation_core"] = df_out["consommation"] - df_out[
    "elapsed_time"
] * power_sleep_1core * (nb_cores - 1)


df_out["consommation_alt"] = (
    df_out["consommation"] + (elapsed_max - df_out["elapsed_time"]) * power_sleep
)


def compute_CO2_mass(consommation):
    """
    kWh = 3.6e6 J
    0.283 kWh -> 1 kg

    Also takes into account difference in t_end
    """
    return consommation / 3.6 / 0.283 * 1e-6 * (10 / t_end)


df_out["CO2"] = compute_CO2_mass(df_out["consommation"])
df_out["CO2_alt"] = compute_CO2_mass(df_out["consommation_alt"])
df_out["CO2_core"] = compute_CO2_mass(df_out["consommation_core"])


fig, ax0 = plt.subplots()
fig, ax1 = plt.subplots()
fig, ax2 = plt.subplots()

axes = [ax0, ax1, ax2]
quantities = ["CO2", "CO2_core", "CO2_alt"]

for index, row in df_out.iterrows():
    implementation, language = row.name

    if language == "py":
        color = "r"
    elif language in ("cpp", "fortran"):
        color = "g"
    elif language == "julia":
        color = "b"
    else:
        color = "y"

    if (
        language == "julia"
        or "jit" in implementation
        or "pypy" in implementation
        or "numba" in implementation
    ):
        marker = "o"
        markersize = "8"
    else:
        marker = "*"
        markersize = "10"

    for ax, quantity in zip(axes, quantities):
        ax.plot(
            row.elapsed_time,
            row[quantity],
            marker=marker,
            color=color,
            markersize=markersize,
        )

x_ratios = []
y_ratios = []
for ax in axes:
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    x_ratios.append(xmax / xmin)
    y_ratios.append(ymax / ymin)

for index, row in df_out.iterrows():

    name = row.name[0].capitalize()
    if name.endswith("Pythran high-level jit"):
        name = "Pythran\n naive"
    elif name == "Pypy":
        name = "PyPy"

    factor_time = -0.008
    factor_cons = 0.005

    if nb_particles_short == "16k":
        if name == "PyPy":
            factor_cons = -0.003
            factor_time = -0.018

        elif name == "Pythran\n naive":
            factor_time = -0.01
            factor_cons = -0.020

        elif name.startswith("Fortran"):
            factor_cons = -0.01

        elif name.startswith("Julia nbabel"):
            factor_time = 0.005
            factor_cons = -0.004

    elif nb_particles_short == "1k":

        if name == "Numba":
            factor_time = 0.006
            factor_cons = -0.006

        if name == "Pythran\n naive":
            factor_time = -0.01
            factor_cons = -0.022

    for iax, (ax, quantity) in enumerate(zip(axes, quantities)):
        ax.text(
            row.elapsed_time * (1 + factor_time * x_ratios[iax]),
            row[quantity] * (1 + factor_cons * y_ratios[iax]),
            name,
        )


ax0.set_ylabel("Production CO$_2$ full node during run (kg)")
ax1.set_ylabel("Production CO$_2$ used core(s) during run (kg)")
ax2.set_ylabel("Production CO$_2$ full node during time slowest run (kg)")

for _ in (ax0, ax1, ax2):
    _.set_xscale("log")
    _.set_yscale("log")
    _.set_xlabel("Elapsed time (s)")
    _.figure.tight_layout()


ax0.legend(
    handles=[
        Line2D(
            [0],
            [0],
            color="w",
            markerfacecolor="r",
            marker="s",
            markersize=8,
            label="Python",
        ),
        Line2D(
            [0],
            [0],
            color="w",
            marker="o",
            markerfacecolor="b",
            markeredgecolor="b",
            markersize=8,
            label="Julia",
        ),
        Line2D(
            [0],
            [0],
            color="w",
            marker="*",
            markerfacecolor="g",
            markeredgecolor="g",
            markersize=10,
            label="C++ & Fortran",
        ),
        Line2D(
            [0],
            [0],
            color="w",
            marker="o",
            markerfacecolor="w",
            markeredgecolor="k",
            markersize=8,
            label="JIT compilation",
        ),
        Line2D(
            [0],
            [0],
            color="w",
            marker="*",
            markerfacecolor="w",
            markeredgecolor="k",
            markersize=10,
            label="AOT compilation",
        ),
    ]
)

# plt.close(ax0.figure)
plt.close(ax1.figure)
plt.close(ax2.figure)


plt.show()
