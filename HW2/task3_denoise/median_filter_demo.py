import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common import filters, image_io, metrics


def main():
    original_path = input("Enter path to original clean image: ").strip()
    noisy_path = input("Enter path to noisy image: ").strip()

    original = image_io.load_grayscale_image(original_path)
    noisy = image_io.load_grayscale_image(noisy_path)

    output_dir = os.path.join(os.path.dirname(__file__), "sample_outputs")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for window in [3, 5]:
        filtered = filters.median_filter(noisy, window)
        output_path = os.path.join(output_dir, f"median_window_{window}.png")
        image_io.save_grayscale_image(filtered, output_path)

        fixed = metrics.count_fixed_noisy_pixels(original, noisy, filtered)
        damaged = metrics.count_damaged_clean_pixels(original, noisy, filtered)
        print(f"Median window {window}: fixed noisy pixels = {fixed}, damaged clean pixels = {damaged}. Saved to {output_path}")


if __name__ == "__main__":
    main()
