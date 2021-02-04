module NB

using Printf
using DelimitedFiles

tbeg = 0.0
time_step = 0.001

function NBabel(fname::String; tend = 10.0, show=false)
    if show
	    println("Reading file : $fname")
    end
    ID, masses, positions, velocities = read_ICs(fname)
    nb_steps = round(tend / time_step)
    loop(time_step, nb_steps, masses, positions, velocities)
end

function advance_positions(positions, velocities, accelerations, time_step)
    @. positions += time_step * velocities + 0.5 * time_step ^ 2 * accelerations
end

function advance_velocities(velocities, accelerations, accelerations1, time_step)
    @. velocities += 0.5 * time_step * (accelerations + accelerations1)
end

function compute_accelerations(accelerations, masses, positions)
    nb_particules = length(masses)
    vector = [0.0, 0.0, 0.0]
    @inbounds for index_p0=1:nb_particules - 1
        @fastmath @inbounds @simd for index_p1= index_p0 + 1:nb_particules
            # we need to be a bit more low level otherwise it is very slow
            vector[:] = positions[:, index_p0] - positions[:, index_p1]
            # for i in 1:3
            #     vector[i] = positions[i, index_p0] - positions[i, index_p1]
            # end
            distance = sqrt(sum(vector .^ 2))
            # distance = sqrt(vector[1] ^ 2 + vector[2] ^ 2 + vector[3] ^ 2)
            coef = 1.0 / distance ^ 3
            accelerations[:, index_p0] -= coef * masses[index_p1] * vector
            accelerations[:, index_p1] += coef * masses[index_p0] * vector
            # for i in 1:3
            #     accelerations[i, index_p0] -= coef * masses[index_p1] * vector[i]
            #     accelerations[i, index_p1] += coef * masses[index_p0] * vector[i]
            # end
        end
    end
end

function loop(time_step, nb_steps, masses, positions, velocities)
    energy0, _, _ = compute_energies(masses, positions, velocities)

    accelerations = similar(positions)
    accelerations1 = similar(positions)
    fill!(accelerations, 0.)
    fill!(accelerations1, 0.)

    compute_accelerations(accelerations, masses, positions)

    time = 0.0
    energy0, _, _ = compute_energies(masses, positions, velocities)
    energy_previous = energy0
    energy = energy0
    for step= 0:nb_steps-1
        advance_positions(positions, velocities, accelerations, time_step)
        # swap acceleration arrays
        accelerations, accelerations1 = accelerations1, accelerations
        fill!(accelerations, 0.)

        compute_accelerations(accelerations, masses, positions)
        advance_velocities(velocities, accelerations, accelerations1, time_step)
        time += time_step

        if step % 100 == 0
            energy, _, _ = compute_energies(masses, positions, velocities)
            dE = (energy - energy_previous) / energy_previous
            @printf "t = %g, Etot=%g, dE/E=%g \n" time_step * step energy dE

            energy_previous = energy
        end
    end
    return energy, energy0
end

function compute_kinetic_energy(masses, velocities)
    return 0.5 * sum(masses .* vec(sum(velocities.^2, dims=1)))
end


function compute_potential_energy(masses, positions)
    nb_particules = length(masses)
    pe = 0.0
    @inbounds for index_p0=1:nb_particules - 1
        @fastmath @inbounds @simd for index_p1= index_p0 + 1:nb_particules
            mass0 = masses[index_p0]
            mass1 = masses[index_p1]
            vector = positions[:, index_p0] - positions[:, index_p1]
            distance = sqrt(sum(vector .^ 2))
            pe -= (mass0 * mass1) / distance
        end
    end

    return pe
end


function compute_energies(masses, positions, velocities)
    energy_kin = compute_kinetic_energy(masses, velocities)
    energy_pot = compute_potential_energy(masses, positions)
    return energy_kin + energy_pot, energy_kin, energy_pot
end

function read_ICs(fname::String)

    ICs = readdlm(fname)

    N = size(ICs,1)

    id = Array{Float64}(undef, N)
    mass = Array{Float64}(undef, N)
    pos = Array{Float64}(undef, 3, N)
    vel = Array{Float64}(undef, 3, N)

    id[:] = ICs[:,1]
    mass[:] = ICs[:,2]

    pos[1,:] = ICs[:,3]
    pos[2,:] = ICs[:,4]
    pos[3,:] = ICs[:,5]

    vel[1,:] = ICs[:,6]
    vel[2,:] = ICs[:,7]
    vel[3,:] = ICs[:,8]

    return id, mass, pos, vel
end

export NBabel

end
