from pathlib import Path

import numpy as np
import pandas as pd
import h5py
from matplotlib import cm
from scipy.integrate import trapz

here = Path(__file__).absolute().parent

dir_saved = here / "saved"

# See https://matplotlib.org/tutorials/colors/colormaps.html
cmap = cm.get_cmap("tab20c")
colors = cmap(range(20))

color_Python = colors[4 + 0]  # red: level 0
color_static = colors[8 + 2]  # green: level 2
color_Julia = colors[0 + 1]  # blue: level 1

nb_particles_dict = {"1k": 1024, "2k": 2048, "16k": 16384}


def load_data(path_h5):

    path_csv = path_h5.with_suffix(".csv")

    assert path_csv.exists()
    assert path_h5.exists()

    df = pd.read_csv(path_csv)

    with h5py.File(path_h5) as file:
        t_end = file.attrs["t_end"]
        node = file.attrs["node"]
        nb_particles_short = file.attrs["nb_particles_short"]
        t_sleep_before = file.attrs["t_sleep_before"]
        try:
            time_julia_bench = file.attrs["time_julia_bench"]
        except KeyError:
            time_julia_bench = 0

        nb_cpus = file.attrs["nb_cpus"]

        times = file["times"][:]
        watts = file["watts"][:]

    # fig, ax0 = plt.subplots()
    # ax0.plot(times, watts)

    consommations = np.empty(df.shape[0])

    power_sleeps = []

    deltat = 0.2
    for index, row in df.iterrows():

        cond = (times > row.timestamp_start - deltat) & (
            times < row.timestamp_end + deltat
        )

        # ax0.vlines(row.timestamp_start, 0, 250, colors="g")
        # ax0.vlines(row.timestamp_end, 0, 250, colors="r")

        times_run = times[cond]
        watts_run = watts[cond]

        consommations[index] = trapz(watts_run, times_run)  # in J

        if row.implementation.startswith("sleep"):
            power_sleeps.append(np.percentile(watts_run, 20))

        # fig, ax1 = plt.subplots()
        # ax1.plot(times_run, watts_run)
        # nb_threads = row.nb_threads
        # ax1.set_title(f"{row.implementation} nb_threads={nb_threads}")

    power_sleep = np.array(power_sleeps).mean()
    print("power_sleep", power_sleep, power_sleeps)
    nb_cores = nb_cpus // 2
    power_sleep_1core = power_sleep / nb_cores

    df["consommation"] = consommations
    df["power_mean"] = df["consommation"] / df["elapsed_time"]

    loc = locals()

    info = {
        name: loc[name]
        for name in [
            "t_end",
            "node",
            "nb_particles_short",
            "time_julia_bench",
            "t_sleep_before",
            "power_sleep",
            "power_sleep_1core",
            "nb_cores",
        ]
    }

    return info, df


def compute_CO2_mass(consommation):
    """
    kWh = 3.6e6 J

    283 g CO2 / kWh

    warning: "0.283 kWh/kg" typo in Zwart (2020) (personal communication)
    """

    return consommation / 3.6e6 * 0.283


def complete_df_out(df_out, info):
    t_end = info["t_end"]

    elapsed_max = df_out["elapsed_time"].max()

    if df_out.index.name == "nb_threads":
        nb_threads = df_out.index
    else:
        nb_threads = 1

    if info["node"].startswith("taurus"):
        nb_cores = 12
    else:
        nb_cores = info["nb_cores"]

    print("power_sleep_1core", info["power_sleep_1core"])

    df_out["consommation_core"] = df_out["consommation"] - df_out[
        "elapsed_time"
    ] * info["power_sleep_1core"] * (nb_cores - nb_threads)

    df_out["power_mean_core"] = (
        df_out["consommation_core"] / df_out["elapsed_time"]
    )

    df_out["consommation_alt"] = (
        df_out["consommation"]
        + (elapsed_max - df_out["elapsed_time"]) * info["power_sleep"]
    )

    df_out["CO2"] = (10 / t_end) * compute_CO2_mass(df_out["consommation"])
    df_out["CO2_alt"] = (10 / t_end) * compute_CO2_mass(
        df_out["consommation_alt"]
    )
    df_out["CO2_core"] = (10 / t_end) * compute_CO2_mass(
        df_out["consommation_core"]
    )
    # in days
    df_out.elapsed_time *= 10 / t_end / (24 * 3600)
