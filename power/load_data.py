from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import h5py
from scipy.integrate import trapz

here = Path(__file__).absolute().parent

dir_saved = here / "saved"

paths_csv = sorted(dir_saved.glob("*.csv"))

path_csv = paths_csv[0]

path_h5 = path_csv.with_suffix(".h5")

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
nb_cores = 32

# fig, ax = plt.subplots()
# ax.plot(times, watts)

consommations = np.empty(df.shape[0])

deltat = 0.2
for index, row in df.iterrows():

    cond = (times > row.timestamp_start - deltat) & (
        times < row.timestamp_end + deltat
    )

    # ax.vlines(row.timestamp_start, 0, 250, colors="g")
    # ax.vlines(row.timestamp_end, 0, 250, colors="r")

    times_run = times[cond]
    watts_run = watts[cond]

    # fig, ax0 = plt.subplots()
    # ax0.plot(times_run, watts_run)
    # ax0.set_title(row.implementation)

    consommations[index] = trapz(watts_run, times_run)  # in J


df["consommation"] = consommations
df["power"] = df["consommation"] / df["elapsed_time"]

df["consommation_core"] = (
    consommations - df["elapsed_time"] * power_sleep * (nb_cores - 1) / nb_cores
)

print(df)

columns = [
    "implementation",
    "language",
    "elapsed_time",
    "consommation",
    "power",
    "consommation_core",
]

df_out = df.loc[:, columns].groupby(["implementation", "language"]).mean()
df_out.drop("sleep(t_sleep_before)", inplace=True)

print(df_out)


def compute_CO2_mass(consommation):
    """
    kWh = 3.6e6 J
    0.283 kWh -> 1 kg

    Also takes into account difference in t_end
    """
    return consommation / 3.6 / 0.283 * 1e-6 * (10 / t_end)


df_out["CO2"] = compute_CO2_mass(df_out["consommation"])
df_out["CO2_core"] = compute_CO2_mass(df_out["consommation_core"])


fig, ax = plt.subplots()
fig, ax1 = plt.subplots()

for index, row in df_out.iterrows():

    marker = "o"
    color = "b"
    if row.name[1] == "py":
        marker = "s"
        color = "r"
    elif row.name[1] in ("cpp", "fortran"):
        color = "g"

    factor_time = 0.93
    factor_cons = 1.03

    name = row.name[0].capitalize()
    if name.endswith("Pythran high-level jit"):
        name = "Pythran\n naive"
    elif name == "Pypy":
        name = "PyPy"

    if name == "Numba":
        factor_cons = 0.94
    elif name == "Pythran\n naive":
        factor_cons = 0.85

    ax.plot(row.elapsed_time, row.CO2, marker=marker, color=color)
    ax.text(factor_time * row.elapsed_time, factor_cons * row.CO2, name)

    ax1.plot(row.elapsed_time, row.CO2_core, marker=marker, color=color)
    ax1.text(factor_time * row.elapsed_time, factor_cons * row.CO2_core, name)

ax.set_ylabel("Production CO2 full node during run (kg)")
ax1.set_ylabel("Production CO2 used core(s) during run (kg)")

for _ in (ax, ax1):
    _.set_xscale("log")
    _.set_yscale("log")
    _.set_xlabel("Elapsed time (s)")
    _.figure.tight_layout()


# for index, row in df_out.iterrows():

#     marker = "o"
#     color = "b"
#     if row.name[1] == "py":
#         marker = "s"
#         color = "r"


#     factor_time = 0.93
#     factor_cons = 1.03

#     name = row.name[0].capitalize()
#     if name.endswith("Pythran high-level jit"):
#         name = "Pythran\n naive"
#     elif name == "Pypy":
#         name = "PyPy"

#     if name == "Numba":
#         factor_cons = 0.94
#     elif name == "Pythran\n naive":
#         factor_cons = 0.85


# ax.set_xscale("log")
# ax.set_yscale("log")

# ax.set_xlabel("Elapsed time (s)")
# ax.figure.tight_layout()


plt.show()