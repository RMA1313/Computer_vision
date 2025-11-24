import csv
import os

import matplotlib.pyplot as plt


def read_csv(path):
    rows = []
    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def plot_noise_levels(header, data, title):
    noise_levels = []
    noisy_pixels = []
    fixed_pixels = []
    damaged_pixels = []

    for row in data:
        noise_levels.append(float(row[0]))
        noisy_pixels.append(int(row[1]))
        fixed_pixels.append(int(row[2]))
        damaged_pixels.append(int(row[3]))

    plt.figure()
    plt.plot(noise_levels, noisy_pixels, label="Noisy pixels")
    plt.plot(noise_levels, fixed_pixels, label="Fixed noisy pixels")
    plt.plot(noise_levels, damaged_pixels, label="Damaged clean pixels")
    plt.xlabel("Noise level")
    plt.ylabel("Pixel count")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_filters(header, data, title):
    filters = []
    fixed_pixels = []
    damaged_pixels = []

    for row in data:
        filters.append(row[0])
        fixed_pixels.append(int(row[2]))
        damaged_pixels.append(int(row[3]))

    positions = list(range(len(filters)))
    width = 0.35

    plt.figure()
    plt.bar([p - width / 2 for p in positions], fixed_pixels, width=width, label="Fixed noisy")
    plt.bar([p + width / 2 for p in positions], damaged_pixels, width=width, label="Damaged clean")
    plt.xticks(positions, filters, rotation=30, ha="right")
    plt.ylabel("Pixel count")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main():
    csv_path = input("Enter path to CSV file: ").strip()
    if not os.path.exists(csv_path):
        print("CSV file not found.")
        return

    rows = read_csv(csv_path)
    if len(rows) < 2:
        print("CSV file is empty.")
        return

    header = rows[0]
    data = rows[1:]

    if "noise_level" in header:
        plot_noise_levels(header, data, "Noise Levels Experiment")
    elif "filter" in header:
        plot_filters(header, data, "Filter Comparison")
    else:
        print("Unknown table format. Unable to plot.")


if __name__ == "__main__":
    main()
