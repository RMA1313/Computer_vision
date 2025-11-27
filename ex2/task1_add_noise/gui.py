import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

current_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from common import image_io, noise, metrics  # noqa: E402


class AddNoiseGUI:
    """Simple GUI to add different noise types to an image."""

    def __init__(self, root):
        self.root = root
        self.root.title("Add Noise Demo")

        # Keep references to images so tkinter does not clear them
        self.original_pixels = None
        self.noisy_pixels = None
        self.original_photo = None
        self.noisy_photo = None

        # Buttons for loading and saving
        load_btn = tk.Button(root, text="Load Image", command=self.load_image)
        load_btn.pack(pady=4)

        # Noise level slider
        self.noise_scale = tk.Scale(
            root,
            from_=0.0,
            to=0.2,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            label="Noise Level",
        )
        self.noise_scale.set(0.05)
        self.noise_scale.pack(fill=tk.X, padx=10, pady=4)

        # Buttons for different noise types
        button_frame = tk.Frame(root)
        button_frame.pack(pady=4)
        tk.Button(button_frame, text="Salt & Pepper", command=self.apply_salt_and_pepper).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Salt", command=self.apply_salt).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Pepper", command=self.apply_pepper).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Gaussian", command=self.apply_gaussian).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Uniform", command=self.apply_uniform).pack(side=tk.LEFT, padx=2)

        # Image previews
        preview_frame = tk.Frame(root)
        preview_frame.pack(pady=6)
        self.original_label = tk.Label(preview_frame, text="Original")
        self.original_label.pack(side=tk.LEFT, padx=10)
        self.noisy_label = tk.Label(preview_frame, text="Noisy")
        self.noisy_label.pack(side=tk.LEFT, padx=10)

        # Save button
        save_btn = tk.Button(root, text="Save Noisy Image", command=self.save_noisy)
        save_btn.pack(pady=4)

        # Label to show noisy pixel counts
        self.info_label = tk.Label(root, text="Noisy pixels: 0 (0.00%)")
        self.info_label.pack(pady=4)

    def load_image(self):
        """Load an image from disk."""
        path = filedialog.askopenfilename(title="Select Image")
        if not path:
            return
        self.original_pixels = image_io.load_grayscale_image(path)
        self.noisy_pixels = None
        self.show_image(self.original_pixels, self.original_label, is_noisy=False)
        self.info_label.config(text="Noisy pixels: 0 (0.00%)")

    def save_noisy(self):
        """Save the noisy image if it exists."""
        if self.noisy_pixels is None:
            messagebox.showinfo("Info", "No noisy image to save.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path:
            return
        image_io.save_grayscale_image(self.noisy_pixels, path)
        messagebox.showinfo("Saved", f"Saved noisy image to {path}")

    def apply_noise(self, noise_fn):
        """Apply a chosen noise function."""
        if self.original_pixels is None:
            messagebox.showinfo("Info", "Please load an image first.")
            return
        level = float(self.noise_scale.get())
        self.noisy_pixels = noise_fn(self.original_pixels, level)
        self.show_image(self.noisy_pixels, self.noisy_label, is_noisy=True)
        noisy_count = metrics.count_noisy_pixels(self.original_pixels, self.noisy_pixels)
        total = len(self.original_pixels) * len(self.original_pixels[0])
        percent = (noisy_count / total) * 100
        self.info_label.config(text=f"Noisy pixels: {noisy_count} ({percent:.2f}%)")

    def apply_salt_and_pepper(self):
        self.apply_noise(lambda img, lvl: noise.add_salt_and_pepper_noise(img, lvl))

    def apply_salt(self):
        self.apply_noise(lambda img, lvl: noise.add_salt_noise(img, lvl))

    def apply_pepper(self):
        self.apply_noise(lambda img, lvl: noise.add_pepper_noise(img, lvl))

    def apply_gaussian(self):
        # Use noise level to control standard deviation
        self.apply_noise(lambda img, lvl: noise.add_gaussian_noise(img, 0, max(1, lvl * 100)))

    def apply_uniform(self):
        # Use noise level to control range
        self.apply_noise(lambda img, lvl: noise.add_uniform_noise(img, -lvl * 255, lvl * 255))

    def show_image(self, pixels, label, is_noisy):
        """Convert 2D list to PhotoImage and show in a label."""
        if pixels is None:
            return
        height = len(pixels)
        width = len(pixels[0])
        img = Image.new("L", (width, height))
        for y in range(height):
            for x in range(width):
                img.putpixel((x, y), int(pixels[y][x]))
        # Resize for preview if large
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
    gui = AddNoiseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
