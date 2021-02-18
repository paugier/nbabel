//! Based on https://github.com/rust-lang/packed_simd/blob/master/examples/nbody/src/simd.rs
use std::path::Path;
use std::{fs, mem};

use wide::f64x4;

#[derive(Clone)]
pub struct Particle {
    position: f64x4,
    velocity: f64x4,
    acceleration: [f64x4; 2],
    mass: f64,
}

pub struct Bodies {
    particles: Vec<Particle>,
}

impl Bodies {
    pub fn new(path_name: &str) -> Bodies {
        let file_path = Path::new(path_name);
        let particles: Vec<Particle> = fs::read_to_string(file_path)
            .expect("File not found!")
            .lines()
            .filter(|x| !x.is_empty())
            .map(|x| parse_row(x))
            .collect();

        Bodies { particles }
    }

    pub fn compute_energy(&self, pe: f64) -> f64 {
        let res: f64 = self
            .particles
            .iter()
            .map(|p| 0.5 * p.mass * (p.velocity * p.velocity).reduce_add())
            .sum();
        pe + res
    }

    pub fn advance_velocities(&mut self, dt: f64) {
        for p in &mut self.particles {
            p.velocity += 0.5 * dt * (p.acceleration[0] + p.acceleration[1]);
        }
    }

    pub fn advance_positions(&mut self, dt: f64) {
        for p in &mut self.particles {
            p.position += dt * p.velocity + 0.5 * dt.powi(2) * p.acceleration[0];
        }
    }

    pub fn accelerate(&mut self) -> f64 {
        for p in self.particles.iter_mut() {
            p.acceleration[1] = mem::take(&mut p.acceleration[0]);
        }

        let mut pe = 0.0;

        let mut particles = self.particles.as_mut_slice();

        while let Some((p1, rest)) = particles.split_first_mut() {
            particles = rest;

            for p2 in particles.iter_mut() {
                let vector = p1.position - p2.position;
                let norm2 = (vector * vector).reduce_add();
                let distance = norm2.sqrt();
                let distance_cube = norm2 * distance;

                p1.acceleration[0] -= (p2.mass / distance_cube) * vector;
                p2.acceleration[0] += (p1.mass / distance_cube) * vector;

                pe -= (p1.mass * p2.mass) / distance;
            }
        }

        pe
    }
}

fn parse_row(line: &str) -> Particle {
    let row_vec: Vec<f64> = line
        .split(' ')
        .filter(|s| s.len() > 2)
        .map(|s| s.parse().unwrap())
        .collect();

    Particle {
        position: f64x4::from([row_vec[1], row_vec[2], row_vec[3], 0.]),
        velocity: f64x4::from([row_vec[4], row_vec[5], row_vec[6], 0.]),
        acceleration: [f64x4::splat(0.0); 2],
        mass: row_vec[0],
    }
}

pub fn run(path: &str) {
    let mut pe;
    let mut energy = 0.;
    let (tend, dt) = (10.0, 0.001); // end time, timestep
    let (mut old_energy, energy0) = (-0.25, -0.25);

    println!("Running SIMD version");

    let mut bodies = Bodies::new(path);

    bodies.accelerate();

    for step in 1..(tend / dt + 1.0) as i64 {
        bodies.advance_positions(dt);
        pe = bodies.accelerate();
        bodies.advance_velocities(dt);

        // if step % 100 == 0 {
        //     energy = bodies.compute_energy(pe);
        //     println!(
        //         "t = {:5.2}, E = {:.10},  dE/E = {:+.10}",
        //         dt * step as f64,
        //         energy,
        //         (energy - old_energy) / old_energy
        //     );
        //     old_energy = energy;
        // }
    }

    // println!("Final dE/E = {}", (energy - energy0) / energy0);
}
