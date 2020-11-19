
lines = []

with open("raw_code.txt") as file:
    for line in file:
        lines.append(line[3:])

code = "".join(lines)

print(code)

with open("raw.cpp", "w") as file:
    file.write(code)