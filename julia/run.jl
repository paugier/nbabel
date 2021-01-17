include(ARGS[1])

if length(ARGS) == 4
    tend = parse(Float64, ARGS[4])
else
    tend = 10.
end

using .NB
NBabel(ARGS[2], tend=tend, show=parse(Bool, ARGS[3]))
