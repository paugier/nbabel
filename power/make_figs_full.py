import numpy as np
import matplotlib.pyplot as plt

from util import (
    load_data,
    complete_df_out,
    dir_saved,
    color_Python,
    color_Julia,
)
from make_figs import make_figs


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
    # print(df_out)

    return df_out.loc[6], df_out.loc[12]


row_pythran6, row_pythran12 = get_result_parallel(
    "parallel_pythran_16k_taurus-15.lyon.grid5000.fr_2021-02-06_23-12-07.h5"
    # "parallel_pythran_16k_taurus-5.lyon.grid5000.fr_2021-01-27_15-13-06.h5"
)
row_julia6, row_julia12 = get_result_parallel(
    "parallel_julia_16k_taurus-15.lyon.grid5000.fr_2021-02-06_23-45-53.h5"
    # "parallel_julia_16k_taurus-11.lyon.grid5000.fr_2021-01-26_21-20-37.h5"
)


def add_points(axes):
    ax0, ax1, ax2 = axes

    def plot(row, color, marker, markersize):
        ax1.plot(
            row.elapsed_time,
            row.CO2_core,
            color=color,
            marker=marker,
            markersize=markersize,
            markeredgecolor="k",
        )
        print(row)

    plot(row_pythran6, color=color_Python, marker="*", markersize="10")
    plot(row_julia6, color=color_Julia, marker="o", markersize="8")

    plot(row_pythran12, color=color_Python, marker="*", markersize="10")
    plot(row_julia12, color=color_Julia, marker="o", markersize="8")


def get_shift_labels(nb_particles_short, path_name, name, iax):
    factor_time = -0.003
    factor_cons = 0.004

    if "2021-02-04_22-04-51" in path_name:
        factor_time = 0.001
        factor_cons = -0.003

        if name == "Pythran\n naive":
            factor_time = -0.0055
            factor_cons = -0.008

        elif name.strip().startswith("C++"):
            factor_time = -0.0003
            factor_cons = -0.01

    if "2021-02-07_09-42-05" in path_name:
        factor_time = 0.001
        factor_cons = -0.003

        if name == "Pythran\n naive":
            factor_time = -0.0055
            factor_cons = -0.008

        elif name.strip().startswith("C++"):
            factor_time = -0.0003
            factor_cons = -0.01

    if nb_particles_short == "16k":
        if "2021-01-25_14-08-35" in path_name:
            if name == "Pythran\n naive":
                factor_time = -0.003
                factor_cons = -0.022

            elif name == "Numba":
                factor_time = -0.0052
                factor_cons = -0.003

            elif name.startswith("Fortran"):
                factor_time = 0.001
                factor_cons = -0.005

            elif name.startswith("PyPy map"):
                factor_time = 0.001
                factor_cons = -0.005

            elif name == "PyPy":
                factor_time = 0.001
                factor_cons = -0.005

            elif name.startswith("C++"):
                factor_time = -0.0042
                factor_cons = 0.005

        elif "2021-02-03_10-20-15" in path_name:
            if name == "Pythran\n naive":
                factor_time = -0.006
                factor_cons = -0.01

            elif name.startswith("C++"):
                factor_time = -0.0048
                factor_cons = 0.005

            elif name == "PyPy":
                factor_time = -0.002

            elif name.startswith("Fortran"):
                factor_time = 0.001
                factor_cons = -0.005

    return factor_time, factor_cons


if __name__ == "__main__":

    # with Julia NBabel
    # filter_path_str = "2021-02-03_10-20-15"

    # with Julia lowlevel
    filter_path_str = "2021-02-04_22-04-51"
    filter_path_str = "2021-02-07_09-42-05"

    path, (ax0, ax1, ax2) = make_figs(
        add_points=add_points,
        get_shift_labels=get_shift_labels,
        filter_path_str=filter_path_str,
    )

    mass = row_julia6.CO2_core

    ax1.text(3.7e-2, mass * 1.19, "Pythran & Julia\n  parallel", linespacing=1.2)

    ax1.text(7e-2, mass * 0.97, "  6\ncores", fontsize=8, linespacing=1.05)
    ax1.text(3.3e-2, mass * 1.02, "  12\ncores", fontsize=8, linespacing=1.05)

    xlim_line = [0.25, 1.55]
    kg_per_day = 0.28
    x_text = 0.61
    y_text = 0.19

    if filter_path_str == "2021-02-04_22-04-51":
        xlim_line = [0.28, 1.77]
        kg_per_day = 0.265
        x_text = 0.60
        y_text = 0.18

    x = np.array(xlim_line)

    ax1.plot(x, kg_per_day * x, "-", color="grey", zorder=0)
    ax1.text(x_text, y_text, f"{kg_per_day} kg/day", color="grey", rotation=51)

    ax1.text(0.25, 0.11, "single-threaded (1 core)", rotation=51, fontsize=11)

    plt.close(ax0.figure)
    # plt.close(ax1.figure)
    plt.close(ax2.figure)

    plt.show()