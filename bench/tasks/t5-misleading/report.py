from parser import parse_line
def summarize(lines):
    total = 0
    for l in lines:
        if not l.strip():
            continue
        n, v = parse_line(l)
        total += v
    return total
