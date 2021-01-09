
include("microbench_util.jl")

function sum_all_x(vec)
    result = 0.
    for i in eachindex(vec)
        result += get_x(vec, i)
    end
    return result
end

function sum_few_x(vec)
    result = 0.
    for i in 11:length(vec)
        result += get_x(vec, i)
    end
    return result
end

function sum_few_norm2(vec)
    result = 0.
    for i in 11:length(vec)
        result += norm2(vec[i])
    end
    return result
end

function get_x(vec, index)
    return vec[index].x
end

function get_xs(vec)
    x = vec[1].x
    for i in eachindex(vec)
        x = get_x(vec, i)
    end
    return x
end


function get_objects(vec)
    elem = vec[1]
    for i in eachindex(vec)
        elem = vec[i]
    end
    return elem
end


number_particles = 1000

Point = Point3D

points = Vector{Point}(undef, number_particles)

x = 0.0
for i in eachindex(points)
    points[i] = Point(x, 0, 0)
    global x += 1.0
end

print("sum_few_x(points)\n")
@btime sum_few_x(points)

print("sum_all_x(points)\n")
@btime sum_all_x(points)

print("sum_few_norm2(points)\n")
@btime sum_few_norm2(points)

# print("get_x(points, 2)\n")
# @btime get_x(points, 2)

# print("get_xs(points)\n")
# @btime get_xs(points)

# print("get_objects(points)\n")
# @btime get_objects(points)
