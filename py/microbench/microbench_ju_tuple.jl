
using Printf
using BenchmarkTools


function compute_acceleration!(pos, mass, acc)
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

function main()

    number_particles = 1024

    T4f = Tuple{Float64, Float64, Float64, Float64}

    masses = Vector{Float64}(undef, number_particles)
    positions = Vector{T4f}(undef, number_particles)
    accelerations = Vector{T4f}(undef, number_particles)

    x = 0.0
    for i in eachindex(accelerations)
        positions[i] = (x, 0., 0., 0.)
        x += 1.0
        accelerations[i] = (0., 0., 0., 0.)
    end

    @btime compute_acceleration!($accelerations, $masses, $positions)

end

main()