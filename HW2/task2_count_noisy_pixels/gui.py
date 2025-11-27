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


class CountNoisyGUI:
    """GUI to count noisy pixels between two images."""

    def __init__(self, root):
        self.root = root
        self.root.title("Count Noisy Pixels")

        self.original_pixels = None
        self.noisy_pixels = None
        self.original_photo = None
        self.noisy_photo = None

        button_frame = tk.Frame(root)
        button_frame.pack(pady=4)
        tk.Button(button_frame, text="Load Original Image", command=self.load_original).pack(side=tk.LEFT, padx=4)
        tk.Button(button_frame, text="Load Noisy Image", command=self.load_noisy).pack(side=tk.LEFT, padx=4)

        preview_frame = tk.Frame(root)
        preview_frame.pack(pady=6)
        self.original_label = tk.Label(preview_frame, text="Original")
        self.original_label.pack(side=tk.LEFT, padx=10)
        self.noisy_label = tk.Label(preview_frame, text="Noisy")
        self.noisy_label.pack(side=tk.LEFT, padx=10)

        tk.Button(root, text="Count Noisy Pixels", command=self.count_noisy).pack(pady=4)

        self.info_label = tk.Label(root, text="Noisy pixels: 0 (0.00%)")
        self.info_label.pack(pady=4)

    def load_original(self):
        path = filedialog.askopenfilename(title="Select Original Image")
        if not path:
            return
        self.original_pixels = image_io.load_grayscale_image(path)
        self.show_image(self.original_pixels, self.original_label, is_noisy=False)

    def load_noisy(self):
        path = filedialog.askopenfilename(title="Select Noisy Image")
        if not path:
            return
        self.noisy_pixels = image_io.load_grayscale_image(path)
        self.show_image(self.noisy_pixels, self.noisy_label, is_noisy=True)

    def count_noisy(self):
        if self.original_pixels is None or self.noisy_pixels is None:
            messagebox.showinfo("Info", "Please load both images first.")
            return
        noisy_count = metrics.count_noisy_pixels(self.original_pixels, self.noisy_pixels)
        total = len(self.original_pixels) * len(self.original_pixels[0])
        percent = (noisy_count / total) * 100
        self.info_label.config(text=f"Noisy pixels: {noisy_count} ({percent:.2f}%)")

    def show_image(self, pixels, label, is_noisy):
        if pixels is None:
            return
        height = len(pixels)
        width = len(pixels[0])
        img = Image.new("L", (width, height))
        for y in range(height):
            for x in range(width):
                img.putpixel((x, y), int(pixels[y][x]))
        max_size = 300
        if width > max_size or height > max_size:
            img.thumbnail((max_size, max_size))
        photo = ImageTk.PhotoImage(img)
        label.config(image=photo)
        if is_noisy:
            self.noisy_photo = photo
        else:
            self.original_photo = photo


def main():
    root = tk.Tk()
    gui = CountNoisyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
