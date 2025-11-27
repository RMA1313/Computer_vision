import os
import sys

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common import image_io, noise, metrics


def main():
    input_path = input("Enter path to input image: ").strip()
    levels = [0.01, 0.03, 0.05, 0.1]
    original = image_io.load_grayscale_image(input_path)

    output_dir = os.path.join(os.path.dirname(__file__), "sample_outputs")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for level in levels:
        noisy = noise.add_salt_and_pepper_noise(original, level)
        output_path = os.path.join(output_dir, f"noisy_level_{str(level).replace('.', '_')}.png")
        image_io.save_grayscale_image(noisy, output_path)
        noisy_count = metrics.count_noisy_pixels(original, noisy)
        total_pixels = len(original) * len(original[0])
        percent = (noisy_count / total_pixels) * 100
        print(f"Noise level {level}: noisy pixels = {noisy_count} ({percent:.2f}%) saved to {output_path}")


if __name__ == "__main__":
    main()
