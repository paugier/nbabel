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
    k = Threads.nthreads()
    splits = splitter(size(pos, 1), k)
    accs = [similar(vel) for _ in 1:k]
    acc = similar(vel)
    acc = compute_acceleration(pos, mass, acc, splits, accs)
    last_acc = copy(acc)

    Ekin, Epot = compute_energy(pos, vel, mass)
    Etot_ICs = Ekin + Epot

    t = 0.0
    nstep = 0

    while t < tend

        pos = update_positions(pos, vel, acc, dt)

        acc, last_acc = last_acc, acc

        acc = compute_acceleration(pos, mass, acc, splits, accs)

        vel = update_velocities(vel, acc, last_acc, dt)
        
        t += dt
        nstep += 1

        if show && nstep%100 == 0

            Ekin, Epot = compute_energy(pos, vel, mass)
            Etot = Ekin + Epot
            dE = (Etot - Etot_ICs)/Etot_ICs

            @printf "t = %g, Etot=%g, Ekin=%g, Epot=%g, dE=%g \n" t Etot Ekin Epot dE
        end
    end

    Ekin, Epot = compute_energy(pos, vel, mass)
    Etot = Ekin + Epot
    return (; Ekin, Epot, Etot)
end

function update_positions(pos, vel, acc, dt)
    N = length(pos)

    @inbounds @simd for i in 1:N
        pos[i] = @. (0.5 * acc[i] * dt + vel[i])*dt + pos[i]
    end

    return pos
end

function update_velocities(vel, acc, last_acc, dt)
    N = length(vel)

    @inbounds @simd for i in 1:N
        vel[i] = @. vel[i] + 0.5 * dt * (acc[i] + last_acc[i])
    end

    return vel
end

"""
Force calculation.
"""
function splitter(n, k)
    xz = [0; reverse([Int(ceil(n*(1 - sqrt(i/k)))) for i in 1:k-1]); n]
    return [xz[i]+1:xz[i+1] for i in 1:k]
end

function chunk_compute_acceleration(r, pos, mass, acc)
    N = length(pos)
    @inbounds for i in 1:N
        acc[i] = (0.0, 0.0, 0.0, 0.0)
    end

    @inbounds for i in r

        pos_i = pos[i]
        m_i = mass[i]

        @inbounds @simd for j = i+1:N
            dr = pos_i .- pos[j]

            rinv3 = 1/sqrt(sum(dr .^ 2)) ^ 3
            dr = rinv3 .* dr

            acc[i] = @. acc[i] - mass[j] * dr
            acc[j] = @. acc[j] + m_i * dr
        end
    end

    return acc
end

function compute_acceleration(pos, mass, acc, splits, accs)
    k = Threads.nthreads()
    # tasks = Vector{Task}(undef, k - 1)
    # for i in 1:k-1
    @sync for i in 1:k
        @async @Threads.spawn chunk_compute_acceleration(splits[i], pos, mass, accs[i])
        # tasks[i] = @Threads.spawn chunk_compute_acceleration(splits[i], pos, mass, accs[i])
    end
    # chunk_compute_acceleration(splits[end], pos, mass, accs[end])
    # for i in 1:k-1
    #     wait(tasks[i])
    # end

    acc .= accs[1]
    @inbounds @simd for i in 2:k
        accs_i = accs[i]
        for j in eachindex(acc)
            acc[j] = acc[j] .+ accs_i[j]
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
        @inbounds for j = i+1:N
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
