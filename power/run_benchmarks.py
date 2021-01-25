"""
We should save two files:

1. a csv file with columns:

# implementation language index timestamp_start timestamp_end elapsed_time

2. a hdf5 file with power versus time data.

warning: this script does not take care of compilation.
"""

from pathlib import Path
import subprocess
from time import time, perf_counter, sleep
from datetime import datetime
import platform
import os
import gzip

import numpy as np
import pandas as pd
import h5py

t_sleep_before = 4  # (s)


def get_time_as_str(decimal=0):
    """Return a string coding the time."""
    dt = datetime.now()
    ret = dt.strftime("%Y-%m-%d_%H-%M-%S")
    if decimal > 0:
        if not isinstance(decimal, int):
            raise TypeError

        ret += f".{dt.microsecond:06d}"[: decimal + 1]
    return ret


def run(command, working_dir):
    print(f"launching command ({datetime.now():%Y-%m-%d %H:%M:%S}):\n{command}")
    try:
        return subprocess.run(
            command, shell=True, check=True, cwd=working_dir, capture_output=True
        )
    except subprocess.CalledProcessError as error:
        print(
            f"The command\n{command}\nreturned non-zero exit status. "
            f"stderr:\n{error.stderr}"
        )
        raise


path_base_repo = Path(__file__).absolute().parent.parent
nb_cpus = os.cpu_count()

implementations = {
    "julia optimized": (
        "julia",
        "julia -O3 --check-bounds=no -- run.jl "
        "nbabel5_serial.jl ../data/input{nb_particles_short} true {t_end}",
    ),
    "pythran": (
        "py",
        "python bench.py ../data/input{nb_particles_short} {t_end}",
    ),
    "pypy map-improvements": (
        "py",
        "pypy-map-improvements bench_purepy_Particle.py ../data/input{nb_particles_short} {t_end}",
    ),
    "numba": (
        "py",
        "python bench_numba.py ../data/input{nb_particles_short} {t_end}",
    ),
    "julia nbabel.org": (
        "julia",
        "julia -O3 --check-bounds=no -- run.jl "
        "nbabel.jl ../data/input{nb_particles_short} true {t_end}",
    ),
    "fortran nbabel.org": (
        "fortran",
        "./nbabel ../data/input{nb_particles_short} {nb_particles} {t_end}",
    ),
    "c++ nbabel.org": (
        "cpp",
        "cat ../data/input{nb_particles_short} | time ./main {t_end}",
    ),
    "pythran high-level jit": (
        "py",
        "python bench_numpy_highlevel_jit.py ../data/input{nb_particles_short} {t_end}",
    ),
    "pypy": (
        "py",
        "pypy bench_purepy_Point.py ../data/input{nb_particles_short} {t_end}",
    ),
}

nb_particles_dict = {"1k": 1024, "2k": 2048, "16k": 16384}


def run_benchmarks(nb_particles_short, time_julia_bench):

    nb_particles = nb_particles_dict[nb_particles_short]

    def create_command(command_template, nb_particles_short, t_end):
        return command_template.format(
            nb_particles_short=nb_particles_short,
            t_end=t_end,
            nb_particles=nb_particles,
        )

    print("First run to evaluate t_end for time_julia_bench")
    t_end = 0.1
    if nb_particles_short == "16k":
        t_end = 0.05

    name_dir, command_template = implementations["julia optimized"]
    working_dir = path_base_repo / name_dir
    command = create_command(command_template, nb_particles_short, t_end)

    t_perf_start = perf_counter()
    run(command, working_dir)
    elapsed_time = perf_counter() - t_perf_start

    t_end = t_end * time_julia_bench / elapsed_time
    print(f"We'll run the benchmarks with t_end = {t_end}")

    timestamp_before = time()
    time_as_str = get_time_as_str()

    lines = []
    index_run = 0

    nb_loops = 2
    for i_loop in range(nb_loops):
        print(f"--- Running all benchmarks ({i_loop+1}/{nb_loops}) ---")
        for implementation, (
            name_dir,
            command_template,
        ) in implementations.items():
            working_dir = path_base_repo / name_dir

            # warmup
            for _ in range(1):
                command = create_command(
                    command_template, nb_particles_short, 0.004
                )
                run(command, working_dir)

            command = create_command(command_template, nb_particles_short, t_end)
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
                    name_dir,
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
                    implementation,
                    name_dir,
                    index_run,
                    timestamp_start,
                    timestamp_end,
                    elapsed_time,
                ]
            )
            index_run += 1

    columns = (
        "implementation language index timestamp_start timestamp_end elapsed_time"
    ).split()

    df = pd.DataFrame(
        lines,
        columns=columns,
    )

    df.sort_values("implementation", inplace=True)

    elapsed_pythran = df[df.implementation == "pythran"]["elapsed_time"].min()
    df["ratio_elapsed"] = df["elapsed_time"] / elapsed_pythran

    print(df)

    node = platform.node()

    path_dir_result = path_base_repo / "power/tmp"
    path_dir_result.mkdir(exist_ok=True)
    path_result = (
        path_dir_result / f"{nb_particles_short}_{node}_{time_as_str}.csv"
    )
    df.to_csv(path_result)

    if "grid5000" not in node:
        return

    from getwatt import getwatt

    timestamp_end = time()
    node_shortname = node.split(".")[0]
    try:
        conso = np.array(getwatt(node_shortname, timestamp_before, timestamp_end))
    except gzip.BadGzipFile:
        print(
            "Error gzip.BadGzipFile. " "Power data will need to be upload later."
        )
        error_BadGzipFile = True
        path_result = path_result.with_name(
            path_result.stem + "_incomplete" + ".h5"
        )
    else:
        error_BadGzipFile = False
        path_result = path_result.with_suffix(".h5")

    with h5py.File(str(path_result), "w") as file:
        file.attrs["t_end"] = t_end
        file.attrs["node"] = node
        file.attrs["node_shortname"] = node_shortname
        file.attrs["nb_particles_short"] = nb_particles_short
        file.attrs["time_julia_bench"] = time_julia_bench
        file.attrs["t_sleep_before"] = t_sleep_before
        file.attrs["nb_cpus"] = nb_cpus
        file.attrs["timestamp_before"] = timestamp_before
        file.attrs["timestamp_end"] = timestamp_end

    if error_BadGzipFile:
        return

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
        time_julia_bench = float(sys.argv[2])
    else:
        time_julia_bench = 20.0  # (s)

    run_benchmarks(nb_particles_short, time_julia_bench)