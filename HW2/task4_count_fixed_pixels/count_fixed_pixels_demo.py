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

    fixed = metrics.count_fixed_noisy_pixels(original, noisy, denoised)
    total_noisy = metrics.count_noisy_pixels(original, noisy)

    percent = 0.0
    if total_noisy > 0:
        percent = (fixed / total_noisy) * 100

    print(f"Fixed noisy pixels: {fixed} of {total_noisy} ({percent:.2f}%)")


if __name__ == "__main__":
    main()
