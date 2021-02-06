"""
We should save two files:

1. a csv file with columns:

# implementation language index timestamp_start timestamp_end elapsed_time

2. a hdf5 file with power versus time data.

"""

from pathlib import Path
from time import time, perf_counter, sleep
import platform
import os

import numpy as np
import pandas as pd
import h5py

from run_benchmarks import get_time_as_str, run

t_sleep_before = 4  # (s)

path_base_repo = Path(__file__).absolute().parent.parent
working_dir = path_base_repo / "py"

nb_cpus = os.cpu_count()

if nb_cpus == 24:
    nb_threads_list = [1, 2, 4, 6, 8, 12]
elif nb_cpus == 6:
    nb_threads_list = [1, 2, 4, 6]
else:
    nb_threads_list = [1, 2, 4]


command_template = (
    "python bench{omp}.py ../data/input{nb_particles_short} {t_end}"
)


def run_benchmarks(nb_particles_short, time_sequential_bench):

    def create_command(command_template, nb_particles_short, t_end, nb_threads=1):

        if nb_threads == 1:
            omp = ""
        else:
            omp = "_omp"

        return command_template.format(
            nb_particles_short=nb_particles_short,
            t_end=t_end,
            omp=omp,
        )

    print("First run to evaluate t_end for time_sequential_bench")

    command = create_command(command_template, nb_particles_short, 0.002)
    run(command, working_dir)

    if nb_particles_short == "1k":
        t_end = 2
    elif nb_particles_short == "2k":
        t_end = 0.5
    elif nb_particles_short == "16k":
        t_end = 0.05
    else:
        raise ValueError

    command = create_command(command_template, nb_particles_short, t_end)
    t_perf_start = perf_counter()
    run(command, working_dir)
    elapsed_time = perf_counter() - t_perf_start
    print(f"elapsed time: {elapsed_time:.3f} s")

    t_end = t_end * time_sequential_bench / elapsed_time
    print(f"We'll run the benchmarks with t_end = {t_end}")

    timestamp_before = time()
    time_as_str = get_time_as_str()

    lines = []
    index_run = 0

    nb_loops = 2
    for i_loop in range(nb_loops):
        print(f"--- Running all benchmarks ({i_loop+1}/{nb_loops}) ---")
        for nb_threads in nb_threads_list:
            print(f"setting OMP_NUM_THREADS={nb_threads}")
            os.environ["OMP_NUM_THREADS"] = f"{nb_threads}"

            # warmup
            for _ in range(1):
                command = create_command(
                    command_template, nb_particles_short, 0.004, nb_threads
                )
                run(command, working_dir)

            command = create_command(
                command_template, nb_particles_short, t_end, nb_threads
            )
            sleep(2)

            t_perf_start = perf_counter()
            timestamp_start = time()
            sleep(t_sleep_before)
            elapsed_time = perf_counter() - t_perf_start
            timestamp_end = time()

            sleep(2)

            lines.append(
                [
                    "sleep(t_sleep_before)",
                    1,
                    "None",
                    index_run,
                    timestamp_start,
                    timestamp_end,
                    elapsed_time,
                ]
            )

            t_perf_start = perf_counter()
            timestamp_start = time()
            run(command, working_dir)
            elapsed_time = perf_counter() - t_perf_start
            timestamp_end = time()
            print(f"elapsed time: {elapsed_time:.3f} s")

            sleep(2)

            lines.append(
                [
                    f"nbabel5_threads.jl",
                    nb_threads,
                    "py",
                    index_run,
                    timestamp_start,
                    timestamp_end,
                    elapsed_time,
                ]
            )
            index_run += 1

    columns = (
        "implementation nb_threads language index timestamp_start timestamp_end elapsed_time"
    ).split()

    df = pd.DataFrame(
        lines,
        columns=columns,
    )

    df.sort_values("nb_threads", inplace=True)

    elapsed_serial = df[(df.language == "py") & (df.nb_threads == 1)][
        "elapsed_time"
    ].min()
    df["ratio_elapsed"] = df["elapsed_time"] / elapsed_serial

    print(df[df.language == "py"])

    node = platform.node()

    path_dir_result = path_base_repo / "power/tmp"
    path_dir_result.mkdir(exist_ok=True)
    path_result = (
        path_dir_result
        / f"parallel_pythran_{nb_particles_short}_{node}_{time_as_str}.csv"
    )
    df.to_csv(path_result)

    if "grid5000" not in node:
        return

    from getwatt import getwatt

    path_result = path_result.with_suffix(".h5")

    timestamp_end = time()
    node_shortname = node.split(".")[0]
    with h5py.File(str(path_result), "w") as file:
        file.attrs["t_end"] = t_end
        file.attrs["node"] = node
        file.attrs["node_shortname"] = node_shortname
        file.attrs["nb_particles_short"] = nb_particles_short
        file.attrs["time_sequential_bench"] = time_sequential_bench
        file.attrs["t_sleep_before"] = t_sleep_before
        file.attrs["nb_cpus"] = nb_cpus
        file.attrs["timestamp_before"] = timestamp_before
        file.attrs["timestamp_end"] = timestamp_end

    conso = np.array(getwatt(node_shortname, timestamp_before, timestamp_end))
    times = conso[:, 0]
    watts = conso[:, 1]
    with h5py.File(str(path_result), "a") as file:
        file.create_dataset(
            "times", data=times, compression="gzip", compression_opts=9
        )
        file.create_dataset(
            "watts", data=watts, compression="gzip", compression_opts=9
        )

    print(f"File {path_result} saved")


if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1:
        # can be "1k", "2k", "16k"
        nb_particles_short = sys.argv[1]
    else:
        nb_particles_short = "1k"

    if len(sys.argv) > 2:
        time_sequential_bench = float(sys.argv[2])
    else:
        time_sequential_bench = 20.0  # (s)

    run_benchmarks(nb_particles_short, time_sequential_bench)
