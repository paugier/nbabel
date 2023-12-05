module NB
"""
This is an implementation of the NBabel N-body problem.
See nbabel.org for more information.

This is 'naive & native' Julia with type and loop annotations for
fastmath and vectorization, because this is really is no effort.

Without annotations the code will be as slow as naive Python/IDL.

    include("nbabel.jl")
    NBabel("IC/input128", show=true)

Julius Donnert INAF-IRA 2017
"""

using Printf
using DelimitedFiles

export NBabel

function NBabel(fname::String; tend = 10.0, dt = 0.001, show=false)

    if show
	    println("Reading file : $fname")
    end

    ID, mass, pos, vel = read_ICs(fname)

    return NBabelCalcs(ID, mass, pos, vel, tend, dt, show)
end

function NBabelCalcs(ID, mass, pos, vel, tend = 10.0, dt = 0.001, show=false)
    acc = similar(vel)
    acc = compute_acceleration(pos, mass, acc)
    last_acc = copy(acc)

    Ekin, Epot = compute_energy(pos, vel, mass)
    Etot_ICs = Ekin + Epot
    Etot_previous = Etot_ICs

    t = 0.0
    nstep = 0

    while t < tend

        pos = update_positions(pos, vel, acc, dt)

        acc, last_acc = last_acc, acc

        acc = compute_acceleration(pos, mass, acc)

        vel = update_velocities(vel, acc, last_acc, dt)

        t += dt
        nstep += 1

        if show && nstep%100 == 0
            Ekin, Epot = compute_energy(pos, vel, mass)
            Etot = Ekin + Epot
            dE = (Etot - Etot_previous)/Etot_previous
            @printf "t = %g, Etot=%.7g, Ekin=%g, Epot=%g, dE/E=%e \n" t Etot Ekin Epot dE
            Etot_previous = Etot
        end
    end

    Ekin, Epot = compute_energy(pos, vel, mass)
    Etot = Ekin + Epot
    @printf "(E - E_init)/E_init = %g %%\n" 100 * (Etot - Etot_ICs) / Etot_ICs

    return (; Ekin, Epot, Etot)
    # return size(pos,1)
end

function update_positions(pos, vel, acc, dt)
    N = length(pos)

    @fastmath @inbounds @simd for i in 1:N
        pos[i] = @. (0.5 * acc[i] * dt + vel[i])*dt + pos[i]
    end

    return pos
end

function update_velocities(vel, acc, last_acc, dt)
    N = length(vel)

    @fastmath @inbounds @simd for i in 1:N
        vel[i] = @. vel[i] + 0.5 * dt * (acc[i] + last_acc[i])
    end

    return vel
end

"""
Force calculation.
"""
function compute_acceleration(pos, mass, acc)
    N = length(pos)
    @inbounds for i in 1:N
        acc[i] = (0.0, 0.0, 0.0, 0.0)
    end

    @inbounds for i in 1:N

        pos_i = pos[i]
        m_i = mass[i]

        @fastmath @inbounds @simd for j = i+1:N
            dr = pos_i .- pos[j]

            rinv3 = 1/sqrt(sum(dr .^ 2)) ^ 3
            dr = rinv3 .* dr

            acc[i] = @. acc[i] - mass[j] * dr
            acc[j] = @. acc[j] + m_i * dr
        end
    end

    return acc
end


"""
Kinetic and potential energy.
"""
function compute_energy(pos, vel, mass)

    N = length(vel)

    Ekin = 0.0

    @simd for i = 1:N
        @inbounds Ekin += 0.5 * mass[i] * sum(vel[i] .^ 2)
    end

    Epot = 0.0

    @inbounds for i = 1:N-1
        pos_i = pos[i]
        @fastmath @inbounds for j = i+1:N
            dr = pos_i .- pos[j]

            rinv = 1/sqrt(sum(dr .^ 2))
            Epot -= mass[i] * mass[j] * rinv
        end
    end

    return Ekin, Epot
end

function read_ICs(fname)
    ICs = readdlm(fname)

    N = size(ICs,1)

    pos = Vector{Tuple{Float64, Float64, Float64, Float64}}(undef, N)
    vel = Vector{Tuple{Float64, Float64, Float64, Float64}}(undef, N)

    id = ICs[:, 1]
    mass = ICs[:, 2]

    for i in axes(ICs, 1)
        pos[i] = (ICs[i, 3], ICs[i, 4], ICs[i, 5], 0.0)
    end

    for i in axes(ICs, 1)
        vel[i] = (ICs[i, 6], ICs[i, 7], ICs[i, 8], 0.0)
    end

    return id, mass, pos, vel
end

end # module
