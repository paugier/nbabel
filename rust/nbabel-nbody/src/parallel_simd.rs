use std::{mem};

use crate::simd;
use rayon::prelude::*;
use rayon::ThreadPoolBuilder;

struct ParallelBodies {
    bodies: simd::Bodies,
    n_threads: usize
}

impl ParallelBodies {
    pub fn new(path_name: &str, n_threads: usize) -> ParallelBodies {
        ParallelBodies { bodies: simd::Bodies::new(path_name) , n_threads}
    }

    pub fn compute_energy(&self, pe: f64) -> f64{
        let res: f64 = self
            .bodies
            .particles
            .par_iter()
            .map(|p| 0.5 * p.mass * (p.velocity*p.velocity).sum())
            .sum();
        pe + res
    }

    pub fn advance_velocities(&mut self, dt: f64) {
        self.bodies
            .particles
            .par_iter_mut()
            .for_each(|p| {
                p.velocity += 0.5 * dt * (p.acceleration[0] + p.acceleration[1]);
            });
    }

    pub fn advance_positions(&mut self, dt: f64) {
        self.bodies
            .particles
            .par_iter_mut()
            .for_each(|p| {
                p.position += dt * p.velocity + 0.5 * dt.powi(2) * p.acceleration[0];
            });
    }

    pub fn accelerate(&mut self) -> f64 {
        self.bodies
            .particles
            .par_iter_mut()
            .for_each(|p| {
                p.acceleration[1] = mem::take(&mut p.acceleration[0]);
            });

        self.bodies
            .particles
            .par_chunks_mut(self.n_threads)
            .map(|mut particles| {
                let mut pe = 0.0;

                while let Some((p1, rest)) = particles.split_first_mut(){
                    particles = rest;

                    for p2 in particles.iter_mut() {
                        let vector = p1.position - p2.position;
                        let norm2 = (vector*vector).sum();
                        let distance = norm2.sqrt();
                        let distance_cube = norm2 * distance;
        
                        p1.acceleration[0] -= (p2.mass / distance_cube) * vector;
                        p2.acceleration[0] += (p1.mass / distance_cube) * vector;
        
                        pe -= (p1.mass * p2.mass) / distance;
                    }
                }
                -pe
            })
            .sum::<f64>()
    }
}

pub fn run(path: &str, n_threads:usize) {
    let mut pe;
    let mut energy = 0.;
    let (tend, dt) = (10.0, 0.001); // end time, timestep
    let (mut old_energy, energy0) = (-0.25, -0.25);
    
    println!("Running Parallel SIMD version");

    ThreadPoolBuilder::new().num_threads(n_threads).build_global().unwrap();
    let mut bodies = ParallelBodies::new(path, n_threads);

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