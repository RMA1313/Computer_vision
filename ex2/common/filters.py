from .utils import clamp_pixel


def get_pixel_safe(image, y, x):
    """Return pixel value while handling borders by replication."""
    height = len(image)
    width = len(image[0])
    if y < 0:
        y = 0
    if y >= height:
        y = height - 1
    if x < 0:
        x = 0
    if x >= width:
        x = width - 1
    return image[y][x]


def median_filter(image, window):
    """Apply a median filter with a square window size."""
    height = len(image)
    width = len(image[0])
    offset = window // 2
    filtered = []
    for y in range(height):
        row = []
        for x in range(width):
            values = []
            for dy in range(-offset, offset + 1):
                for dx in range(-offset, offset + 1):
                    values.append(get_pixel_safe(image, y + dy, x + dx))
            values.sort()
            middle = len(values) // 2
            row.append(values[middle])
        filtered.append(row)
    return filtered


def mean_filter(image, window):
    """Apply a simple mean (average) filter."""
    height = len(image)
    width = len(image[0])
    offset = window // 2
    filtered = []
    for y in range(height):
        row = []
        for x in range(width):
            total = 0
            count = 0
            for dy in range(-offset, offset + 1):
                for dx in range(-offset, offset + 1):
                    total += get_pixel_safe(image, y + dy, x + dx)
                    count += 1
            row.append(total // count)
        filtered.append(row)
    return filtered


def trimmed_alpha_filter(image, window, trim_amount):
    """Apply a trimmed alpha filter by cutting extremes before averaging."""
    height = len(image)
    width = len(image[0])
    offset = window // 2
    filtered = []
    for y in range(height):
        row = []
        for x in range(width):
            values = []
            for dy in range(-offset, offset + 1):
                for dx in range(-offset, offset + 1):
                    values.append(get_pixel_safe(image, y + dy, x + dx))
            values.sort()
            start = trim_amount
            end = len(values) - trim_amount
            if start >= end:
                start = 0
                end = len(values)
            total = 0
            count = 0
            for i in range(start, end):
                total += values[i]
                count += 1
            if count == 0:
                row.append(values[len(values) // 2])
            else:
                row.append(total // count)
        filtered.append(row)
    return filtered


def contra_harmonic_filter(image, window, Q):
    """Apply a contra-harmonic filter."""
    height = len(image)
    width = len(image[0])
    offset = window // 2
    filtered = []
    for y in range(height):
        row = []
        for x in range(width):
            numerator = 0.0
            denominator = 0.0
            for dy in range(-offset, offset + 1):
                for dx in range(-offset, offset + 1):
                    value = get_pixel_safe(image, y + dy, x + dx)
                    numerator += value ** (Q + 1)
                    denominator += value ** Q
            if denominator == 0:
                row.append(get_pixel_safe(image, y, x))
            else:
                row.append(clamp_pixel(numerator / denominator))
        filtered.append(row)
    return filtered
