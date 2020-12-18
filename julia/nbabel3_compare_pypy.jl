
module NB

using Printf
using DelimitedFiles

struct Point3D
    x::Float64
    y::Float64
    z::Float64
end
norm2(vec::Point3D) = vec.x^2 + vec.y^2 + vec.z^2
norm(vec::Point3D) = sqrt(norm2(vec))
import Base: +, -, *, zero
-(vec1::Point3D,vec2::Point3D) = Point3D(vec1.x - vec2.x, vec1.y - vec2.y, vec1.z - vec2.z)
+(vec1::Point3D,vec2::Point3D) = Point3D(vec1.x + vec2.x, vec1.y + vec2.y, vec1.z + vec2.z)
*(c::Real, vec1::Point3D) = Point3D(c * vec1.x, c * vec1.y, c * vec1.z)
*(vec1::Point3D, c::Real) = c * vec1
zero(T::Type{Point3D}) = Point3D(0, 0, 0)

struct Point4D
    x::Float64
    y::Float64
    z::Float64
    w::Float64
end
Point4D(x,y,z) = Point4D(x, y, z, 0)
norm2(vec::Point4D) = vec.x^2 + vec.y^2 + vec.z^2 + vec.w^2
norm(vec::Point4D) = sqrt(norm2(vec))
import Base: +, -, *, zero
-(vec1::Point4D,vec2::Point4D) = Point4D(vec1.x - vec2.x, vec1.y - vec2.y, vec1.z - vec2.z, vec1.w - vec2.w)
+(vec1::Point4D,vec2::Point4D) = Point4D(vec1.x + vec2.x, vec1.y + vec2.y, vec1.z + vec2.z, vec1.w + vec2.w)
*(c::Real, vec1::Point4D) = Point4D(c * vec1.x, c * vec1.y, c * vec1.z, c * vec1.w)
*(vec1::Point4D, c::Real) = c * vec1
zero(T::Type{Point4D}) = Point4D(0, 0, 0, 0)

function NBabel(fname::String; tend=10., dt=0.001, show=false)

    if show
	    println("Reading file : $fname")
    end

    masses, positions, velocities = read_ICs(fname)

    return NBabelCalcs(masses, positions, velocities, tend=tend, dt=dt, show=show)
end

function NBabelCalcs(masses, positions, velocities; tend=10., dt=0.001, show=false)
    accelerations = Vector{eltype(velocities)}(undef, length(velocities))
    compute_acceleration!(positions, masses, accelerations)
    last_acc = copy(accelerations)

    Ekin, Epot = compute_energy(positions, velocities, masses)
    Etot_ICs = Ekin + Epot
    Etot_previous = Etot_ICs

    t = 0.0
    nstep = 0

    while t < tend

        update_positions!(positions, velocities, accelerations, dt)

        last_acc .= accelerations

        compute_acceleration!(positions, masses, accelerations)

        update_velocities!(velocities, accelerations, last_acc, dt)

        t += dt
        nstep += 1

        if show && nstep % 100 == 1

            Ekin, Epot = compute_energy(positions, velocities, masses)
            Etot = Ekin + Epot
            dE = (Etot - Etot_previous) / Etot_previous
            Etot_previous = Etot

            @printf "t = %5.2f, Etot = %.10f, dE = %+.10f \n" t Etot dE
        end
    end

    Ekin, Epot = compute_energy(positions, velocities, masses)
    Etot = Ekin + Epot
    return Ekin, Epot, Etot
end

function update_positions!(positions, velocities, accelerations, dt)
    for i in eachindex(positions)
        positions[i] = positions[i] + (0.5 * accelerations[i] * dt + velocities[i]) * dt
    end
    nothing
end

function update_velocities!(velocities, accelerations, last_acc, dt)
    for i in eachindex(velocities)
        velocities[i] = velocities[i] + 0.5 * dt * (accelerations[i] + last_acc[i])
    end
    nothing
end

#
# Force calculation.
#
function compute_acceleration!(positions, masses, accelerations)
    N = length(positions)

    for i in eachindex(accelerations)
        accelerations[i] = zero(eltype(accelerations))
    end

    for i = 1:N - 1
        for j = i + 1:N
            dr = positions[i] - positions[j]
            rinv3 = 1 / norm(dr)^3
            accelerations[i] = accelerations[i] - masses[i] * rinv3 * dr
            accelerations[j] = accelerations[j] + masses[j] * rinv3 * dr
        end
    end
    nothing
end



#
# Kinetic and potential energy.
#
function compute_energy(positions, velocities, masses)
    N = length(velocities)

    Ekin = 0.0
    for i = 1:N
        Ekin += 0.5 * masses[i] * norm2(velocities[i])
    end

    Epot = 0.
    for i = 1:N - 1
        for j = i + 1:N
            dr = positions[i] - positions[j]
            rinv = 1 / norm(dr)
            Epot -= masses[i] * masses[j] * rinv
        end
    end
    return Ekin, Epot
end

function read_ICs(fname::String)

    ICs = readdlm(fname)

    N = size(ICs, 1)

    Point = Point3D

    positions = Vector{Point}(undef, N)
    velocities = Vector{Point}(undef, N)

    masses = Vector{Float64}(undef, N)
    masses .= ICs[:,2]

    for i in axes(ICs, 1)
        positions[i] = Point(ICs[i, 3], ICs[i, 4], ICs[i, 5])
    end

    for i in axes(ICs, 1)
        velocities[i] = Point(ICs[i, 6], ICs[i, 7], ICs[i, 8])
    end

    return masses, positions, velocities
end

export NBabel

end
