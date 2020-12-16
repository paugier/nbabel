//! Based on https://github.com/rust-lang/packed_simd/blob/master/examples/nbody/src/main.rs
#![deny(warnings, rust_2018_idioms)]

use std::{env};

fn main() {
    let path = env::args_os()
        .nth(1)
        .and_then(|s| s.into_string().ok())
        .unwrap_or_else(|| "../../data/input128".to_string());

    let alg: usize = if let Some(v) = std::env::args().nth(2) {
        v.parse().expect("second argument must be a usize")
    } else {
        1 // SIMD algorithm
    };

    let n_threads: usize = if let Some(v) = std::env::args().nth(3) {
        v.parse().expect("third argument must be a usize")
    } else {
        4
    };

    nbabel_lib::run(&path, alg, n_threads);
}