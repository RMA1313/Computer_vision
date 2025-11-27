def count_noisy_pixels(f, g):
    """Count pixels that changed from f to g."""
    noisy = 0
    height = len(f)
    width = len(f[0])
    for y in range(height):
        for x in range(width):
            if g[y][x] != f[y][x]:
                noisy += 1
    return noisy


def count_fixed_noisy_pixels(f, g, k):
    """Count noisy pixels fixed by k."""
    fixed = 0
    height = len(f)
    width = len(f[0])
    for y in range(height):
        for x in range(width):
            was_noisy = g[y][x] != f[y][x]
            if was_noisy and k[y][x] == f[y][x]:
                fixed += 1
    return fixed


def count_damaged_clean_pixels(f, g, k):
    """Count clean pixels that were changed by k."""
    damaged = 0
    height = len(f)
    width = len(f[0])
    for y in range(height):
        for x in range(width):
            was_clean = g[y][x] == f[y][x]
            if was_clean and k[y][x] != f[y][x]:
                damaged += 1
    return damaged
