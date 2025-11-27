import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Circle
import threading
import queue
import os

class UltimateFrequencyLab:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Frequency Lab — Full-Screen, Real-time, Pro Tool")
        self.root.state('zoomed')  # Full screen

        # Data
        self.lock = threading.Lock()
        self.img = None
        self.fshift = None
        self.mask = None
        self.result_cache = None

        # Tools
        self.tool = tk.StringVar(value="brush")
        self.brush_size = tk.IntVar(value=15)
        self.strength = tk.DoubleVar(value=1000)  # شروع با عدد منطقی
        self.freq_u = tk.DoubleVar(value=30)
        self.freq_v = tk.DoubleVar(value=20)
        self.phase = tk.DoubleVar(value=0)

        # Threading
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker = threading.Thread(target=self.worker_loop, daemon=True)
        self.worker.start()

        self.setup_gui()
        self.root.after(30, self.check_queue)

    def setup_gui(self):
        # Top panel
        top = ttk.Frame(self.root)
        top.pack(side=tk.TOP, fill=tk.X, padx=12, pady=8)

        ttk.Button(top, text="Load Image", command=self.load_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Save Result", command=self.save_result).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Reset", command=self.reset_image).pack(side=tk.LEFT, padx=5)

        ttk.Separator(top, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=15)

        tools = ["brush", "erase", "sine", "line", "ring", "grid"]
        for t in tools:
            ttk.Radiobutton(top, text=t.capitalize(), variable=self.tool, value=t).pack(side=tk.LEFT, padx=8)

        # Live sliders
        ttk.Label(top, text="  Size:").pack(side=tk.LEFT, padx=(30,5))
        ttk.Scale(top, from_=5, to=100, variable=self.brush_size, length=180).pack(side=tk.LEFT, padx=5)

        ttk.Label(top, text="  Strength:").pack(side=tk.LEFT, padx=(30,5))
        ttk.Scale(top, from_=1e3, to=5e7, variable=self.strength, length=250, orient=tk.HORIZONTAL).pack(side=tk.LEFT, padx=5)
        ttk.Label(top, textvariable=self.strength, width=10).pack(side=tk.LEFT)

        # Frequency sliders
        ttk.Label(top, text="  u (freq X):").pack(side=tk.LEFT, padx=(30,5))
        ttk.Scale(top, from_=1, to=200, variable=self.freq_u, length=150).pack(side=tk.LEFT)
        ttk.Label(top, textvariable=self.freq_u, width=5).pack(side=tk.LEFT)

        ttk.Label(top, text="v (freq Y):").pack(side=tk.LEFT, padx=(20,5))
        ttk.Scale(top, from_=1, to=200, variable=self.freq_v, length=150).pack(side=tk.LEFT)
        ttk.Label(top, textvariable=self.freq_v, width=5).pack(side=tk.LEFT)

        # 3 full-size panels
        self.fig = plt.figure(figsize=(19, 10), dpi=100)
        self.ax = self.fig.add_subplot(131)
        self.ax2 = self.fig.add_subplot(132)
        self.ax3 = self.fig.add_subplot(133)

        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(self.canvas, self.root)

        self.ax.set_title("Original Image", fontsize=16, fontweight='bold')
        self.ax2.set_title("Frequency Domain — Click to Add!", fontsize=16, fontweight='bold')
        self.ax3.set_title("Real-time Result", fontsize=16, fontweight='bold')

        self.cursor = Circle((0,0), 15, color='lime', fill=False, lw=3, alpha=0.9)
        self.ax2.add_patch(self.cursor)
        self.cursor.set_visible(False)

        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_motion)

        self.status = tk.Label(self.root, text="Ready — Load an image to start", relief=tk.SUNKEN, anchor=tk.W, font=("Segoe UI", 10))
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.*")])
        if not path: return
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None: 
            messagebox.showerror("Error", "Cannot load image")
            return

        with self.lock:
            self.img = img.astype(np.float32) / 255.0
            self.fshift = np.fft.fftshift(np.fft.fft2(self.img))
            self.mask = np.ones_like(self.img, dtype=np.float32)

        self.update_display()
        self.trigger_recompute()
        self.status.config(text=f"Loaded: {os.path.basename(path)} — {img.shape[1]}×{img.shape[0]}")

    def update_display(self):
        if self.img is None: return

        # Original — full dynamic range
        self.ax.clear()
        self.ax.imshow(self.img, cmap='gray', vmin=0, vmax=1)
        self.ax.set_title("Original Image")
        self.ax.axis('off')

        # Spectrum
        with self.lock:
            mag = np.log(1 + np.abs(self.fshift) * self.mask)
        self.ax2.clear()
        self.ax2.imshow(mag, cmap='gray')
        self.ax2.set_title("Frequency Domain — Click to Add!")
        self.ax2.axis('off')
        self.ax2.add_patch(self.cursor)

        # Result
        if self.result_cache is not None:
            self.ax3.clear()
            self.ax3.imshow(self.result_cache, cmap='gray', vmin=0, vmax=1)
            self.ax3.set_title("Real-time Result")
            self.ax3.axis('off')

        self.fig.tight_layout()
        self.canvas.draw_idle()

    def trigger_recompute(self):
        if self.fshift is None: return
        with self.lock:
            f_copy = self.fshift.copy()
            m_copy = self.mask.copy()
        self.task_queue.put(("compute", f_copy, m_copy))

    def worker_loop(self):
        while True:
            _, fshift, mask = self.task_queue.get()
            filtered = fshift * mask
            img_back = np.fft.ifftshift(filtered)
            result = np.abs(np.fft.ifft2(img_back))
            self.result_queue.put(result)

    def check_queue(self):
        while True:
            try:
                result = self.result_queue.get_nowait()
                self.result_cache = result
                self.ax3.clear()
                self.ax3.imshow(result, cmap='gray', vmin=0, vmax=1)
                self.ax3.set_title("Real-time Result")
                self.ax3.axis('off')
                self.canvas.draw_idle()
            except:
                break
        self.root.after(30, self.check_queue)

    def on_click(self, event):
        if event.inaxes != self.ax2 or self.fshift is None: return
        x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)
        h, w = self.fshift.shape
        cx, cy = w // 2, h // 2
        strength = self.strength.get()

        with self.lock:
            if self.tool.get() == "brush":
                cv2.circle(self.mask, (x, y), self.brush_size.get(), 1.0, -1)
            elif self.tool.get() == "erase":
                cv2.circle(self.mask, (x, y), self.brush_size.get(), 0.0, -1)
            elif self.tool.get() == "sine":
                val = strength * np.exp(1j * np.deg2rad(self.phase.get()))
                self.fshift[y, x] += val
                if not (x == cx and y == cy):
                    self.fshift[h-1-y, w-1-x] += np.conj(val)
            elif self.tool.get() == "line":
                self.fshift[y, :] += strength
                self.fshift[h-1-y, :] += strength
            elif self.tool.get() == "ring":
                r = np.hypot(x - cx, y - cy)
                yy, xx = np.ogrid[:h, :w]
                ring = np.abs(np.hypot(xx - cx, yy - cy) - r) < 6
                self.fshift[ring] += strength
                self.fshift[np.flipud(np.fliplr(ring))] += strength
            elif self.tool.get() == "grid":
                u, v = int(self.freq_u.get()), int(self.freq_v.get())
                for dy in [-v, v]:
                    for dx in [-u, u]:
                        if dx == 0 and dy == 0: continue
                        ny = (y + dy) % h
                        nx = (x + dx) % w
                        self.fshift[ny, nx] += strength
                        self.fshift[h-1-ny, w-1-nx] += strength

        self.update_display()
        self.trigger_recompute()
        self.status.config(text=f"Added {self.tool.get()} at ({x},{y}) — Strength: {strength:.0e}")

    def on_motion(self, event):
        if event.inaxes == self.ax2:
            self.cursor.set_visible(True)
            self.cursor.center = (event.xdata, event.ydata)
            self.cursor.set_radius(self.brush_size.get())
            colors = {"brush":"white", "erase":"red", "sine":"lime", "line":"cyan", "ring":"gold", "grid":"magenta"}
            self.cursor.set_color(colors.get(self.tool.get(), "lime"))
        else:
            self.cursor.set_visible(False)
        self.canvas.draw_idle()

    def clear_all(self):
        if self.fshift is not None:
            with self.lock: self.mask.fill(1.0)
            self.update_display(); self.trigger_recompute()

    def reset_image(self):
        if self.img is not None:
            with self.lock:
                self.fshift = np.fft.fftshift(np.fft.fft2(self.img))
                self.mask.fill(1.0)
            self.update_display(); self.trigger_recompute()

    def save_result(self):
        if self.result_cache is None: return
        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            cv2.imwrite(path, (self.result_cache * 255).astype(np.uint8))
            messagebox.showinfo("Saved", f"Result saved to {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = UltimateFrequencyLab(root)
    root.mainloop()