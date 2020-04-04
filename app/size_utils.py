import bitmath 
def format_size(num_bytes):
    size = bitmath.Byte(num_bytes)
    return size.best_prefix().format("{value:.2f} {unit}")
