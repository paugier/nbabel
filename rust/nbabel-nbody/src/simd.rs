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
            .expect(&format!("File `{}` not found!", path_name))
            .lines()
            .filter(|x| !x.is_empty())
            .map(|x| parse_row(x))
            .collect();
        Bodies { particles }
    }

    pub fn compute_energy(&mut self) -> (f64, f64) {
        let (mut epot, mut ekin) = (0.0, 0.0);

        let mut particles = self.particles.as_mut_slice();

        while let Some((p1, rest)) = particles.split_first_mut() {
            ekin += 0.5 * p1.mass * (p1.velocity * p1.velocity).reduce_add();

            particles = rest;

            for p2 in particles.iter_mut() {
                let dr = p1.position - p2.position;
                let rinv = 1. / (dr * dr).reduce_add().sqrt();
                epot -= p1.mass * p2.mass * rinv;
            }
        }
        (ekin, epot)
    }

    pub fn compute_k_energy(&self) -> f64 {
        self.particles
            .iter()
            .map(|p| 0.5 * p.mass * (p.velocity * p.velocity).reduce_add())
            .sum::<f64>()
    }

    pub fn advance_velocities(&mut self, dt: f64) {
        self.particles
            .iter_mut()
            .for_each(|p| p.velocity += 0.5 * dt * (p.acceleration[0] + p.acceleration[1]));
    }

    pub fn advance_positions(&mut self, dt: f64) {
        self.particles
            .iter_mut()
            .for_each(|p| p.position += dt * p.velocity + 0.5 * dt.powi(2) * p.acceleration[0]);
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
                let distance = (vector * vector).reduce_add().sqrt();
                let distance_cube = distance.powi(3);

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
    let (tend, dt) = (10.0, 0.001); // end time, timestep

    println!("Running SIMD version");

    let mut bodies = Bodies::new(path);

    bodies.accelerate();
    let (mut ekin, mut epot) = bodies.compute_energy();
    let etot = ekin + epot;

    for step in 1..(tend / dt + 1.0) as i64 {
        bodies.advance_positions(dt);
        epot = bodies.accelerate();
        bodies.advance_velocities(dt);

        // if step % 100 == 0 {
        //     ekin = bodies.compute_k_energy();
        //     let etot_s = ekin + epot;

        //     let de = (etot_s - etot)/etot;
        //     println!(
        //         "t = {:5.2}, Etot = {:.5}, Ekin = {:.5}, Epot = {:.5},  dE/E = {:.5}",
        //         dt * step as f64,
        //         etot_s,
        //         ekin,
        //         epot,
        //         de
        //     );
        // }
    }
    let r = bodies.compute_energy();
    ekin = r.0;
    epot = r.1;
    println!("Final dE/E = {}", ((ekin + epot) - etot) / etot);
}
