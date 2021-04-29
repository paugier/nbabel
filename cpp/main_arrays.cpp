/*
N-Body integrator using leapfrog scheme
Compile as:
g++ -O4 main.cpp  -o main
Run as:
more input128 | ./main
*/
#include <iostream>
#include <math.h>
#include <numeric>
#include <vector>
#include <array>
typedef double real;
using namespace std;
// Star cluster based on the Star class
// A star cluster contains a number of stars
// stored in the vector S
//
class Cluster {
protected:
public:
  vector<real> m;
  vector<array<real, 3>> r;
  vector<array<real, 3>> v;
  vector<array<real, 3>> a, a0;
  // Computes the acceleration of each star in the cluster
  void acceleration() {
    size_t N = m.size();
    a.reserve(N);
    for (size_t si = 0; si < N; si++)
      std::fill(a[si].begin(), a[si].end(), 0);
    // For each star
    for (size_t si = 0; si < N; si++) {
      // For each remaining star
      for (size_t sj = si+1; sj < N; sj++) {
          array<real, 3> rij;
          // Distance difference between the two stars
          for (int i = 0; i < 3; ++i)
            rij[i] = r[sj][i] - r[si][i];
          // Sum of the dot product
          real init = 0.0;
          real RdotR = inner_product(rij.begin(), rij.end(), rij.begin(), init);
          real apre = 1 / (sqrt(RdotR) * RdotR);
          // Update accelerations
          for (int i = 0; i < 3; ++i) {
            a[si][i] -= m[sj] * apre * rij[i];
            a[sj][i] += m[si] * apre * rij[i];
          }
      }   // end for
    }     // end for
  }       // end acceleration

  // Update positions
  void updatePositions(real dt) {
    size_t N = m.size();
    a0.reserve(N);
    for (size_t si = 0; si < N; si++) {
      // Update the positions, based on the calculated accelerations and
      // velocities
      a0[si] = a[si];
      for (int i = 0; i != 3; ++i) // for each axis (x/y/z)
        r[si][i] += dt * v[si][i] + 0.5 * dt * dt * a0[si][i];
    }
  }

  // Update velocities based on previous and new accelerations
  void updateVelocities(real dt) {
    // Update the velocities based on the previous and old accelerations
    size_t N = m.size();
    for (size_t si = 0; si < N; si++) {
      for (int i = 0; i != 3; ++i)
        v[si][i] += 0.5 * dt * (a0[si][i] + a[si][i]);
      a0 = a;
    }
  }

  // Compute the energy of the system,
  // contains an expensive O(N^2) part which can be moved to the acceleration
  // part where this is already calculated
  array<real, 3> energies() {
    real init = 0;
    array<real, 3> E, rij;
    std::fill(E.begin(), E.end(), 0);

    size_t N = m.size();
    // Kinetic energy
    for (size_t si = 0; si < N; si++)
      E[1] += m[si] *
              inner_product(v[si].begin(), v[si].end(), v[si].begin(), init);
    E[1] *= 0.5;

    // Potential energy
    for (size_t si = 0; si < N; si++) {
      for (size_t sj = si + 1; sj < N; sj++) {
        for (int i = 0; i != 3; ++i)
          rij[i] = r[si][i] - r[sj][i];
        E[2] -= m[si] * m[sj] /
                sqrt(inner_product(rij.begin(), rij.end(), rij.begin(), init));
      }
    }
    E[0] = E[1] + E[2];
    return E;
  }

};

int main(int argc, char* argv[]) {

  Cluster cl;
  real m;
  int dummy;
  array<real, 3> r, v;

  // Read input data from the command line (makeplummer | dumbp)
  do {
    cin >> dummy;
    cin >> m;
    for (int i = 0; i != 3; ++i)
      cin >> r[i];
    for (int i = 0; i != 3; ++i)
      cin >> v[i];
    cl.m.push_back(m);
    cl.r.push_back(r);
    cl.v.push_back(v);
  } while (!cin.eof());

  // Remove the last one
  cl.m.pop_back();
  cl.r.pop_back();
  cl.v.pop_back();

  // Compute initial energu of the system
  array<real, 3> E, E0;
  E0 = cl.energies();
  cerr << "Energies: " << E0[0] << " " << E0[1] << " " << E0[2] << endl;

  // Start time, end time and simulation step
  real t = 0.0;
  real tend;

  if (argc > 1)
    tend = strtod(argv[1], NULL);
  else
    tend = 10.0;

  real dt = 1e-3;
  int k = 0;

  // Initialize the accelerations
  cl.acceleration();

  // Start the main loop
  while (t < tend) {
    // Update positions based on velocities and accelerations
    cl.updatePositions(dt);

    // Get new accelerations
    cl.acceleration();

    // Update velocities
    cl.updateVelocities(dt);

    t += dt;
    k += 1;
    if (k % 100 == 0) {
      E = cl.energies();
      cout << "t= " << t << " E= " << E[0] << " " << E[1] << " " << E[2]
           << " dE/E = " << (E[0] - E0[0]) / E0[0] << endl;
    }
  } // end while

  cout << "number time steps: " << k << endl;

  return 0;
} // end program
