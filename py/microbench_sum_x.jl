
include("microbench_util.jl")

function sum_x(positions)
    result = 0.
    for i in eachindex(positions)
        result += positions[i].x
    end
    return result
end

function get_x(vec, index)
    return vec[index].x
end

number_particles = 1024
nb_steps = 200

positions = Vector{Point3D}(undef, number_particles)

x = 0.0
for i in eachindex(positions)
    positions[i] = Point3D(x, 0, 0)
    global x += 1.0
end

print("sum_x(positions)")
@btime sum_x(positions)
print("get_x(positions, 2)")
@btime get_x(positions, 2)
