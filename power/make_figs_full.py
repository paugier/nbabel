import matplotlib.pyplot as plt


from util import load_data, complete_df_out, dir_saved
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
        "power",
    ]

    df_out = df.loc[:, columns].groupby(["nb_threads"]).mean()
    complete_df_out(df_out, info)

    return df_out.loc[6], df_out.loc[12]


row_pythran6, row_pythran12 = get_result_parallel(
    "parallel_pythran_16k_taurus-5.lyon.grid5000.fr_2021-01-27_15-13-06.h5"
)
row_julia6, row_julia12 = get_result_parallel(
    "parallel_julia_16k_taurus-11.lyon.grid5000.fr_2021-01-26_21-20-37.h5"
)


def add_points(axes):
    ax0, ax1, ax2 = axes
    row = row_pythran6
    ax1.plot(row.elapsed_time, row.CO2_core, "r", marker="*", markersize="10")
    print(row)

    row = row_julia6
    ax1.plot(row.elapsed_time, row.CO2_core, "ob", markersize="8")
    print(row)

    row = row_pythran12
    ax1.plot(row.elapsed_time, row.CO2_core, "r", marker="*", markersize="10")
    print(row)

    row = row_julia12
    ax1.plot(row.elapsed_time, row.CO2_core, "ob", markersize="8")
    print(row)


def get_shift_labels(nb_particles_short, path_name, name, iax):
    factor_time = -0.003
    factor_cons = 0.005

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


            #     factor_time = -0.0035
            #     factor_cons = 0.0045

            elif name.startswith("C++"):
                factor_time = -0.0042
                factor_cons = 0.005

    return factor_time, factor_cons


if __name__ == "__main__":

    ax0, ax1, ax2 = make_figs(
        add_points=add_points, get_shift_labels=get_shift_labels
    )

    mass = row_julia6.CO2_core

    ax1.text(3.5e-2, mass * 1.27, "Pythran & Julia")
    ax1.text(3.9e-2, mass * 1.15, "parallel")

    ax1.text(7e-2, mass * 1, "6 cores", fontsize=8)
    ax1.text(3.2e-2, mass * 1, "12 cores", fontsize=8)

    plt.close(ax0.figure)
    # plt.close(ax1.figure)
    plt.close(ax2.figure)

    plt.show()