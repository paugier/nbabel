/*
N-Body integrator using leapfrog scheme
Compile as:
g++ -O4 main_opt_all.cpp  -o main
Run as:
more input128 | ./main
*/
/*
 Optimisation de l'algorithme de calcul d'accélération :
 Voir main_opt_algo.cpp
 +
 Divers optimisations classiques :
 
 - Pas d'allocation dynamique dans les boucles.
 - Pas de vector(3) pour représenter un vecteur mais plutôt array(3) qui est contigu en mémoire
 - Pas de classe "Star" pour éviter les problèmes de contiguité en mémoire, le tableau m, r, ... doivent être contigu respectivement pour être vectorisable par le compilateur.
 - Utilisation de pow(-1.5) au lieu de /sqrt(^3). Même si SQRT est souvent plus performant que POW, ici on utilise 1 opération contre 4.
 - Optimisation divers comme "real dt2 = 0.5 * dt * dt;" en dehors de la boucle qui permet d'éviter de recalculer cette constante. En réalité, le compilateur est assez intelligent pour le faire lui même, c'est plus une habitude.
 
 A noter qu'il serait possible de rendre le code plus lisible en ajoutant une classe Vecteur (double[3]) et implémenter les opérateurs mathématiques (operator+ ...)
 Ainsi, une boucle
  for (int k = 0; k < 3; ++k) rij[k] = ri[k] - r[j][k];
 pourrait se simplifier par (avec les mêmes performances)
  rij = ri - r[j];
 
 Pour info, je suis programmeur C donc le C++ n'est pas ma spécialité...
 Il y a surement plein d'optimisations possibles, je laisserais d'autres collègues en proposer.
 
 Si la parallélisation est autorisé, l'utilisation de OMP pourrait grandement améliorer l'efficacité du code. Un simple #pragma omp parallel num_threads(MAX) au dessus de certaine boucle par exemple.
 
 */
#include <iostream>
#include <math.h>
#include <numeric>
#include <vector>
#include <array>
using namespace std;

typedef double real;
typedef array<real, 3> real3;

inline real mag(real3 a)
{
  return a[0]*a[0] + a[1]*a[1] + a[2]*a[2];
}

// Star cluster based on the Star class
// A star cluster contains a number of stars
// stored in the vector S
//
class Cluster {
protected:
  vector<real> m;
  vector<real3> r;
  vector<real3> v;
  vector<real3> a;
  vector<real3> a0;
  real3 zero;
  int size;
public:
  
  Cluster() : size(0)
  {
    for (int i = 0; i < 3; ++i)
      zero[i] = 0.0;
  }
  
  void fill(vector<real>& m_in, vector<real3>& r_in, vector<real3>& v_in)
  {
    size = m_in.size() - 1;
    m.resize(size);
    r.resize(size);
    v.resize(size);
    a.resize(size);
    a0.resize(size);
    for (int i = 0; i < size; ++i) {
      m[i] = m_in[i];
      r[i] = r_in[i];
      v[i] = v_in[i];
    }
  }
  
  size_t Size(void) {return size;}
  
  // Computes the acceleration of each star in the cluster
  void acceleration()
  {
    for (int i = 0; i < size; ++i)
      a[i] = zero;
    // For each star
    real3 rij, ri;
    real RdotR;
    // For each star
    for (int i = 0; i < size - 1; ++i) {
      ri = r[i];
      for (int j = i + 1; j < size; ++j) {
        // Distance difference between the two stars
        for (int k = 0; k < 3; ++k)
          rij[k] = ri[k] - r[j][k];
        // Sum of the dot product
        RdotR = pow(mag(rij), -1.5);
        // Update accelerations
        for (int k = 0; k < 3; ++k)
        {
          a[i][k] -= m[j] * RdotR * rij[k];
          a[j][k] += m[i] * RdotR * rij[k];
        }
      }   // si != sj
    }     // end for
  }       // end acceleration

  // Update positions
  void updatePositions(real dt)
  {
    real dt2 = 0.5 * dt * dt;
    for (int i = 0; i < size; ++i) {
      // Update the positions, based on the calculated accelerations and
      // velocities
      a0[i] = a[i];
      for (int k = 0; k < 3; ++k) // for each axis (x/y/z)
        r[i][k] += dt * v[i][k] + dt2 * a0[i][k];
    }
  }

  // Update velocities based on previous and new accelerations
  void updateVelocities(real dt)
  {
    // Update the velocities based on the previous and old accelerations
    real dtc = 0.5 * dt;
    for (int i = 0; i < size; ++i) {
      for (int k = 0; k < 3; ++k)
        v[i][k] += dtc * (a0[i][k] + a[i][k]);
      a0[i] = a[i];
    }
  }

  // Compute the energy of the system,
  // contains an expensive O(N^2) part which can be moved to the acceleration
  // part where this is already calculated
  real3 energies(void)
  {
    real3 rij;
    real3 E = zero;

    // Kinetic energy
    for (int i = 0; i < size; ++i)
      E[1] += 0.5 * m[i] * mag(v[i]);

    // Potential energy
    for (int i = 0; i < size; ++i) {
      real m2 = m[i] * m[i];
      for (int j = i + 1; j < size; ++j) {
        for (int k = 0; k < 3; ++k)
          rij[k] = r[i][k] - r[j][k];
        E[2] -= m2 /
                sqrt(mag(rij));
      }
    }
    E[0] = E[1] + E[2];
    return E;
  }

  // Print function
  friend ostream &operator<<(ostream &so, Cluster &cl) {
    for (int i = 0; i < cl.Size(); ++i)
      so << cl.m[i] << " " << cl.r[i][0] << " " << cl.r[i][1] << " " << cl.r[i][2] << " "
    << cl.v[i][0] << " " << cl.v[i][1] << " " << cl.v[i][2] << endl;
    return so;
  }
};

int main(int argc, char* argv[]) {

  Cluster cl;
  int dummy;
  real m;
  real3 r, v;
  vector<real> tm;
  vector<real3> tr, tv;

  // Read input data from the command line (makeplummer | dumbp)
  do {
    cin >> dummy;
    cin >> m;
    for (int i = 0; i < 3; ++i)
      cin >> r[i];
    for (int i = 0; i < 3; ++i)
      cin >> v[i];
    tm.push_back(m);
    tr.push_back(r);
    tv.push_back(v);
  } while (!cin.eof());

  // Init class
  cl.fill(tm, tr, tv);
  
  // Compute initial energu of the system
  real3 E, E0;
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
