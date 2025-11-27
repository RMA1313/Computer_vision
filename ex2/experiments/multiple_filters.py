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


def apply_filters(original, noisy):
    """Apply several filters and return metric rows."""
    rows = []

    # Median filter with window 3
    median_result = filters.median_filter(noisy, 3)
    rows.append(("median_3", median_result))

    # Mean filter with window 3
    mean_result = filters.mean_filter(noisy, 3)
    rows.append(("mean_3", mean_result))

    # Trimmed alpha filter: window 3, trim 1 pixel from each side
    trimmed_result = filters.trimmed_alpha_filter(noisy, 3, 1)
    rows.append(("trimmed_alpha_3_trim1", trimmed_result))

    # Contra-harmonic filter with Q=1
    contra_result = filters.contra_harmonic_filter(noisy, 3, 1)
    rows.append(("contra_harmonic_Q1", contra_result))

    results = []
    for name, filtered in rows:
        noisy_pixels = metrics.count_noisy_pixels(original, noisy)
        fixed = metrics.count_fixed_noisy_pixels(original, noisy, filtered)
        damaged = metrics.count_damaged_clean_pixels(original, noisy, filtered)
        results.append((name, noisy_pixels, fixed, damaged, filtered))
    return results


def main():
    image_path = input("Enter path to original clean image: ").strip()
    original = image_io.load_grayscale_image(image_path)
    results_dir = ensure_results_dir()

    noise_types = [
        ("salt_and_pepper", lambda img: noise.add_salt_and_pepper_noise(img, 0.05)),
        ("salt", lambda img: noise.add_salt_noise(img, 0.05)),
        ("pepper", lambda img: noise.add_pepper_noise(img, 0.05)),
        ("gaussian", lambda img: noise.add_gaussian_noise(img, 0, 10)),
        ("uniform", lambda img: noise.add_uniform_noise(img, -10, 10)),
    ]

    for noise_name, noise_fn in noise_types:
        noisy = noise_fn(original)
        filtered_results = apply_filters(original, noisy)

        table_path = os.path.join(results_dir, f"filters_{noise_name}.csv")
        with open(table_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["filter", "noisy_pixels", "fixed_pixels", "damaged_clean_pixels"])
            for name, noisy_pixels, fixed, damaged, filtered in filtered_results:
                writer.writerow([name, noisy_pixels, fixed, damaged])

                noisy_path = os.path.join(results_dir, f"{noise_name}_noisy.png")
                filtered_path = os.path.join(results_dir, f"{noise_name}_{name}.png")
                image_io.save_grayscale_image(noisy, noisy_path)
                image_io.save_grayscale_image(filtered, filtered_path)

        print(f"Saved table for {noise_name} to {table_path}")


if __name__ == "__main__":
    main()
