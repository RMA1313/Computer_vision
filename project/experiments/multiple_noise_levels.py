import csv
import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common import filters, image_io, metrics, noise


def ensure_results_dir():
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    return results_dir


def main():
    image_path = input("Enter path to original clean image: ").strip()
    original = image_io.load_grayscale_image(image_path)

    noise_levels = [0.01, 0.03, 0.05, 0.1]
    results_dir = ensure_results_dir()

    table_path = os.path.join(results_dir, "noise_levels.csv")
    with open(table_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["noise_level", "noisy_pixels", "fixed_pixels", "damaged_clean_pixels"])

        for level in noise_levels:
            noisy = noise.add_salt_and_pepper_noise(original, level)
            filtered = filters.median_filter(noisy, 3)

            noisy_pixels = metrics.count_noisy_pixels(original, noisy)
            fixed_pixels = metrics.count_fixed_noisy_pixels(original, noisy, filtered)
            damaged_clean = metrics.count_damaged_clean_pixels(original, noisy, filtered)

            noisy_name = os.path.join(results_dir, f"noisy_level_{str(level).replace('.', '_')}.png")
            filtered_name = os.path.join(results_dir, f"filtered_level_{str(level).replace('.', '_')}.png")
            image_io.save_grayscale_image(noisy, noisy_name)
            image_io.save_grayscale_image(filtered, filtered_name)

            writer.writerow([level, noisy_pixels, fixed_pixels, damaged_clean])
            print(f"Level {level}: noisy={noisy_pixels}, fixed={fixed_pixels}, damaged={damaged_clean}")
            print(f"Saved noisy to {noisy_name} and filtered to {filtered_name}")

    print(f"Table saved to {table_path}")


if __name__ == "__main__":
    main()
