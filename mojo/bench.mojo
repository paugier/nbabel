
# from math import sqrt
from time import now as perf_counter
import sys

# from file import open
from python import Python
from utils.vector import DynamicVector
# from datetime import timedelta

# import numpy as np

from util import split

# def load_input_data(path: String):
#     pd = Python.import_module("pandas")

#     df = pd.read_csv(
#         path
#         # , names=["mass", "x", "y", "z", "vx", "vy", "vz"], delimiter=r"\s+"
#     )
    # masses = df["mass"].values
    # positions = df.loc[:, ["x", "y", "z"]].values
    # velocities = df.loc[:, ["vx", "vy", "vz"]].values

    # return masses, positions, velocities


def read_file(path: String) -> String:
    let text: String
    with open(path, "r") as file:
        text = file.read()
    return text




alias Vec4floats = SIMD[DType.float64, 4]
alias vec4zeros = Vec4floats(0)

@register_passable("trivial")
struct Particle:
    var position: Vec4floats
    var velocity: Vec4floats
    var acceleration: Vec4floats
    var acceleration1: Vec4floats
    var mass: Float64

    fn __init__(
        pos: Vec4floats,
        vel: Vec4floats,
        mass: Float64,
    ) -> Self:
        return Self {
            position: pos,
            velocity: vel,
            acceleration: vec4zeros,
            acceleration1: vec4zeros,
            mass: mass,
        }

    # not yet supported...
    fn __str__(self) -> String:
        # Mojo is still very basic for string formatting
        return "Particle(" + String(self.position) + ", ...)"



def main():

    t_start = perf_counter()

    args = sys.argv()

    p = Particle(vec4zeros, vec4zeros, 1.0)

    print(p.position)

    print(p.__str__())

    # if len(args) > 2:
    #     # not (yet?) supported
    #     time_end = Float64(args[2])
    # else:
    #     time_end = 10.

    time_end = 10.

    time_step = 0.001
    nb_steps = (time_end / time_step).to_int() + 1
    print(nb_steps)

    path_input = args[1]
    print(path_input)

    lines = split(read_file(path_input), "\n")

    for index in range(lines[:10].__len__()):
        line = lines[index]
        print(line)

    # masses, positions, velocities = load_input_data(path_input)

    # energy, energy0 = loop(time_step, nb_steps, masses, positions, velocities)
    # print(f"Final dE/E = {(energy - energy0) / energy0:.6e}")
    # print(
    #     f"{nb_steps} time steps run in {timedelta(seconds=perf_counter()-t_start)}"
    # )
