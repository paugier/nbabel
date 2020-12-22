"""

Main.NB.MutablePoint3D  2.579159 seconds (210.76 M allocations: 6.281 GiB, 5.43% gc time)
Main.NB.Point3D  0.671755 seconds
Main.NB.Point4D  0.523249 seconds

- Huge effect of adding the mutable keyword (3.8 x longer)
- Using Point4D instead of Point3D leads to a 1.3 speedup.

"""

using Printf
using BenchmarkTools

mutable struct MutablePoint3D
    x::Float64
    y::Float64
    z::Float64
end
norm2(vec::MutablePoint3D) = vec.x^2 + vec.y^2 + vec.z^2
norm(vec::MutablePoint3D) = sqrt(norm2(vec))
import Base: +, -, *, zero
-(vec1::MutablePoint3D,vec2::MutablePoint3D) = MutablePoint3D(vec1.x - vec2.x, vec1.y - vec2.y, vec1.z - vec2.z)
+(vec1::MutablePoint3D,vec2::MutablePoint3D) = MutablePoint3D(vec1.x + vec2.x, vec1.y + vec2.y, vec1.z + vec2.z)
*(c::Real, vec1::MutablePoint3D) = MutablePoint3D(c * vec1.x, c * vec1.y, c * vec1.z)
*(vec1::MutablePoint3D, c::Real) = c * vec1
zero(T::Type{MutablePoint3D}) = MutablePoint3D(0, 0, 0)


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


function compute_acceleration!(positions, masses, accelerations)
    N = length(positions)

    for i in eachindex(accelerations)
        accelerations[i] = zero(eltype(accelerations))
    end

    for i = 1:N - 1
        for j = i + 1:N
            dr = positions[i] - positions[j]
            rinv3 = 1 / norm(dr)^3
            accelerations[i] -= masses[i] * rinv3 * dr
            accelerations[j] += masses[j] * rinv3 * dr
        end
    end
    nothing
end

function main(Point)
    print(Point)

    number_particles = 1024
    nb_steps = 200

    masses = Vector{Float64}(undef, number_particles)
    positions = Vector{Point}(undef, number_particles)
    accelerations = Vector{Point}(undef, number_particles)

    x = 0.0
    for i in eachindex(accelerations)
        positions[i] = Point(x, 0, 0)
        x += 1.0
        accelerations[i] = zero(eltype(accelerations))
    end

    @btime compute_acceleration!($accelerations, $masses, $positions)

end
