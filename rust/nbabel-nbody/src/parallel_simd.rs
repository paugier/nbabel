//! Based on https://github.com/rust-lang/packed_simd/blob/master/examples/nbody/src/simd.rs
//! and https://github.com/paugier/nbabel/blob/master/julia/nbabel5_threads.jl

use std::path::Path;
use std::{fs, sync::mpsc::channel};

use wide::f64x4;

use threadpool::ThreadPool;

#[derive(Clone)]
pub struct Particle {
    position: f64x4,
    velocity: f64x4,
    acceleration: [f64x4; 2],
    mass: f64,
}

pub struct Bodies {
    particles: Vec<Particle>,
    pool: ThreadPool,
    accs: Vec<Vec<f64x4>>,
    splits: Vec<(usize, usize)>,
}

fn accelerated_chuncked(split: (usize, usize), pos: &[f64x4], mass: &[f64]) -> Vec<f64x4> {
    let N = pos.len();
    let mut acc = vec![f64x4::splat(0.0); N];

    for i in split.0..split.1 {
        let pos_i = pos[i];
        let m_i = mass[i];

        for j in i + 1..N {
            let mut dr = pos_i - pos[j];
            let rinv3 = (1. / (dr * dr).reduce_add().sqrt()).powi(3);
            dr = dr * rinv3;
            acc[i] -= mass[j] * dr;
            acc[j] += m_i * dr;
        }
    }
    acc
}

// Make splits to separate slices of the particles
fn make_splits(n: usize, k: usize) -> Vec<(usize, usize)> {
    let iter = (0..1).chain(
        (0..k)
            .map(|i| f64::ceil((n as f64) * (1. - f64::sqrt((i as f64) / (k as f64)))) as usize)
            .rev(),
    );

    iter.clone().zip(iter.skip(1)).collect()
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

        let k = num_cpus::get();
        let n = (&particles).len();
        let splits = make_splits(n, k);
        let accs = vec![vec![f64x4::splat(0.0); n]; k];

        Bodies {
            particles,
            pool: ThreadPool::new(k),
            accs,
            splits,
        }
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

    pub fn accelerate(&mut self) {
        let (tx, rx) = channel();

        let positions: Vec<f64x4> = self.particles.iter().map(|p| p.position).collect();
        let masses: Vec<f64> = self.particles.iter().map(|p| p.mass).collect();

        for (i, split) in self.splits.iter().enumerate() {
            let tx = tx.clone();
            let split = *split;
            let positions = positions.clone();
            let masses = masses.clone();

            self.pool.execute(move || {
                let acc_i = accelerated_chuncked(split, &positions, &masses);
                tx.send((i, acc_i)).unwrap();
            });
        }

        let k = self.splits.len();

        // Waiting for the values and replacing them without allocaction of a new Vec
        for (i, acc_k) in rx.iter().take(k) {
            self.accs[i]
                .iter_mut()
                .zip(acc_k.iter())
                .for_each(|(e, a)| *e = *a);
        }

        // Transposing Vec<Vec<f64x4>> from [K;N] to [N;K] and summing over K for each N
        let accs = &self.accs;
        let accs_par =
            (0..accs[0].len()).map(|i| accs.iter().map(|row| row[i]).reduce(|a, b| a + b));

        // Replacing new value of acc and storing the previous one
        self.particles
            .iter_mut()
            .zip(accs_par)
            .filter(|(p, a)| a.is_some())
            .for_each(|(p, a)| {
                p.acceleration[1] = p.acceleration[0];
                p.acceleration[0] = a.unwrap();
            });
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

    println!("Running Parallel SIMD version");

    let mut bodies = Bodies::new(path);

    bodies.accelerate();

    let (mut ekin, mut epot) = bodies.compute_energy();
    let etot = ekin + epot;

    for step in 1..(tend / dt + 1.0) as i64 {
        bodies.advance_positions(dt);
        bodies.accelerate();
        bodies.advance_velocities(dt);

        // if step % 100 == 0 {
        //     let r = bodies.compute_energy();
        //     ekin = r.0;
        //     epot = r.1;
        //     let etot_s = ekin + epot;
        //     let de = (etot_s - etot)/etot;

        //     println!(
        //         "t = {:5.2}, Etot = {:.5}, Ekin = {:.5}, Epot = {:.5},  dE/E = {:.10}",
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
