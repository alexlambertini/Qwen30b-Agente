def parse_line(line):
    name, value = line.split(",")
    return name.strip(), float(value)
