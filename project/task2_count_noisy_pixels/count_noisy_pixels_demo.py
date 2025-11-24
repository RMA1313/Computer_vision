import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common import image_io, metrics


def main():
    original_path = input("Enter path to original image: ").strip()
    noisy_path = input("Enter path to noisy image: ").strip()

    original = image_io.load_grayscale_image(original_path)
    noisy = image_io.load_grayscale_image(noisy_path)

    noisy_pixels = metrics.count_noisy_pixels(original, noisy)
    total_pixels = len(original) * len(original[0])
    percent = (noisy_pixels / total_pixels) * 100

    print(f"Noisy pixels: {noisy_pixels} of {total_pixels} ({percent:.2f}%)")


if __name__ == "__main__":
    main()
