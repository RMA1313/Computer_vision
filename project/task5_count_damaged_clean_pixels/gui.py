import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common import image_io, metrics  # noqa: E402


class DamagedPixelsGUI:
    """GUI to count damaged clean pixels after filtering."""

    def __init__(self, root):
        self.root = root
        self.root.title("Count Damaged Clean Pixels")

        self.original_pixels = None
        self.noisy_pixels = None
        self.denoised_pixels = None

        self.original_photo = None
        self.noisy_photo = None
        self.denoised_photo = None

        load_frame = tk.Frame(root)
        load_frame.pack(pady=4)
        tk.Button(load_frame, text="Load Original", command=self.load_original).pack(side=tk.LEFT, padx=4)
        tk.Button(load_frame, text="Load Noisy", command=self.load_noisy).pack(side=tk.LEFT, padx=4)
        tk.Button(load_frame, text="Load Denoised", command=self.load_denoised).pack(side=tk.LEFT, padx=4)

        preview_frame = tk.Frame(root)
        preview_frame.pack(pady=6)
        self.original_label = tk.Label(preview_frame, text="Original")
        self.original_label.pack(side=tk.LEFT, padx=10)
        self.noisy_label = tk.Label(preview_frame, text="Noisy")
        self.noisy_label.pack(side=tk.LEFT, padx=10)
        self.denoised_label = tk.Label(preview_frame, text="Denoised")
        self.denoised_label.pack(side=tk.LEFT, padx=10)

        tk.Button(root, text="Count Damaged Clean Pixels", command=self.count_damaged).pack(pady=4)

        self.info_label = tk.Label(root, text="Damaged clean pixels: 0 (0.00%)")
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

    def load_denoised(self):
        path = filedialog.askopenfilename(title="Select Denoised Image")
        if not path:
            return
        self.denoised_pixels = image_io.load_grayscale_image(path)
        self.show_image(self.denoised_pixels, self.denoised_label, "denoised")

    def count_damaged(self):
        if self.original_pixels is None or self.noisy_pixels is None or self.denoised_pixels is None:
            messagebox.showinfo("Info", "Please load all three images.")
            return
        damaged = metrics.count_damaged_clean_pixels(self.original_pixels, self.noisy_pixels, self.denoised_pixels)
        clean = (len(self.original_pixels) * len(self.original_pixels[0])) - metrics.count_noisy_pixels(
            self.original_pixels, self.noisy_pixels
        )
        percent = 0.0
        if clean > 0:
            percent = (damaged / clean) * 100
        self.info_label.config(text=f"Damaged clean pixels: {damaged} ({percent:.2f}%)")

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
            self.denoised_photo = photo


def main():
    root = tk.Tk()
    gui = DamagedPixelsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
