import numpy as np
import matplotlib.pyplot as plt

from util import (
    load_data,
    complete_df_out,
    dir_saved,
    color_Python,
    color_Julia,
    nb_particles_dict,
)

nb_particles_short = "16k"


def get_result_parallel(filename):

    path_h5 = dir_saved / filename
    info, df = load_data(path_h5)
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

    return df_out


df_pythran = get_result_parallel(
    "parallel_pythran_16k_taurus-15.lyon.grid5000.fr_2021-02-06_23-12-07.h5"
    # "parallel_pythran_16k_taurus-5.lyon.grid5000.fr_2021-01-27_15-13-06.h5"
)
df_julia = get_result_parallel(
    "parallel_julia_16k_taurus-15.lyon.grid5000.fr_2021-02-06_23-45-53.h5"
    # "parallel_julia_16k_taurus-11.lyon.grid5000.fr_2021-01-26_21-20-37.h5"
)


fig, ax = plt.subplots()


def plot(df, color, marker, markersize):
    ax.plot(
        df.elapsed_time,
        df.CO2_core,
        "-",
        color=color,
        marker=marker,
        markersize=markersize,
        markeredgecolor="k",
    )


plot(df_pythran, color=color_Python, marker="*", markersize="10")

plot(df_julia, color=color_Julia, marker="o", markersize="8")

ax.set_xscale("log")
ax.set_yscale("log")

ax.set_xlabel("Time to solution (day)")
ax.set_ylabel("CO$_2$ production (kg)")
ax.set_title(
    f"{nb_particles_dict[nb_particles_short]}" " particles, 10 N-Body time units"
)
fig.tight_layout()

plt.show()