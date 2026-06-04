

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.widgets as mwidgets
from matplotlib.colors import to_rgba
import warnings, time

# ── optional speedup ──────────────────────────────────────────────────────────
try:
    from numba import njit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False


# ── colour palettes ───────────────────────────────────────────────────────────
PALETTES = {
    "classic": ["#1a6634", "#2e8b57", "#52c27a", "#90ee90"],
    "night":   ["#5b21b6", "#7c3aed", "#a78bfa", "#ddd6fe"],
    "autumn":  ["#7c2d12", "#c2410c", "#fb923c", "#fed7aa"],
    "ocean":   ["#0c4a6e", "#0369a1", "#38bdf8", "#bae6fd"],
    "mono":    ["#111111", "#444444", "#888888", "#cccccc"],
}
PALETTE_NAMES = list(PALETTES.keys())

# ── default transform coefficients ───────────────────────────────────────────
DEFAULT_TRANSFORMS = [
    dict(a=0.00, b=0.00, c=0.00, d=0.16, e=0.00, f=0.00, prob=0.01),   # stem
    dict(a=0.85, b=0.04, c=-0.04, d=0.85, e=0.00, f=1.60, prob=0.85),  # frond
    dict(a=0.20, b=-0.26, c=0.23, d=0.22, e=0.00, f=1.60, prob=0.07),  # left leaflet
    dict(a=-0.15, b=0.28, c=0.26, d=0.24, e=0.00, f=0.44, prob=0.07),  # right leaflet
]
N_POINTS = 300_000


# ── point generation ──────────────────────────────────────────────────────────
if HAS_NUMBA:
    @njit(cache=True)
    def _generate_numba(n, coeffs, cum_probs):
        pts  = np.empty((n, 2), dtype=np.float32)
        cidx = np.empty(n,      dtype=np.int32)
        x = y = 0.0
        for i in range(n):
            r   = np.random.random()
            idx = 0
            while idx < len(cum_probs) - 1 and r > cum_probs[idx]:
                idx += 1
            a, b, c, d, e, f = coeffs[idx]
            nx = a*x + b*y + e
            ny = c*x + d*y + f
            x, y = nx, ny
            pts[i, 0]  = x
            pts[i, 1]  = y
            cidx[i]    = idx
        return pts, cidx


def generate_points(transforms, n=N_POINTS):
    probs    = np.array([t["prob"] for t in transforms], dtype=np.float64)
    probs   /= probs.sum()
    cum      = np.cumsum(probs)
    coeffs   = np.array([[t[k] for k in "abcdef"] for t in transforms], dtype=np.float64)

    if HAS_NUMBA:
        return _generate_numba(n, coeffs, cum)

    pts  = np.empty((n, 2), dtype=np.float32)
    cidx = np.empty(n,      dtype=np.int32)
    x = y = 0.0
    for i in range(n):
        r   = np.random.random()
        idx = int(np.searchsorted(cum, r))
        idx = min(idx, len(transforms) - 1)
        a, b, c, d, e, f = coeffs[idx]
        nx = a*x + b*y + e
        ny = c*x + d*y + f
        x, y = nx, ny
        pts[i, 0]  = x
        pts[i, 1]  = y
        cidx[i]    = idx
    return pts, cidx


# ── fast pixel-buffer renderer ────────────────────────────────────────────────
def render_to_rgba(pts, cidx, palette_name, width=800, height=800):
    """
    Paint each point as a single pixel into an RGBA array.
    Far faster than scatter() for large N.
    """
    colors = PALETTES[palette_name]
    rgba_map = np.array([to_rgba(c) for c in colors], dtype=np.float32)

    xs, ys = pts[:, 0], pts[:, 1]
    pad = 0.04
    xmin, xmax = xs.min(), xs.max()
    ymin, ymax = ys.min(), ys.max()
    xr = xmax - xmin or 1.0
    yr = ymax - ymin or 1.0

    # pixel coordinates
    px = ((xs - xmin) / xr * (1 - 2*pad) + pad) * (width  - 1)
    py = ((ys - ymin) / yr * (1 - 2*pad) + pad) * (height - 1)
    py = (height - 1) - py  # flip y

    ix = np.clip(px.astype(np.int32), 0, width  - 1)
    iy = np.clip(py.astype(np.int32), 0, height - 1)

    # accumulate hit counts per pixel per colour
    img = np.zeros((height, width, 4), dtype=np.float32)
    cnt = np.zeros((height, width),    dtype=np.int32)

    for c in range(len(colors)):
        mask = cidx == c
        np.add.at(img[:, :, 0], (iy[mask], ix[mask]), rgba_map[c, 0])
        np.add.at(img[:, :, 1], (iy[mask], ix[mask]), rgba_map[c, 1])
        np.add.at(img[:, :, 2], (iy[mask], ix[mask]), rgba_map[c, 2])
        np.add.at(cnt,          (iy[mask], ix[mask]), 1)

    hit = cnt > 0
    for ch in range(3):
        img[:, :, ch][hit] /= cnt[hit]
    img[:, :, 3] = np.where(hit, 1.0, 0.0)

    return np.clip(img, 0, 1)


# ── main interactive app ──────────────────────────────────────────────────────
class FernApp:
    PIXEL_W = 700
    PIXEL_H = 700

    def __init__(self):
        self.transforms  = [dict(t) for t in DEFAULT_TRANSFORMS]
        self.palette_idx = 0
        self._pending    = False   # debounce flag

        self._build_ui()
        self._render()

    # ── layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.fig = plt.figure(figsize=(12, 8), facecolor="#1a1a2e")
        self.fig.canvas.manager.set_window_title("Barnsley Fern")

        # image axis (left ~60 %)
        self.ax_img = self.fig.add_axes([0.01, 0.02, 0.58, 0.96])
        self.ax_img.set_facecolor("#0d0d1a")
        self.ax_img.axis("off")
        blank = np.zeros((self.PIXEL_H, self.PIXEL_W, 4), dtype=np.float32)
        self.im = self.ax_img.imshow(blank, origin="upper", aspect="equal",
                                     interpolation="nearest")
        self.title_text = self.ax_img.set_title(
            "Barnsley Fern", color="white", fontsize=13, pad=6)

        col  = "#2a2a4a"
        tcol = "#aaaacc"

        def sl(left, bot, label, vmin, vmax, vinit, step=0.01):
            ax = self.fig.add_axes([left, bot, 0.32, 0.022], facecolor=col)
            s  = mwidgets.Slider(ax, label, vmin, vmax, valinit=vinit,
                                 valstep=step, color="#4466aa")
            s.label.set_color(tcol); s.label.set_fontsize(8.5)
            s.valtext.set_color("white"); s.valtext.set_fontsize(8)
            s.on_changed(self._on_slider)
            return s

        L, W2 = 0.62, 0.32
        # probabilities
        self.s_p1 = sl(L, 0.90, "Stem prob",        0.00, 0.10, 0.01, 0.005)
        self.s_p2 = sl(L, 0.86, "Frond prob",       0.60, 0.97, 0.85, 0.005)
        self.s_p3 = sl(L, 0.82, "Left leaflet prob",0.01, 0.20, 0.07, 0.005)
        # transform 2 coefficients
        self.s_a  = sl(L, 0.72, "f2  scale X (a)",  0.50, 0.99, 0.85)
        self.s_d  = sl(L, 0.68, "f2  scale Y (d)",  0.50, 0.99, 0.85)
        self.s_b  = sl(L, 0.64, "f2  shear   (b)", -0.20, 0.20, 0.04)
        self.s_c  = sl(L, 0.60, "f2  lean    (c)", -0.20, 0.20,-0.04)
        # variation
        self.s_e  = sl(L, 0.50, "Trunk lean  (e)",  -0.5,  0.5, 0.00)
        self.s_f  = sl(L, 0.46, "Height off  (f)",   1.2,  2.0, 1.60)

        # palette radio
        ax_pal = self.fig.add_axes([0.62, 0.28, 0.32, 0.13], facecolor=col)
        ax_pal.set_title("Palette", color=tcol, fontsize=8.5, pad=3)
        self.radio = mwidgets.RadioButtons(ax_pal, PALETTE_NAMES,
                                           active=0, activecolor="#4488ff")
        for lbl in self.radio.labels:
            lbl.set_fontsize(8.5); lbl.set_color("white")
        self.radio.on_clicked(self._on_palette)

        # buttons
        def btn(left, bot, label):
            ax = self.fig.add_axes([left, bot, 0.14, 0.038], facecolor="#334466")
            b  = mwidgets.Button(ax, label, color="#334466", hovercolor="#4466aa")
            b.label.set_color("white"); b.label.set_fontsize(8.5)
            return b

        self.btn_reset  = btn(0.62, 0.18, "↺  Reset defaults")
        self.btn_regen  = btn(0.80, 0.18, "⟳  Re-randomise")
        self.btn_save   = btn(0.62, 0.12, "⬇  Save PNG")
        self.btn_hiRes  = btn(0.80, 0.12, "★  Hi-res PNG")

        self.btn_reset.on_clicked(self._on_reset)
        self.btn_regen.on_clicked(lambda e: self._render())
        self.btn_save.on_clicked(lambda e: self._save(dpi=150))
        self.btn_hiRes.on_clicked(lambda e: self._save(dpi=400))

        # status label
        self.ax_status = self.fig.add_axes([0.62, 0.06, 0.32, 0.04])
        self.ax_status.axis("off")
        self.status = self.ax_status.text(
            0.0, 0.5, f"{'Numba ✓' if HAS_NUMBA else 'pure NumPy'}  |  {N_POINTS:,} pts",
            color=tcol, fontsize=8, va="center")

        # section headers (static text)
        for y, label in [(0.945, "PROBABILITIES"),
                         (0.760, "FROND SHAPE"),
                         (0.525, "VARIATION")]:
            self.fig.text(0.62, y, label, color="#6688bb",
                          fontsize=7.5, fontweight="bold")

    # ── event handlers ────────────────────────────────────────────────────────
    def _on_slider(self, _val):
        # debounce: schedule a redraw 120ms after last slider touch
        if not self._pending:
            self._pending = True
            self.fig.canvas.start_event_loop(0.12)
            self._pending = False
            self._render()

    def _on_palette(self, _label):
        self.palette_idx = PALETTE_NAMES.index(_label)
        if self._pts is not None:
            self._redraw()

    def _on_reset(self, _event):
        self.s_p1.set_val(0.01)
        self.s_p2.set_val(0.85)
        self.s_p3.set_val(0.07)
        self.s_a.set_val(0.85);  self.s_d.set_val(0.85)
        self.s_b.set_val(0.04);  self.s_c.set_val(-0.04)
        self.s_e.set_val(0.00);  self.s_f.set_val(1.60)
        self._render()

    # ── data → transforms ────────────────────────────────────────────────────
    def _read_transforms(self):
        p1 = self.s_p1.val
        p2 = self.s_p2.val
        p3 = self.s_p3.val
        p4 = max(0.001, 1 - p1 - p2 - p3)
        return [
            dict(a=0,          b=0,          c=0,          d=0.16,
                 e=0,          f=0,          prob=p1),
            dict(a=self.s_a.val, b=self.s_b.val, c=self.s_c.val, d=self.s_d.val,
                 e=self.s_e.val, f=self.s_f.val, prob=p2),
            dict(a=0.20, b=-0.26, c=0.23, d=0.22, e=0, f=1.6,  prob=p3),
            dict(a=-0.15, b=0.28, c=0.26, d=0.24, e=0, f=0.44, prob=p4),
        ]

    # ── rendering ────────────────────────────────────────────────────────────
    def _render(self):
        t0 = time.perf_counter()
        transforms  = self._read_transforms()
        pts, cidx   = generate_points(transforms)
        self._pts   = pts
        self._cidx  = cidx
        self._transforms = transforms
        self._redraw()
        ms = (time.perf_counter() - t0) * 1000
        self.status.set_text(
            f"{'Numba ✓' if HAS_NUMBA else 'NumPy'}  |  {N_POINTS:,} pts  |  {ms:.0f} ms")
        self.fig.canvas.draw_idle()

    def _redraw(self):
        pname = PALETTE_NAMES[self.palette_idx]
        img   = render_to_rgba(self._pts, self._cidx, pname,
                               self.PIXEL_W, self.PIXEL_H)
        self.im.set_data(img)
        self.im.set_extent([0, self.PIXEL_W, self.PIXEL_H, 0])
        self.fig.canvas.draw_idle()

    # ── save ─────────────────────────────────────────────────────────────────
    def _save(self, dpi=300):
        pname    = PALETTE_NAMES[self.palette_idx]
        w = h    = int(dpi * 6)       # 6-inch square at target dpi
        pts, cidx = generate_points(self._transforms, n=600_000)
        img      = render_to_rgba(pts, cidx, pname, w, h)

        fig2, ax2 = plt.subplots(figsize=(6, 6), facecolor="black")
        ax2.imshow(img, origin="upper", interpolation="nearest")
        ax2.axis("off")
        fname = f"fern_{pname}_{dpi}dpi.png"
        fig2.savefig(fname, dpi=dpi, bbox_inches="tight", pad_inches=0)
        plt.close(fig2)
        self.status.set_text(f"Saved → {fname}")
        self.fig.canvas.draw_idle()
        print(f"Saved: {fname}")

    def _pts(self): return None  # placeholder before first render

    def show(self):
        plt.show()


# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not HAS_NUMBA:
        warnings.warn(
            "Numba not found — using pure NumPy (still fast, but Numba is faster).\n"
            "Install with:  pip install numba", stacklevel=1)
    app = FernApp()
    app.show()
