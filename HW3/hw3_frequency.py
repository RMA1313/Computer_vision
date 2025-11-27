import argparse
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import cv2
import numpy as np


HW3_RESULTS_DIR = Path(__file__).resolve().parent / "HW3_results"


def read_grayscale(path: Path) -> np.ndarray:
    """Load image as grayscale float32 (no alpha)."""
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return img.astype(np.float32)


def magnitude_spectrum(fft_array: np.ndarray) -> np.ndarray:
    """Compute log magnitude spectrum scaled to uint8 for visualization."""
    mag = np.log1p(np.abs(fft_array))
    max_val = mag.max()
    if max_val == 0:
        return np.zeros_like(mag, dtype=np.uint8)
    mag = mag / max_val * 255.0
    return mag.astype(np.uint8)


def normalize_to_uint8(img: np.ndarray) -> np.ndarray:
    """Normalize array to 0-255 uint8."""
    min_val = img.min()
    max_val = img.max()
    if max_val - min_val < 1e-6:
        return np.zeros_like(img, dtype=np.uint8)
    scaled = (img - min_val) / (max_val - min_val)
    return (scaled * 255.0).clip(0, 255).astype(np.uint8)


def add_periodic_noise(image: np.ndarray, offsets: Optional[Iterable[Tuple[int, int]]] = None, strength: float = 6.0):
    """Drop a few bright symmetric points in the spectrum to create grid-like periodic noise."""
    offsets = list(offsets) if offsets else [(18, 36), (42, 12), (28, 64)]

    f = np.fft.fft2(image)
    fshift = np.fft.fftshift(f)
    spectrum_before = magnitude_spectrum(fshift)

    cy, cx = np.array(fshift.shape) // 2
    base_amp = np.mean(np.abs(fshift)) * strength

    for dr, dc in offsets:
        for sr in (1, -1):
            for sc in (1, -1):
                r = cy + sr * dr
                c = cx + sc * dc
                if 0 <= r < fshift.shape[0] and 0 <= c < fshift.shape[1]:
                    fshift[r, c] += base_amp

    spectrum_after = magnitude_spectrum(fshift)

    f_ishift = np.fft.ifftshift(fshift)
    img_back = np.fft.ifft2(f_ishift)
    noisy_image = normalize_to_uint8(np.real(img_back))
    return noisy_image, spectrum_before, spectrum_after


def add_ripple_waves(image: np.ndarray, ripple_strength: float = 0.45, ripple_wavelength: float = 12.0):
    """Modulate spectrum with a radial sine to create concentric ripples."""
    f = np.fft.fft2(image)
    fshift = np.fft.fftshift(f)
    spectrum_before = magnitude_spectrum(fshift)

    rows, cols = image.shape
    cy, cx = rows // 2, cols // 2
    y = np.arange(rows) - cy
    x = np.arange(cols) - cx
    yy, xx = np.meshgrid(y, x, indexing="ij")
    radius = np.hypot(yy, xx)

    ripple = 1.0 + ripple_strength * np.sin(2.0 * np.pi * radius / ripple_wavelength)
    fshift_mod = fshift * ripple

    spectrum_after = magnitude_spectrum(fshift_mod)

    f_ishift = np.fft.ifftshift(fshift_mod)
    img_back = np.fft.ifft2(f_ishift)
    ripple_image = normalize_to_uint8(np.real(img_back))
    return ripple_image, spectrum_before, spectrum_after


def save_results(output_dir: Path, prefix: str, original: np.ndarray, before: np.ndarray, after: np.ndarray, final: np.ndarray):
    """Save a set of images for one experiment."""
    output_dir.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_dir / f"{prefix}_original.png"), normalize_to_uint8(original))
    cv2.imwrite(str(output_dir / f"{prefix}_spectrum_before.png"), before)
    cv2.imwrite(str(output_dir / f"{prefix}_spectrum_after.png"), after)
    cv2.imwrite(str(output_dir / f"{prefix}_result.png"), final)


def find_default_images(search_dir: Path):
    """Locate the first two image files in search_dir to use as defaults."""
    exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    candidates = sorted([p for p in search_dir.iterdir() if p.suffix.lower() in exts])
    if len(candidates) < 2:
        raise FileNotFoundError(
            "Please provide two grayscale images (png/jpg/bmp/tif) in the folder "
            f"{search_dir} or pass --image1/--image2."
        )
    return candidates[0], candidates[1]


def parse_offsets(text: str) -> List[Tuple[int, int]]:
    """Parse offsets like '18,36; 42,12' into a list of integer tuples."""
    if not text.strip():
        return []
    pairs = []
    for chunk in text.split(";"):
        parts = chunk.strip().split(",")
        if len(parts) != 2:
            continue
        try:
            pairs.append((int(parts[0]), int(parts[1])))
        except ValueError:
            continue
    return pairs


def run_pipeline(image1_path: Path, image2_path: Path, output_dir: Path, periodic_strength: float, periodic_offsets: List[Tuple[int, int]], ripple_strength: float, ripple_wavelength: float) -> Path:
    """Execute both parts and save results."""
    img1 = read_grayscale(image1_path)
    img2 = read_grayscale(image2_path)

    noisy_img, spectrum1_before, spectrum1_after = add_periodic_noise(img1, offsets=periodic_offsets, strength=periodic_strength)
    save_results(output_dir, "part1_periodic", img1, spectrum1_before, spectrum1_after, noisy_img)

    ripple_img, spectrum2_before, spectrum2_after = add_ripple_waves(img2, ripple_strength=ripple_strength, ripple_wavelength=ripple_wavelength)
    save_results(output_dir, "part2_ripple", img2, spectrum2_before, spectrum2_after, ripple_img)
    return output_dir


class HW3App:
    """Tiny Tkinter helper to guide file picking and run the transforms."""

    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("HW3 Frequency Playground")

        default_output = str(HW3_RESULTS_DIR)
        self.image1_var = tk.StringVar(value="")
        self.image2_var = tk.StringVar(value="")
        self.output_var = tk.StringVar(value=default_output)
        self.offsets_var = tk.StringVar(value="18,36; 42,12; 28,64")
        self.periodic_strength_var = tk.DoubleVar(value=6.0)
        self.ripple_strength_var = tk.DoubleVar(value=0.45)
        self.ripple_wavelength_var = tk.DoubleVar(value=12.0)
        self.status_var = tk.StringVar(value="Pick two grayscale images and press Run.")

        self._build_rows()

    def _build_rows(self):
        pad = {"padx": 6, "pady": 4, "sticky": "we"}
        self.master.columnconfigure(1, weight=1)

        tk.Label(self.master, text="Image 1 (periodic):").grid(row=0, column=0, **pad)
        tk.Entry(self.master, textvariable=self.image1_var).grid(row=0, column=1, **pad)
        tk.Button(self.master, text="Browse", command=lambda: self._pick_file(self.image1_var)).grid(row=0, column=2, padx=4, pady=4)

        tk.Label(self.master, text="Image 2 (ripple):").grid(row=1, column=0, **pad)
        tk.Entry(self.master, textvariable=self.image2_var).grid(row=1, column=1, **pad)
        tk.Button(self.master, text="Browse", command=lambda: self._pick_file(self.image2_var)).grid(row=1, column=2, padx=4, pady=4)

        tk.Label(self.master, text="Output folder:").grid(row=2, column=0, **pad)
        tk.Entry(self.master, textvariable=self.output_var).grid(row=2, column=1, **pad)
        tk.Button(self.master, text="Select", command=self._pick_folder).grid(row=2, column=2, padx=4, pady=4)

        tk.Label(self.master, text="Periodic offsets (r,c; ...):").grid(row=3, column=0, **pad)
        tk.Entry(self.master, textvariable=self.offsets_var).grid(row=3, column=1, columnspan=2, **pad)

        tk.Label(self.master, text="Periodic strength:").grid(row=4, column=0, **pad)
        tk.Entry(self.master, textvariable=self.periodic_strength_var).grid(row=4, column=1, **pad)

        tk.Label(self.master, text="Ripple strength:").grid(row=5, column=0, **pad)
        tk.Entry(self.master, textvariable=self.ripple_strength_var).grid(row=5, column=1, **pad)

        tk.Label(self.master, text="Ripple wavelength (px):").grid(row=6, column=0, **pad)
        tk.Entry(self.master, textvariable=self.ripple_wavelength_var).grid(row=6, column=1, **pad)

        tk.Button(self.master, text="Run and Save", command=self.run).grid(row=7, column=0, columnspan=3, pady=10)
        tk.Label(self.master, textvariable=self.status_var, fg="blue").grid(row=8, column=0, columnspan=3, padx=6, pady=6, sticky="w")

    def _pick_file(self, var: tk.StringVar):
        path = filedialog.askopenfilename(title="Choose a grayscale image", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff")])
        if path:
            var.set(path)

    def _pick_folder(self):
        path = filedialog.askdirectory(title="Choose output folder", initialdir=self.output_var.get() or str(Path.cwd()))
        if path:
            self.output_var.set(path)

    def run(self):
        try:
            img1_path = Path(self.image1_var.get())
            img2_path = Path(self.image2_var.get())
            output_dir = Path(self.output_var.get()) if self.output_var.get() else HW3_RESULTS_DIR

            if not img1_path.exists() or not img2_path.exists():
                raise FileNotFoundError("Please pick two valid image files.")

            offsets = parse_offsets(self.offsets_var.get())
            if not offsets:
                offsets = None

            run_pipeline(
                image1_path=img1_path,
                image2_path=img2_path,
                output_dir=output_dir,
                periodic_strength=float(self.periodic_strength_var.get()),
                periodic_offsets=offsets,
                ripple_strength=float(self.ripple_strength_var.get()),
                ripple_wavelength=float(self.ripple_wavelength_var.get()),
            )
            self.status_var.set(f"Done. Saved to {output_dir}")
            messagebox.showinfo("Finished", f"Results saved to:\n{output_dir}")
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f"Error: {exc}")
            messagebox.showerror("Error", str(exc))


def launch_gui():
    root = tk.Tk()
    app = HW3App(root)
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="HW3 frequency-domain processing.")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode instead of GUI.")
    parser.add_argument("--image1", type=Path, help="Path to first grayscale image (periodic noise).")
    parser.add_argument("--image2", type=Path, help="Path to second grayscale image (ripple).")
    parser.add_argument("--output", type=Path, default=None, help="Output directory (default: HW3_results next to script).")
    parser.add_argument("--periodic_strength", type=float, default=6.0, help="Amplitude multiplier for added periodic peaks.")
    parser.add_argument("--periodic_offsets", type=str, default="", help="Offsets as 'r,c; r,c; ...' (defaults used if empty).")
    parser.add_argument("--ripple_strength", type=float, default=0.45, help="Strength of radial ripple modulation.")
    parser.add_argument("--ripple_wavelength", type=float, default=12.0, help="Ripple wavelength in pixels.")
    args = parser.parse_args()

    if not args.cli:
        launch_gui()
        return

    script_dir = Path(__file__).resolve().parent
    output_dir = args.output or HW3_RESULTS_DIR

    if args.image1 and args.image2:
        image1_path, image2_path = args.image1, args.image2
    else:
        image1_path, image2_path = find_default_images(script_dir)

    offsets = parse_offsets(args.periodic_offsets)
    offsets = offsets if offsets else None

    out_dir = run_pipeline(
        image1_path=image1_path,
        image2_path=image2_path,
        output_dir=output_dir,
        periodic_strength=args.periodic_strength,
        periodic_offsets=offsets,
        ripple_strength=args.ripple_strength,
        ripple_wavelength=args.ripple_wavelength,
    )

    print(f"Done. Results saved to {out_dir}")


if __name__ == "__main__":
    main()
