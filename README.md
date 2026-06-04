# 🌿 Barnsley Fern

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

> A real-time visualization of the beautiful Barnsley Fern fractal using Python and Matplotlib 🌱
>
> *Watch mathematics come alive as the fern generates before your eyes!*

## 📖 Overview

The **Barnsley Fern** is a classic example of an iterated function system (IFS) fractal, first described by mathematician **Michael Barnsley**. This repository contains both a simple implementation and an advanced interactive application to generate and visualize stunning fern patterns.

🎨 **What makes it special?** Every run produces a naturally-looking fern leaf with stunning fractal detail, without any pre-defined image or pattern!

## ✨ Features

### Basic Implementation (`Barnsley_fern.py`)
- 🎬 **Real-time visualization** - Watch the fern grow point by point
- 🔄 **Interactive plotting** - Updates periodically during generation
- ⚙️ **Customizable parameters** - Adjust iteration count and update frequency
- 📊 **High-resolution output** - 100,000+ points for detailed fern structure
- 🎯 **Perfectly scaled** - Optimized display for beautiful presentation
- 💾 **Memory efficient** - Smart update intervals for smooth performance

### Advanced Interactive Version (`Barnsley_updated.py`)
- 🎨 **Multi-palette support** - Choose from 5 beautiful color schemes:
  - Classic Green
  - Night (Purple)
  - Autumn (Orange)
  - Ocean (Blue)
  - Mono (Grayscale)
- 🎚️ **Interactive sliders** - Real-time control of:
  - Probability of each transformation
  - Frond shape parameters (scale, shear, lean)
  - Trunk positioning and height
- ⚡ **Numba acceleration** - Optional JIT compilation for 5-10x speedup
- 📸 **Export options** - Save at standard (150 DPI) or high resolution (400 DPI)
- 🎲 **600,000+ points** - Ultra-detailed rendering with advanced pixel buffer
- 🔧 **Full transformation control** - Modify all IFS coefficients dynamically

## 📦 Requirements

- 🐍 Python 3.6 or higher
- 📈 Matplotlib 3.0+
- 🔢 NumPy
- 🎲 Random (standard library)
- ⚡ Numba (optional, for ~5-10x speedup)

## 🚀 Installation

1. 📥 Clone the repository:
```bash
git clone https://github.com/priyankardas2007/Barnsley_Fern.git
cd Barnsley_Fern
```

2. 📦 Install the required dependencies:
```bash
pip install matplotlib numpy
```

3. (Optional) Install Numba for faster rendering:
```bash
pip install numba
```

## 🎯 Quick Start

### Basic Version

```bash
python Barnsley_fern.py
```

Simply run the script and watch the fern grow in real-time! The window updates every 1,000 points, and the final result displays 100,000 total points.

### Advanced Interactive Version

```bash
python Barnsley_updated.py
```

Launch the interactive GUI with:
- **Live sliders** to control transformation parameters
- **Color palette selector** for different artistic styles
- **Re-randomise button** to generate new fern variations
- **Save buttons** for standard and high-resolution PNG export
- **Reset button** to return to default settings

### Customization Examples (Basic Version)

**Increase iterations for more detail:**
```python
# In Barnsley_fern.py, modify the iterations parameter
iterations = 200000  # Default: 100,000
```

**Adjust update frequency:**
```python
# Update display every N points for faster/smoother rendering
if i % 1000 == 0 and i > 0:  # Change 1000 to desired interval
```

**Change colors:**
```python
# Customize the fern color
ax.scatter(x_data, y_data, s=0.2, c='darkgreen', marker='.')
```

## 🧮 How It Works

The Barnsley Fern uses four affine transformations with specific probabilities:

| Probability | Transformation | Purpose | Coefficients |
|-------------|---|---|---|
| 1% | Stem | Creates the main trunk | a=0, b=0, c=0, d=0.16, e=0, f=0 |
| 85% | Frond | Builds the fern structure | a=0.85, b=0.04, c=-0.04, d=0.85, e=0, f=1.6 |
| 7% | Left leaflet | Left side symmetry | a=0.20, b=-0.26, c=0.23, d=0.22, e=0, f=1.6 |
| 7% | Right leaflet | Right side symmetry | a=-0.15, b=0.28, c=0.26, d=0.24, e=0, f=0.44 |

Each new point is computed by randomly selecting one of these transformations and applying it to the previous point. This creates the stunning self-similar fractal pattern!

### The Algorithm
```
1. Start at origin (0, 0)
2. Generate random number r between 0 and 1
3. Select transformation based on r:
   - If r < 0.01: Apply stem transformation
   - Else if r < 0.86: Apply frond transformation
   - Else if r < 0.93: Apply left leaflet transformation
   - Else: Apply right leaflet transformation
4. Calculate new point using: (x', y') = (ax + by + e, cx + dy + f)
5. Plot the new point
6. Repeat 100,000+ times
```

### Mathematical Beauty 🌟
- **Fractal Dimension**: The fern exhibits fractional dimensions (not an integer)
- **Self-Similarity**: Zooming in reveals the same pattern repeating at different scales
- **Deterministic Chaos**: Random selection + deterministic math = predictable beauty
- **Iterated Function System (IFS)**: A set of contractive affine transformations

## 📊 Output Examples

### Basic Version
```
Expected Output:
✓ A beautiful green fern-like shape fills the screen
✓ The fern grows smoothly from bottom to top
✓ Fine details emerge as iterations increase
✓ Display updates in real-time (every 1,000 iterations)
```

### Advanced Version
```
Expected Output:
✓ High-quality fern visualization with chosen color palette
✓ Interactive UI with responsive sliders
✓ Real-time parameter adjustment
✓ Smooth rendering with optional Numba acceleration
✓ Export capability at multiple resolutions
```

## 🎮 Interactive Features (Advanced Version)

**Parameter Control:**
- **Probability sliders** - Adjust relative frequency of each transformation
- **Frond shape controls** - Modify scale, shear, and lean parameters
- **Variation sliders** - Control trunk positioning and height offset

**Visual Customization:**
- **5 color palettes** - Switch between artistic color schemes
- **Real-time updates** - See changes as you move sliders (with debouncing)
- **Palette preview** - Radio buttons for easy selection

**Export Options:**
- **Save PNG (150 DPI)** - Standard quality for sharing
- **Save PNG (400 DPI)** - High resolution for printing
- **Auto-naming** - Files saved as `fern_[palette]_[dpi]dpi.png`

## 🔧 Troubleshooting

**Issue: Plot is too slow**
- Try the advanced version with Numba acceleration
- Increase `update_interval` to reduce display updates
- Decrease `iterations` for faster completion

**Issue: Fern looks too sparse**
- Increase `iterations` for more detail
- Check that `update_interval` isn't too large
- Ensure transform probabilities sum to ~1.0

**Issue: Color doesn't show**
- Verify Matplotlib backend supports your display
- Try different color names: 'darkgreen', 'green', '#228B22', etc.
- For advanced version, try different palettes

**Issue: Numba not found (Advanced version)**
- Install with: `pip install numba`
- The script will still run with pure NumPy if Numba isn't available
- Numba provides ~5-10x speedup on point generation

**Issue: Sliders not responding (Advanced version)**
- Ensure you're using Matplotlib with interactive backend
- Try `python -m matplotlib` to check your setup
- Update Matplotlib if needed

## 📚 Learn More

**About Fractals:**
- [Wikipedia: Iterated Function System](https://en.wikipedia.org/wiki/Iterated_function_system)
- [Wikipedia: Barnsley Fern](https://en.wikipedia.org/wiki/Barnsley_fern)
- [Fractals Explained](https://en.wikipedia.org/wiki/Fractal)

**About Michael Barnsley:**
- Pioneer in fractal geometry and chaos theory
- Developed the concept of iterated function systems (IFS)
- Creator of the "Collage theorem"

**Related Concepts:**
- Affine transformations and linear algebra
- Probability theory and stochastic processes
- Self-similar structures in nature

## 🎓 Educational Value

Perfect for learning about:
- ✅ Fractals and self-similarity
- ✅ Probability and random processes
- ✅ Data visualization in Python
- ✅ Iterated function systems (IFS)
- ✅ Mathematical beauty in nature
- ✅ Performance optimization (Numba)
- ✅ GUI design with Matplotlib widgets

## 💡 Extension Ideas

Try these modifications to explore further:

1. **Different Fractals**: Implement the Sierpinski Triangle or Julia Set
2. **3D Visualization**: Extend to 3D coordinates with matplotlib 3D
3. **Animation**: Save frames to create a time-lapse video
4. **Color Mapping**: Use gradient colors based on iteration number or point age
5. **Statistics**: Calculate fractal dimension or analyze point distribution
6. **Advanced GUI**: Add more controls with tkinter or PyQt
7. **Performance Analysis**: Benchmark different optimization techniques
8. **Custom Palettes**: Create your own color schemes
9. **Export Formats**: Add SVG or PDF export
10. **Real-time Zoom**: Implement interactive zooming into fractal regions

## 📁 Repository Structure

```
Barnsley_Fern/
├── README.md                  # This file
├── Barnsley_fern.py          # Simple, straightforward implementation
├── Barnsley_updated.py       # Advanced interactive version with GUI
└── LICENSE                   # MIT License
```

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- ✨ Suggest improvements
- 📝 Add documentation
- 🚀 Submit pull requests
- 🎨 Create new variations or fractals

## 👨‍💻 Author

Created by **Priyankardas2007**

---

### ⭐ If you found this interesting, please give it a star! It helps others discover the beauty of fractals.

*Happy fractal exploring! 🌿✨*
