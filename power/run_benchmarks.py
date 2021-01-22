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

import pandas as pd

# parameters of this script
# TODO argparse
nb_particles_short = "1k"
time_julia_bench = 1.0  # (s)
t_sleep_before = 1  # (s)


def time_as_str(decimal=0):
    """Return a string coding the time."""
    dt = datetime.now()
    ret = dt.strftime("%Y-%m-%d_%H-%M-%S")
    if decimal > 0:
        if not isinstance(decimal, int):
            raise TypeError

        ret += f".{dt.microsecond:06d}"[: decimal + 1]
    return ret


def run(command):
    print(f"launching command:\n{command}")
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

nb_particles_dict = {"1k": 1024, "2k": 2048, "16k": 16384}
nb_particles = nb_particles_dict[nb_particles_short]


def create_command(command_template, nb_particles_short, t_end):
    return command_template.format(
        nb_particles_short=nb_particles_short,
        t_end=t_end,
        nb_particles=nb_particles,
    )


implementations = {
    "julia nbabel.org": (
        "julia",
        "julia -O3 --check-bounds=no -- run.jl "
        "nbabel.jl ../data/input{nb_particles_short} true {t_end}",
    ),
    "c++ nbabel.org": (
        "cpp",
        "cat ../data/input{nb_particles_short} | time ./main {t_end}",
    ),
    "pypy": (
        "py",
        "pypy bench_pypy4.py ../data/input{nb_particles_short} {t_end}",
    ),
    "numba": (
        "py",
        "python bench_numba.py ../data/input{nb_particles_short} {t_end}",
    ),
    "julia optimized": (
        "julia",
        "julia -O3 --check-bounds=no -- run.jl "
        "nbabel5_serial.jl ../data/input{nb_particles_short} true {t_end}",
    ),
    "pythran": (
        "py",
        "python bench.py ../data/input{nb_particles_short} {t_end}",
    ),
    "pythran high-level jit": (
        "py",
        "python bench_numpy_highlevel_jit.py ../data/input{nb_particles_short} {t_end}",
    ),
    "fortran nbabel.org": (
        "fortran",
        "./nbabel ../data/input{nb_particles_short} {nb_particles} {t_end}",
    ),
}

print("First run to evaluate t_end for time_julia_bench")
t_end = 0.1
if nb_particles_short == "16k":
    t_end = 0.05

name_dir, command_template = implementations["julia optimized"]
working_dir = path_base_repo / name_dir
command = create_command(command_template, nb_particles_short, t_end)

t_perf_start = perf_counter()
run(command)
elapsed_time = perf_counter() - t_perf_start

t_end = t_end * time_julia_bench / elapsed_time
print(f"We'll run the benchmarks with t_end = {t_end}")

lines = []
index_run = 0

for _ in range(1):
    for implementation, (name_dir, command_template) in implementations.items():
        working_dir = path_base_repo / name_dir

        # warmup
        for _ in range(1):
            command = create_command(command_template, nb_particles_short, 0.01)
            run(command)

        command = create_command(command_template, nb_particles_short, t_end)
        sleep(1)

        t_perf_start = perf_counter()
        timestamp_start = time()
        sleep(t_sleep_before)
        elapsed_time = perf_counter() - t_perf_start
        timestamp_end = time()

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
        run(command)
        elapsed_time = perf_counter() - t_perf_start
        timestamp_end = time()

        sleep(1)

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

path_dir_result = path_base_repo / "power/results"
path_dir_result.mkdir(exist_ok=True)
path_result = path_dir_result / f"times{time_as_str()}.csv"
df.to_csv(path_result)

# TODO get power data
# TODO save power data and other informations (t_end, hostname, ...) is a hdf5 file
