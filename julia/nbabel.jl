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

tbeg = 0.0
tend = 10.0
dt = 0.001

function NBabel(fname::String; show=false)

    if show
	    println("Reading file : $fname")
    end

    ID, mass, pos, vel = read_ICs(fname)

    acc = similar(vel)
    acc = compute_acceleration(pos, mass, acc)
    last_acc = copy(acc)

    Ekin, Epot = compute_energy(pos, vel, mass)
    Etot_ICs = Ekin + Epot

    t = 0.0
    nstep = 0

    while t < tend

        pos = update_positions(pos, vel, acc, dt)

        last_acc[:,:] = acc[:,:]

        acc = compute_acceleration(pos, mass, acc)

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

    return size(pos,1)
end

function update_positions(pos::Array{Float64,2}, vel::Array{Float64,2},
                          acc::Array{Float64,2}, dt::Float64)

    @fastmath @inbounds @simd for i=1:size(pos,1)

        pos[i,1] += dt * vel[i,1] + 0.5 * dt^2 * acc[i,1]
        pos[i,2] += dt * vel[i,2] + 0.5 * dt^2 * acc[i,2]
        pos[i,3] += dt * vel[i,3] + 0.5 * dt^2 * acc[i,3]

    end

    return pos
end

function update_velocities(vel::Array{Float64,2}, acc::Array{Float64,2},
						   last_acc::Array{Float64,2}, dt::Float64)

    @fastmath @inbounds @simd for i=1:size(vel,1)

        vel[i,1] += 0.5 * dt * (acc[i,1] + last_acc[i,1])
        vel[i,2] += 0.5 * dt * (acc[i,2] + last_acc[i,2])
        vel[i,3] += 0.5 * dt * (acc[i,3] + last_acc[i,3])

    end

    return vel
end

"""
Force calculation.
"""
function compute_acceleration(pos::Array{Float64,2}, mass::Array{Float64,1},
						      acc::Array{Float64,2})
    N = size(pos,1)

    acc[:,:] .= 0

    pos_i = [0.0,0,0]
    acc_i = [0.0,0,0]

    @inbounds for i = 1:N

        pos_i[:] = pos[i,:]
        acc_i[:] .= 0

        @fastmath @inbounds @simd for j = 1:N
            if i != j

                dx = pos_i[1] - pos[j,1]
                dy = pos_i[2] - pos[j,2]
                dz = pos_i[3] - pos[j,3]

                rinv3 = 1/sqrt((dx^2 + dy^2 + dz^2)^3)

                acc_i[1] -= mass[j] * rinv3 * dx
                acc_i[2] -= mass[j] * rinv3 * dy
                acc_i[3] -= mass[j] * rinv3 * dz
            end
        end

        acc[i,:] = acc_i[:]
    end

    return acc
end


"""
Kinetic and potential energy.
"""
function compute_energy(pos::Array{Float64,2}, vel::Array{Float64,2}, mass::Array{Float64})

    N = size(vel,1)

    Ekin = 0

    @simd for i = 1:N
        @inbounds Ekin += 0.5 * mass[i] * (vel[i,1]^2 + vel[i,2]^2 + vel[i,3]^2)
    end

    Epot = 0.0

    @inbounds for i = 1:N-1
        @fastmath @inbounds for j = i+1:N

            dx = pos[i,1] - pos[j,1]
            dy = pos[i,2] - pos[j,2]
            dz = pos[i,3] - pos[j,3]

            rinv = 1/sqrt(dx^2 + dy^2 + dz^2)
            Epot -= mass[i] * mass[j] * rinv
        end
    end

    return Ekin, Epot
end

function read_ICs(fname::String)

    ICs = readdlm(fname)

    N = size(ICs,1)

    id = Array{Float64}(undef, N)
    mass = Array{Float64}(undef, N)
    pos = Array{Float64}(undef, N,3)
    vel = Array{Float64}(undef, N,3)

    id[:] = ICs[:,1]
    mass[:] = ICs[:,2]

    pos[:,1] = ICs[:,3]
    pos[:,2] = ICs[:,4]
    pos[:,3] = ICs[:,5]

    vel[:,1] = ICs[:,6]
    vel[:,2] = ICs[:,7]
    vel[:,3] = ICs[:,8]

    return id, mass, pos, vel
end


function main(args)
    NBabel(args[1], show=true)
end
main(ARGS)