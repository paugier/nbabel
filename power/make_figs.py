from pathlib import Path
from pprint import pprint

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from util import load_data, complete_df_out

here = Path(__file__).absolute().parent

dir_saved = here / "saved"


def get_shift_labels(nb_particles_short, path_name, name, iax):
    factor_time = -0.008
    factor_cons = 0.005

    if nb_particles_short == "16k":
        if "2021-01-24_09-14-08" in path_name:
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
        elif "2021-01-25_14-08-35" in path_name:
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

    return factor_time, factor_cons


def make_figs(
    nb_particles_short="16k",
    add_points=None,
    get_shift_labels=get_shift_labels,
):

    paths_h5 = sorted(dir_saved.glob(f"{nb_particles_short}_*.h5"))
    pprint(paths_h5)

    path_h5 = paths_h5[0]

    info, df = load_data(path_h5)
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

    complete_df_out(df_out, info)
    print(df_out)

    axes = []
    for _ in range(3):
        fig, ax = plt.subplots()
        ax.set_xscale("log")
        ax.set_yscale("log")
        axes.append(ax)

    quantities = ["CO2", "CO2_core", "CO2_alt"]

    for index, row in df_out.iterrows():
        implementation, language = row.name

        if implementation == "pypy":
            continue

        if language == "py":
            color = "r"
        elif language in ("cpp", "fortran"):
            color = "g"
        elif language == "julia":
            color = "b"
        else:
            color = "y"

        zorder = None
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
            zorder = 100

        for ax, quantity in zip(axes, quantities):
            ax.plot(
                row.elapsed_time,
                row[quantity],
                marker=marker,
                color=color,
                markersize=markersize,
                zorder=zorder,
            )

    if add_points is not None:
        add_points(axes)

    x_ratios = []
    y_ratios = []
    for ax in axes:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        x_ratios.append(xmax / xmin)
        y_ratios.append(ymax / ymin)

    for index, row in df_out.iterrows():
        name = row.name[0].capitalize()

        if name == "Pypy":
            continue

        if name.endswith("Pythran high-level jit"):
            name = "Pythran\n naive"
        elif name.startswith("Pypy"):
            name = name.replace("Pypy", "PyPy")
            name = "PyPy"

        for iax, (ax, quantity) in enumerate(zip(axes, quantities)):
            factor_time, factor_cons = get_shift_labels(
                nb_particles_short, path_h5.name, name, iax
            )
            ax.text(
                row.elapsed_time * (1 + factor_time * x_ratios[iax]),
                row[quantity] * (1 + factor_cons * y_ratios[iax]),
                name,
            )

    axes[0].set_ylabel("CO$_2$ production full node (kg)")
    axes[1].set_ylabel("CO$_2$ production (kg)")
    axes[2].set_ylabel("CO$_2$ production full node during time slowest run (kg)")

    handles_legend_languages = [
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
    ]

    handles_legend_compilation_types = [
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

    for ax in axes:
        ax.set_xlabel("Time to solution (day)")
        ax.set_title(f"{nb_particles_short} particles, 10 N-Body time units")
        ax.figure.tight_layout()

        # xmin, xmax = ax.get_xlim()
        # ymin, ymax = ax.get_ylim()

        # x_ratio = xmax / xmin
        # y_ratio = ymax / ymin

        # print(xmin, xmax, x_ratio)
        # print("ymax", ymax)

        ax.figure.legend(
            handles=handles_legend_languages,
            loc=(0.18, 0.757),
        )
        ax.figure.legend(
            handles=handles_legend_compilation_types,
            loc=(0.18, 0.64),
        )

    return axes


if __name__ == "__main__":

    ax0, ax1, ax2 = make_figs()

    plt.close(ax0.figure)
    # plt.close(ax1.figure)
    plt.close(ax2.figure)

    plt.show()
