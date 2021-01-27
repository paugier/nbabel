import numpy as np
import pandas as pd
import h5py
from scipy.integrate import trapz

import matplotlib.pyplot as plt

def load_data(path_h5):

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

        nb_cpus = file.attrs["nb_cpus"]

        times = file["times"][:]
        watts = file["watts"][:]

    power_sleep = np.percentile(watts, 5)
    nb_cores = nb_cpus
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

        consommations[index] = trapz(watts_run, times_run)  # in J

        # fig, ax1 = plt.subplots()
        # ax1.plot(times_run, watts_run)
        # nb_threads = row.nb_threads
        # ax1.set_title(f"{row.implementation} nb_threads={nb_threads}")


    df["consommation"] = consommations
    df["power"] = df["consommation"] / df["elapsed_time"]

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
    0.283 kWh -> 1 kg
    """

    return consommation / 3.6e6 / 0.283


def complete_df_out(df_out, info):
    t_end = info["t_end"]

    elapsed_max = df_out["elapsed_time"].max()

    if df_out.index.name == "nb_threads":
        nb_threads = df_out.index
    else:
        nb_threads = 1

    df_out["consommation_core"] = df_out["consommation"] - df_out[
        "elapsed_time"
    ] * info["power_sleep_1core"] * (info["nb_cores"] - nb_threads)

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
