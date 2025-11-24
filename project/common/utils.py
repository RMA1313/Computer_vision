def copy_image(image):
    """Deep copy a 2D list of pixel values."""
    new_image = []
    for row in image:
        new_row = []
        for value in row:
            new_row.append(value)
        new_image.append(new_row)
    return new_image


def clamp_pixel(value):
    """Clamp a pixel value to the 0-255 range."""
    if value < 0:
        return 0
    if value > 255:
        return 255
    return int(value)
