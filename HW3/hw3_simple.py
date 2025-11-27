import cv2
import numpy as np
from pathlib import Path

def load_gray(path: Path) -> np.ndarray:
    """Load a grayscale image using OpenCV."""
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image not found: {path}")
    return img.astype(np.float32)


def scale_to_uint8(arr: np.ndarray) -> np.ndarray:
    """Scale any float array to the 0-255 range for saving."""
    flat = arr - arr.min()
    maxval = flat.max()
    if maxval <= 0:
        return np.zeros_like(arr, dtype=np.uint8)
    norm = (flat / maxval) * 255.0
    return norm.astype(np.uint8)


def main():
    base = Path(__file__).resolve().parent
    output_dir = base / "HW3_results"
    output_dir.mkdir(exist_ok=True)

    # find two image files in the current folder
    exts = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}
    images = sorted([p for p in base.iterdir() if p.suffix.lower() in exts])
    if len(images) < 2:
        raise FileNotFoundError("Place at least two images next to this script.")

    # PART 1: add periodic noise
    image1 = load_gray(images[0])
    fft1 = np.fft.fft2(image1)
    fft1_shift = np.fft.fftshift(fft1)
    spectrum_before1 = np.log1p(np.abs(fft1_shift))

    # insert symmetric bright points in the shifted spectrum
    center = np.array(fft1_shift.shape) // 2
    offsets = [(20, 45), (35, 15), (10, 60)]
    strength = np.mean(np.abs(fft1_shift)) * 6.0
    for dr, dc in offsets:
        for signr in (-1, 1):
            for signc in (-1, 1):
                r = center[0] + signr * dr
                c = center[1] + signc * dc
                if 0 <= r < fft1_shift.shape[0] and 0 <= c < fft1_shift.shape[1]:
                    fft1_shift[r, c] += strength

    spectrum_after1 = np.log1p(np.abs(fft1_shift))
    img1_back = np.real(np.fft.ifft2(np.fft.ifftshift(fft1_shift)))

    # save all part1 images
    cv2.imwrite(str(output_dir / "part1_original.png"), scale_to_uint8(image1))
    cv2.imwrite(str(output_dir / "part1_before.png"), scale_to_uint8(spectrum_before1))
    cv2.imwrite(str(output_dir / "part1_after.png"), scale_to_uint8(spectrum_after1))
    cv2.imwrite(str(output_dir / "part1_result.png"), scale_to_uint8(img1_back))

    # PART 2: create ripple pattern
    image2 = load_gray(images[1])
    fft2 = np.fft.fft2(image2)
    fft2_shift = np.fft.fftshift(fft2)
    spectrum_before2 = np.log1p(np.abs(fft2_shift))

    # build a radial mask based on distance from center
    rows, cols = image2.shape
    y = np.arange(rows) - rows // 2
    x = np.arange(cols) - cols // 2
    yy, xx = np.meshgrid(y, x, indexing="ij")
    radius = np.sqrt(yy * yy + xx * xx)
    ripple_mask = 1.0 + 0.4 * np.sin(radius / 6.0)
    fft2_shift *= ripple_mask

    spectrum_after2 = np.log1p(np.abs(fft2_shift))
    img2_back = np.real(np.fft.ifft2(np.fft.ifftshift(fft2_shift)))

    # save part2 images
    cv2.imwrite(str(output_dir / "part2_original.png"), scale_to_uint8(image2))
    cv2.imwrite(str(output_dir / "part2_before.png"), scale_to_uint8(spectrum_before2))
    cv2.imwrite(str(output_dir / "part2_after.png"), scale_to_uint8(spectrum_after2))
    cv2.imwrite(str(output_dir / "part2_result.png"), scale_to_uint8(img2_back))

    print(f"Saved results to {output_dir}")


if __name__ == "__main__":
    main()
