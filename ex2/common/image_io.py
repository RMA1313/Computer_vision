from PIL import Image


def load_grayscale_image(path):
    """Load an image file and return a 2D list of grayscale pixel values."""
    image = Image.open(path).convert("L")
    width, height = image.size
    pixels = image.load()
    data = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(pixels[x, y])
        data.append(row)
    return data


def save_grayscale_image(pixels, path):
    """Save a 2D list of grayscale values to an image file."""
    if not pixels:
        raise ValueError("Pixel data is empty.")
    height = len(pixels)
    width = len(pixels[0])
    image = Image.new("L", (width, height))
    for y in range(height):
        for x in range(width):
            value = int(pixels[y][x])
            value = max(0, min(255, value))
            image.putpixel((x, y), value)
    image.save(path)
