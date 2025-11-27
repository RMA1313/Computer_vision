# Noise and Denoising Playground

Small Python exercises for adding noise to grayscale images, denoising them with classic filters, and measuring how many pixels were corrupted or fixed. Each task ships a CLI demo and a lightweight Tkinter GUI.

## Project Layout
- `common/` shared helpers for image I/O (`Pillow`), noise generation, filters, and pixel metrics
- `task1_add_noise/` add salt-and-pepper, salt, pepper, Gaussian, or uniform noise
- `task2_count_noisy_pixels/` measure how many pixels differ between clean and noisy images
- `task3_denoise/` apply median/mean/trimmed-alpha/contra-harmonic filters to noisy images
- `task4_count_fixed_pixels/` count noisy pixels that were restored after denoising
- `task5_count_damaged_clean_pixels/` count clean pixels that were incorrectly altered by denoising
- `experiments/` batch scripts to generate tables/plots and save noisy/filtered outputs

## Requirements
- Python 3.9+ (Tkinter is included with the standard install on most platforms)
- Pip packages: `pillow`, `matplotlib`

Install dependencies:
```bash
python -m pip install pillow matplotlib
```

## Running the demos (CLI)
From the repo root, run any script with Python:
- Add noise and save variants: `python task1_add_noise/add_noise_demo.py`
- Count noisy pixels: `python task2_count_noisy_pixels/count_noisy_pixels_demo.py`
- Denoise with median filter (3x3 and 5x5): `python task3_denoise/median_filter_demo.py`
- Count fixed noisy pixels: `python task4_count_fixed_pixels/count_fixed_pixels_demo.py`
- Count damaged clean pixels: `python task5_count_damaged_clean_pixels/count_damaged_clean_pixels_demo.py`

Scripts prompt for file paths; outputs are written alongside each task (e.g., `sample_outputs/`).

## GUI tools
Each task has a Tkinter GUI:
- `python task1_add_noise/gui.py`
- `python task2_count_noisy_pixels/gui.py`
- `python task3_denoise/gui.py`
- `python task4_count_fixed_pixels/gui.py`
- `python task5_count_damaged_clean_pixels/gui.py`

Load the requested images (original/noisy/denoised), adjust parameters (noise level, filter, window size, trim, Q), then review previews and pixel statistics. Images are converted to 8-bit grayscale on load.

## Experiments
- Compare noise levels with a 3x3 median filter: `python experiments/multiple_noise_levels.py`
- Compare multiple filters across several noise types: `python experiments/multiple_filters.py`
- Summarize CSV outputs into a single text file: `python experiments/generate_tables.py`
- Plot CSV tables (noise levels or filter comparisons): `python experiments/generate_plots.py`

Results are written to `experiments/results/`; plots open interactively via Matplotlib.

## Notes
- Metrics assume images share the same dimensions; mismatched sizes will raise errors.
- Noise generation is random; reruns produce slightly different outputs.
- Values are clamped to the 0–255 range when saving or filtering.
