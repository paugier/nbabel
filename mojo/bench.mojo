# from math import sqrt
from time import now as perf_counter
import sys

# from file import open
from python import Python
from utils.vector import InlinedFixedVector

# from datetime import timedelta

from util import split, list
from helpers import string_to_float

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
        return (
            "Particle(mass="
            + String(self.mass)
            + ", position="
            + String(self.position)
            + ", ...)"
        )


def main():
    t_start = perf_counter()

    args = sys.argv()

    if len(args) > 2:
        time_end = string_to_float(args[2])
    else:
        time_end = 10.0

    time_end = 10.0

    time_step = 0.001
    nb_steps = (time_end / time_step).to_int() + 1

    path_input = args[1]
    print(path_input)

    lines = split(read_file(path_input), "\n")

    nb_parts = 0
    for index in range(lines.__len__()):
        line = lines[index]
        if not len(line):
            continue
        nb_parts += 1

    particles = InlinedFixedVector[Particle, 4](nb_parts)

    index_part = -1

    for index in range(lines.__len__()):
        line = lines[index]
        if not len(line):
            continue

        index_part += 1

        words = split(line)
        words1 = list[String]()
        for idx in range(1, words.__len__()):
            word = words[idx]
            if len(word):
                words1.append(word)

        m = string_to_float(words1[0])
        x = string_to_float(words1[1])
        y = string_to_float(words1[2])
        z = string_to_float(words1[3])
        vx = string_to_float(words1[4])
        vy = string_to_float(words1[5])
        vz = string_to_float(words1[6])

        particles[index_part] = Particle(Vec4floats(x, y, z, 0), Vec4floats(vx, vy, vz, 0), m)

    print(particles[0].__str__())

    # masses, positions, velocities = load_input_data(path_input)

    # energy, energy0 = loop(time_step, nb_steps, masses, positions, velocities)
    # print(f"Final dE/E = {(energy - energy0) / energy0:.6e}")
    # print(
    #     f"{nb_steps} time steps run in {timedelta(seconds=perf_counter()-t_start)}"
    # )
