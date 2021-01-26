from pathlib import Path
from pprint import pprint

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from util import load_data, complete_df_out

here = Path(__file__).absolute().parent

dir_saved = here / "saved"

nb_particles_short = "16k"

paths_h5 = sorted(dir_saved.glob(f"{nb_particles_short}_*.h5"))
pprint(paths_h5)

path_h5 = paths_h5[0]

info, df = load_data(path_h5)
# print(df)

t_end = info["t_end"]

columns = [
    "implementation",
    "language",
    "elapsed_time",
    "consommation",
    "power",
]

df_out = df.loc[:, columns].groupby(["implementation", "language"]).mean()
df_out.drop("sleep(t_sleep_before)", inplace=True)

complete_df_out(df_out, info)
print(df_out)

# elapsed_max = df["elapsed_time"].max()

# df_out["consommation_core"] = df_out["consommation"] - df_out[
#     "elapsed_time"
# ] * info["power_sleep_1core"] * (info["nb_cores"] - 1)


# df_out["consommation_alt"] = (
#     df_out["consommation"]
#     + (elapsed_max - df_out["elapsed_time"]) * info["power_sleep"]
# )

# df_out["CO2"] = (10 / t_end) * compute_CO2_mass(df_out["consommation"])
# df_out["CO2_alt"] = (10 / t_end) * compute_CO2_mass(df_out["consommation_alt"])
# df_out["CO2_core"] = (10 / t_end) * compute_CO2_mass(df_out["consommation_core"])
# # in days
# df_out.elapsed_time *= 10 / t_end / (24 * 3600)

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
    elif name.startswith("Pypy"):
        name = name.replace("Pypy", "PyPy")

    factor_time = -0.008
    factor_cons = 0.005

    if nb_particles_short == "16k":
        if "2021-01-24_09-14-08" in path_h5.name:
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
        elif "2021-01-25_14-08-35" in path_h5.name:
            if name == "Pythran\n naive":
                factor_time = -0.01
                factor_cons = -0.020

            elif name == "Numba":
                factor_time = -0.024
                factor_cons = -0.003

            elif name.startswith("Fortran"):
                factor_time = 0.004
                factor_cons = -0.007

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
    _.set_xlabel("Elapsed time (day)")
    _.set_title(f"{nb_particles_short} particles, 10 N-Body time units")
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
            label="Static languages",
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
