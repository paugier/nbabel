
include("microbench_util.jl")

function sum_x(positions)
    result = 0.
    for i in eachindex(positions)
        result += get_x(positions, i)
    end
    return result
end

function get_x(vec, index)
    return vec[index].x
end

function get_xs(vec)
    for i in eachindex(vec)
        get_x(vec, i)
    end
end


function get_objects(vec)
    for i in eachindex(vec)
        vec[i]
    end
end


number_particles = 1000

positions = Vector{Point3D}(undef, number_particles)

x = 0.0
for i in eachindex(positions)
    positions[i] = Point3D(x, 0, 0)
    global x += 1.0
end

print("sum_x(positions)\n")
@btime sum_x(positions)

print("get_x(positions, 2)\n")
@btime get_x(positions, 2)

print("get_xs(positions)\n")
@btime get_xs(positions)

print("get_objects(positions)\n")
@btime get_objects(positions)
