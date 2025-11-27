import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common import filters, image_io, metrics  # noqa: E402


class DenoiseGUI:
    """GUI to load a noisy image and apply simple filters."""

    def __init__(self, root):
        self.root = root
        self.root.title("Denoise Demo")

        self.original_pixels = None
        self.noisy_pixels = None
        self.filtered_pixels = None

        self.original_photo = None
        self.noisy_photo = None
        self.filtered_photo = None

        # Load buttons
        load_frame = tk.Frame(root)
        load_frame.pack(pady=4)
        tk.Button(load_frame, text="Load Original Image", command=self.load_original).pack(side=tk.LEFT, padx=4)
        tk.Button(load_frame, text="Load Noisy Image", command=self.load_noisy).pack(side=tk.LEFT, padx=4)

        # Filter selection
        options_frame = tk.Frame(root)
        options_frame.pack(pady=4)
        tk.Label(options_frame, text="Filter:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="Median")
        tk.OptionMenu(options_frame, self.filter_var, "Median", "Mean", "Trimmed-Alpha", "Contra-Harmonic").pack(
            side=tk.LEFT, padx=4
        )

        tk.Label(options_frame, text="Window Size:").pack(side=tk.LEFT)
        self.window_scale = tk.Scale(options_frame, from_=3, to=7, resolution=2, orient=tk.HORIZONTAL)
        self.window_scale.set(3)
        self.window_scale.pack(side=tk.LEFT, padx=4)

        tk.Label(options_frame, text="Trim Amount:").pack(side=tk.LEFT)
        self.trim_entry = tk.Entry(options_frame, width=5)
        self.trim_entry.insert(0, "1")
        self.trim_entry.pack(side=tk.LEFT, padx=4)

        tk.Label(options_frame, text="Q Value:").pack(side=tk.LEFT)
        self.q_entry = tk.Entry(options_frame, width=5)
        self.q_entry.insert(0, "1")
        self.q_entry.pack(side=tk.LEFT, padx=4)

        tk.Button(root, text="Apply Filter", command=self.apply_filter).pack(pady=4)

        # Previews
        preview_frame = tk.Frame(root)
        preview_frame.pack(pady=6)
        self.original_label = tk.Label(preview_frame, text="Original")
        self.original_label.pack(side=tk.LEFT, padx=10)
        self.noisy_label = tk.Label(preview_frame, text="Noisy")
        self.noisy_label.pack(side=tk.LEFT, padx=10)
        self.filtered_label = tk.Label(preview_frame, text="Filtered")
        self.filtered_label.pack(side=tk.LEFT, padx=10)

        # Metrics label
        self.info_label = tk.Label(root, text="Fixed noisy: 0, Damaged clean: 0")
        self.info_label.pack(pady=4)

    def load_original(self):
        path = filedialog.askopenfilename(title="Select Original Image")
        if not path:
            return
        self.original_pixels = image_io.load_grayscale_image(path)
        self.show_image(self.original_pixels, self.original_label, "original")

    def load_noisy(self):
        path = filedialog.askopenfilename(title="Select Noisy Image")
        if not path:
            return
        self.noisy_pixels = image_io.load_grayscale_image(path)
        self.show_image(self.noisy_pixels, self.noisy_label, "noisy")

    def apply_filter(self):
        if self.noisy_pixels is None:
            messagebox.showinfo("Info", "Please load a noisy image first.")
            return
        window = int(self.window_scale.get())
        filter_name = self.filter_var.get()

        if filter_name == "Median":
            self.filtered_pixels = filters.median_filter(self.noisy_pixels, window)
        elif filter_name == "Mean":
            self.filtered_pixels = filters.mean_filter(self.noisy_pixels, window)
        elif filter_name == "Trimmed-Alpha":
            try:
                trim_amount = int(self.trim_entry.get())
            except ValueError:
                trim_amount = 1
            self.filtered_pixels = filters.trimmed_alpha_filter(self.noisy_pixels, window, trim_amount)
        elif filter_name == "Contra-Harmonic":
            try:
                q_value = float(self.q_entry.get())
            except ValueError:
                q_value = 1.0
            self.filtered_pixels = filters.contra_harmonic_filter(self.noisy_pixels, window, q_value)
        else:
            messagebox.showinfo("Info", "Unknown filter selected.")
            return

        self.show_image(self.filtered_pixels, self.filtered_label, "filtered")
        self.update_metrics()

    def update_metrics(self):
        if self.original_pixels is None or self.noisy_pixels is None or self.filtered_pixels is None:
            self.info_label.config(text="Fixed noisy: 0, Damaged clean: 0")
            return
        fixed = metrics.count_fixed_noisy_pixels(self.original_pixels, self.noisy_pixels, self.filtered_pixels)
        damaged = metrics.count_damaged_clean_pixels(self.original_pixels, self.noisy_pixels, self.filtered_pixels)
        self.info_label.config(text=f"Fixed noisy: {fixed}, Damaged clean: {damaged}")

    def show_image(self, pixels, label, kind):
        if pixels is None:
            return
        height = len(pixels)
        width = len(pixels[0])
        img = Image.new("L", (width, height))
        for y in range(height):
            for x in range(width):
                img.putpixel((x, y), int(pixels[y][x]))
        max_size = 250
        if width > max_size or height > max_size:
            img.thumbnail((max_size, max_size))
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        if kind == "original":
            self.original_photo = photo
        elif kind == "noisy":
            self.noisy_photo = photo
        else:
            self.filtered_photo = photo


def main():
    root = tk.Tk()
    gui = DenoiseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
