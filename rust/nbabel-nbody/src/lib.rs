//! Based on https://github.com/rust-lang/packed_simd/blob/master/examples/nbody/src/lib.rs

#![deny(rust_2018_idioms)]
#![allow(
    clippy::similar_names,
    clippy::excessive_precision,
    clippy::must_use_candidate
)]

pub mod scalar;
pub mod simd;
pub mod parallel_simd;

pub fn run(path: &str, alg: usize, n_threads:usize) {
    match alg {
        0 => scalar::run(path),
        1 => simd::run(path),
        2 => parallel_simd::run(path,n_threads),
        v => panic!("unknown algorithm value: {}", v),
    };
}