import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common import image_io, metrics


def main():
    original_path = input("Enter path to original clean image: ").strip()
    noisy_path = input("Enter path to noisy image: ").strip()
    denoised_path = input("Enter path to denoised image: ").strip()

    original = image_io.load_grayscale_image(original_path)
    noisy = image_io.load_grayscale_image(noisy_path)
    denoised = image_io.load_grayscale_image(denoised_path)

    damaged = metrics.count_damaged_clean_pixels(original, noisy, denoised)
    clean_pixels = (len(original) * len(original[0])) - metrics.count_noisy_pixels(original, noisy)

    percent = 0.0
    if clean_pixels > 0:
        percent = (damaged / clean_pixels) * 100

    print(f"Damaged clean pixels: {damaged} of {clean_pixels} ({percent:.2f}%)")


if __name__ == "__main__":
    main()
