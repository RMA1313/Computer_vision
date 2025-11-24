import random

from .utils import copy_image, clamp_pixel


def add_salt_and_pepper_noise(image, noise_level):
    """Add both salt and pepper noise to an image."""
    noisy = copy_image(image)
    height = len(noisy)
    width = len(noisy[0])
    for y in range(height):
        for x in range(width):
            r = random.random()
            if r < noise_level:
                noisy[y][x] = 0
            elif r > 1 - noise_level:
                noisy[y][x] = 255
    return noisy


def add_salt_noise(image, noise_level):
    """Add only salt noise (white pixels)."""
    noisy = copy_image(image)
    height = len(noisy)
    width = len(noisy[0])
    for y in range(height):
        for x in range(width):
            if random.random() < noise_level:
                noisy[y][x] = 255
    return noisy


def add_pepper_noise(image, noise_level):
    """Add only pepper noise (black pixels)."""
    noisy = copy_image(image)
    height = len(noisy)
    width = len(noisy[0])
    for y in range(height):
        for x in range(width):
            if random.random() < noise_level:
                noisy[y][x] = 0
    return noisy


def add_gaussian_noise(image, mean, std_dev):
    """Add Gaussian noise with given mean and standard deviation."""
    noisy = copy_image(image)
    height = len(noisy)
    width = len(noisy[0])
    for y in range(height):
        for x in range(width):
            noise = random.gauss(mean, std_dev)
            noisy_value = noisy[y][x] + noise
            noisy[y][x] = clamp_pixel(noisy_value)
    return noisy


def add_uniform_noise(image, min_value, max_value):
    """Add uniform noise within a range."""
    noisy = copy_image(image)
    height = len(noisy)
    width = len(noisy[0])
    for y in range(height):
        for x in range(width):
            noise = random.uniform(min_value, max_value)
            noisy_value = noisy[y][x] + noise
            noisy[y][x] = clamp_pixel(noisy_value)
    return noisy
