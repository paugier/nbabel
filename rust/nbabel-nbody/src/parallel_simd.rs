use std::path::Path;
use std::{fs, mem};

use packed_simd::*;
use rayon::prelude::*;
use rayon::{ThreadPoolBuilder, current_thread_index};

struct Particle {
    position: f64x4,
    velocity: f64x4,
    mass: f64,
}

pub struct Bodies {
    particles: Vec<Particle>,
    acc_paralell: Vec<Vec<f64x4>>,
    n_threads: usize
}

impl Bodies {
    pub fn new(path_name: &str, n_threads: usize) -> Bodies {
        let file_path = Path::new(path_name);
        let particles: Vec<Particle> = fs::read_to_string(file_path)
            .expect("File not found!")
            .lines()
            .filter(|x| !x.is_empty())
            .map(|x| parse_row(x))
            .collect();

        let len = particles.len();

        Bodies { particles, n_threads, acc_paralell: vec![vec![f64x4::splat(0.0); n_threads]; len] }
    }

    pub fn compute_energy(&self, pe: f64) -> f64{
        let res: f64 = self
            .particles
            .par_iter()
            .map(|p| 0.5 * p.mass * (p.velocity*p.velocity).sum())
            .sum();
        pe + res
    }

    pub fn advance_velocities(&mut self, dt: f64) {
        self.particles
            .par_iter_mut()
            .enumerate()
            .for_each(|(i,p)| {
                p.velocity += 0.5 * dt * (self.acc_paralell[i][0] + self.acc_paralell[i][1]);
            });
    }

    pub fn advance_positions(&mut self, dt: f64) {
        self.particles
            .par_iter_mut()
            .enumerate()
            .for_each(|(i,p)| {
                p.position += dt * p.velocity + 0.5 * dt.powi(2) * self.acc_paralell[i][0];
            });
    }

    pub fn accelerate(&mut self) -> f64 {
        self.acc_paralell
            .par_iter_mut()
            .for_each(|p| {
                p[1] = mem::take(&mut p[0]);
            });

        (0..self.acc_paralell.len())
            .into_par_iter()
            .map(| i | {
                let mut pe = 0.0;
                let idx = current_thread_index().unwrap_or(0);

                let p1 = &self.particles[i];

                for j in i+1 .. self.acc_paralell.len()+1 {
                    let p2 = &self.particles[j];
                    
                    let vector = p1.position - p2.position;
                    let norm2 = (vector*vector).sum();
                    let distance = norm2.sqrt();
                    let distance_cube = norm2 * distance;

                    self.acc_paralell[i][idx] -= (p2.mass / distance_cube) * vector;
                    self.acc_paralell[j][idx] += (p1.mass / distance_cube) * vector;

                    pe -= (p1.mass * p2.mass) / distance;

                }
                -pe
            })
            .sum::<f64>()
    }
}

pub fn parse_row(line: &str) -> Particle {
    let row_vec: Vec<f64> = line
        .split(' ')
        .filter(|s| s.len() > 2)
        .map(|s| s.parse().unwrap())
        .collect();

    Particle {
        position: f64x4::new(row_vec[1], row_vec[2], row_vec[3],0.),
        velocity: f64x4::new(row_vec[4], row_vec[5], row_vec[6],0.),
        mass: row_vec[0],
    }
}

pub fn run(path: &str, n_threads:usize) {
    let mut pe;
    let mut energy = 0.;
    let (tend, dt) = (10.0, 0.001); // end time, timestep
    let (mut old_energy, energy0) = (-0.25, -0.25);
    
    println!("Running Parallel SIMD version");

    ThreadPoolBuilder::new().num_threads(n_threads).build_global().unwrap();
    let mut bodies = Bodies::new(path, n_threads.max(2));

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