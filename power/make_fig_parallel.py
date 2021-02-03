from pathlib import Path
from pprint import pprint

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from util import load_data, complete_df_out, dir_saved



nb_particles_short = "16k"

language = "julia"

paths_h5 = sorted(
    dir_saved.glob(f"parallel_{language}_{nb_particles_short}_*.h5"),
    key=lambda p: p.name.split("grid5000")[-1],
)
pprint(paths_h5)

path_h5 = paths_h5[-1]

info, df = load_data(path_h5)
pprint(info)
# print(df)

t_end = info["t_end"]

df = df[df.implementation != "sleep(t_sleep_before)"]

columns = [
    "implementation",
    "language",
    "nb_threads",
    "elapsed_time",
    "consommation",
    "power_mean",
]

df_out = df.loc[:, columns].groupby(["nb_threads"]).mean()
complete_df_out(df_out, info)

print(df_out)


def set_ylim_twin(ax):
    y0, y1 = ax.get_ylim()
    ax_twin = ax.ax_twin
    norm = ax.ax_twin_norm
    ax_twin.set_ylim(100 * y0 / norm, 100 * y1 / norm)
    ax_twin.figure.canvas.draw()
    ax_twin.yaxis.set_major_formatter(mtick.PercentFormatter())


fig, (ax0, ax1) = plt.subplots(2, 1, sharex=True)

nb_threads_list = df_out.index

ax0.plot(nb_threads_list, df_out.elapsed_time, marker=".")

ax0.plot(nb_threads_list, df_out.elapsed_time.max() / nb_threads_list, "k:")


ax0.ax_twin = ax0.twinx()
ax0.ax_twin_norm = df_out.elapsed_time.max()
ax0.callbacks.connect("ylim_changed", set_ylim_twin)


ax1.plot(nb_threads_list, df_out.CO2, marker=".", label="CO$_2$ during run")
ax1.plot(
    nb_threads_list,
    df_out.CO2_alt,
    marker=".",
    label="CO$_2$ during time longer run",
)
ax1.plot(nb_threads_list, df_out.CO2.max() / nb_threads_list, "k:")

ax1.ax_twin = ax1.twinx()
ax1.ax_twin_norm = df_out.CO2.max()
ax1.callbacks.connect("ylim_changed", set_ylim_twin)

ax0.set_ylabel("Elapsed time (day)")

for ax in (ax0, ax1):
    ax.set_ylim(ymin=0)
    ax.set_xlim(xmax=16)

ax0.set_ylim(ymax=0.33)
ax1.set_ylim(ymax=3.8)

ax1.set_xlabel("number of threads")
ax1.set_ylabel("Production CO$_2$ (kg)")
ax1.legend()
ax0.set_title(f"{info['nb_particles_short']} particles, 10 N-Body time units ({language.capitalize()})")
fig.tight_layout()

plt.show()