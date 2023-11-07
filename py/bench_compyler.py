"""
Taken from https://github.com/comPylerProject/AboutNbody/blob/master/nbody-C.py

See https://github.com/comPylerProject/AboutNbody

# short
python bench_compyler.py ../data/input16

# longer
python bench_compyler.py ../data/input128

"""

import sys
from itertools import combinations
from math import sqrt
from time import perf_counter
from datetime import timedelta


class Particle:
    __slots__ = ('mass', 'px', 'py', 'pz', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'oax', 'oay', 'oaz')

    def __init__(self, mass, x, y, z, vx, vy, vz):
        self.mass = mass
        self.px, self.py, self.pz = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.ax, self.ay, self.az = 0.0, 0.0, 0.0
        self.oax, self.oay, self.oaz = 0.0, 0.0, 0.0


class Cluster(list):
    def get_energy(self):
        ke = 0.0
        for p in self:
            ke += 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)
        pe = 0.0
        for p1, p2 in combinations(self, 2):
            dx = p1.px - p2.px
            dy = p1.py - p2.py
            dz = p1.pz - p2.pz
            pe -= (p1.mass * p2.mass) / sqrt(dx * dx + dy * dy + dz * dz)
        return ke + pe

    def step(self, dt):
        half_dt_square = 0.5 * dt * dt
        for p in self:
            p.px += dt * p.vx + half_dt_square * p.ax
            p.py += dt * p.vy + half_dt_square * p.ay
            p.pz += dt * p.vz + half_dt_square * p.az
        self.accelerate()
        half_dt = 0.5 * dt
        for p in self:
            p.vx += half_dt * (p.ax + p.oax)
            p.vy += half_dt * (p.ay + p.oay)
            p.vz += half_dt * (p.az + p.oaz)

    def accelerate(self):
        for p in self:
            p.oax, p.oay, p.oaz = p.ax, p.ay, p.az
            p.ax, p.ay, p.az = 0.0, 0.0, 0.0

        nb_particules = len(self)
        for i, p1 in enumerate(self):
            for i in range(i + 1, nb_particules):
                p2 = self[i]
                dx = p1.px - p2.px
                dy = p1.py - p2.py
                dz = p1.pz - p2.pz
                distance_square = dx * dx + dy * dy + dz * dz
                distance_cube = distance_square * sqrt(distance_square)
                tmp = p2.mass / distance_cube
                p1.ax -= tmp * dx
                p1.ay -= tmp * dy
                p1.az -= tmp * dz
                tmp = p1.mass / distance_cube
                p2.ax += tmp * dx
                p2.ay += tmp * dy
                p2.az += tmp * dz


if __name__ == "__main__":

    t_start = perf_counter()

    try:
        time_end = float(sys.argv[2])
    except IndexError:
        time_end = 10.

    time_step = 0.001
    cluster = Cluster()
    with open(sys.argv[1]) as input_file:
        for line in input_file:
            try:
                cluster.append(Particle(*[float(x) for x in line.split()[1:]]))
            except TypeError:
                pass

    old_energy = energy0 = energy = -0.25
    cluster.accelerate()
    for step in range(1, int(time_end / time_step + 1)):
        cluster.step(time_step)
        if not step % 100:
            energy = cluster.get_energy()
            print(
                f"t = {time_step * step:.2f}, E = {energy:.10f}, "
                f"dE/E = {(energy - old_energy) / old_energy:.10f}"
            )
            old_energy = energy
    print(f"Final dE/E = {(energy - energy0) / energy0:.6e}")

    print(f"run in {timedelta(seconds=perf_counter()-t_start)}")
