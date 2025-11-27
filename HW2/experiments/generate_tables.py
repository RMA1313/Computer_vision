import csv
import os


def read_csv(path):
    rows = []
    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def main():
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    if not os.path.exists(results_dir):
        print("No results directory found.")
        return

    summary_path = os.path.join(results_dir, "summary.txt")
    with open(summary_path, "w") as summary_file:
        for filename in os.listdir(results_dir):
            if not filename.endswith(".csv"):
                continue
            path = os.path.join(results_dir, filename)
            rows = read_csv(path)
            summary_file.write(f"Table: {filename}\n")
            for row in rows:
                line = ", ".join(row)
                summary_file.write(line + "\n")
            summary_file.write("\n")
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()
