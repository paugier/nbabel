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

watt_sleep = np.percentile(watts, 5)

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

print(df)

df_out = (
    df.loc[:, ["implementation", "language", "elapsed_time", "consommation", "power"]]
    .groupby(["implementation"])
    .mean()
)
df_out.drop("sleep(t_sleep_before)", inplace=True)

print(df_out)

ax = df_out.plot(x="elapsed_time", y="consommation", kind="scatter", loglog=True)

for index, row in df_out.iterrows():
    ax.text(row.elapsed_time, row.consommation, row.name)


ax.figure.tight_layout()

plt.show()