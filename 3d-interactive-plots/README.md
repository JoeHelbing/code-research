# 3D Interactive Plots with FastHTML

This experiment demonstrates how to embed interactive 3D visualizations in FastHTML pages using **multiple plotting libraries**, comparing their strengths, weaknesses, and use cases.

## 🎯 Quick Start - View All Comparisons

**Option 1: Comprehensive Comparison (Recommended)**
```bash
python3 compare_all_packages.py
```
Then open `comparison_all_packages.html` in your browser to see all four libraries side-by-side with pros/cons analysis!

**Option 2: View Original Plotly Examples**
Simply open `interactive_plots.html` in your browser - works completely offline!

## 📊 Libraries Tested

| Library | 3D Interactive | Web-Ready | Ease of Use | Best For | Rating |
|---------|---------------|-----------|-------------|----------|--------|
| **Plotly** | ✅ Excellent | ✅ Excellent | ⭐⭐⭐⭐⭐ | Dashboards, general 3D | **9.5/10** |
| **PyVista** | ✅ Excellent | 🟡 Good | ⭐⭐⭐⭐ | Scientific viz, CAD | **8.5/10** |
| **Bokeh** | ❌ Limited (2D only) | ✅ Excellent | ⭐⭐⭐⭐⭐ | 2D interactive only | **6/10** |
| **Matplotlib+mpld3** | ❌ No 3D support | 🟡 Fair | ⭐⭐⭐⭐⭐ | Static 3D images | **5/10** |

## 🚀 Examples Included

### Plotly (Files: 01-03)
1. **3D Surface Plot** (`01_3d_surface.py`) - Visualizes the Sombrero (Mexican Hat) function
2. **3D Scatter Plot** (`02_3d_scatter.py`) - Shows multiple data clusters in 3D space
3. **Parametric 3D Surfaces** (`03_3d_parametric.py`) - Displays a torus and helix with custom styling
4. **Prerendered Static HTML** (`prerender_plots.py`) - Generates a single HTML file with all three plots

### Additional Libraries (Files: 04-06)
4. **Bokeh** (`04_bokeh_3d.py`) - Demonstrates Bokeh's limitations for 3D (shows 2D heatmap instead)
5. **PyVista** (`05_pyvista_3d.py`) - Professional scientific 3D visualization with VTK backend
6. **Matplotlib + mpld3** (`06_matplotlib_mpld3.py`) - Shows why matplotlib/mpld3 doesn't work for interactive 3D

### Comparison Tool
7. **Compare All Packages** (`compare_all_packages.py`) - Generates comprehensive side-by-side comparison HTML

## 📦 Setup

Install dependencies using pixi:

```bash
cd 3d-interactive-plots
pixi install
```

This will install:
- `plotly` - Interactive web-based plotting
- `pyvista` - Scientific 3D visualization
- `bokeh` - Interactive 2D/limited 3D plotting
- `matplotlib` + `mpld3` - Traditional plotting with web export
- `numpy`, `pandas` - Data manipulation
- `python-fasthtml` - Web framework

## 🎨 Detailed Comparison

### 1. Plotly ⭐⭐⭐⭐⭐ (9.5/10)

**The Winner for Web-Based 3D Visualization**

#### ✅ Pros
- **Excellent 3D interactivity** - Rotate, zoom, pan works flawlessly
- **Web-native design** - Built specifically for web applications
- **Easy integration** - Simple `to_html()` method with CDN support
- **Beautiful aesthetics** - Modern, professional-looking plots
- **Great documentation** - Extensive examples and guides
- **No special requirements** - Works everywhere, no display server needed

#### ❌ Cons
- Limited mesh editing capabilities
- Not ideal for extremely complex scientific visualizations
- Requires Plotly.js (via CDN or bundled)

#### How to Use
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z, colorscale='Viridis')])
fig.update_layout(title='3D Surface', scene=dict(
    xaxis_title='X', yaxis_title='Y', zaxis_title='Z'
))
html = fig.to_html(include_plotlyjs='cdn', div_id='plot', full_html=False)
```

#### Best For
- Dashboards and data visualization apps
- General-purpose 3D plotting
- Quick prototyping
- Web applications with interactive requirements

---

### 2. PyVista ⭐⭐⭐⭐ (8.5/10)

**Best for Scientific and Engineering Applications**

#### ✅ Pros
- **Professional visualization** - Industry-standard VTK backend
- **Powerful mesh handling** - Excellent for complex geometries
- **Rich feature set** - Advanced rendering, lighting, textures
- **Scientific community** - Widely used in research and engineering
- **Export to HTML** - Can generate interactive web visualizations via pythreejs

#### ❌ Cons
- **System dependencies** - Requires VTK and sometimes display server
- **Steeper learning curve** - More complex API than Plotly
- **Environment sensitive** - May not work in all environments (needs graphics support)
- **Larger output files** - HTML exports can be bigger

#### How to Use
```python
import pyvista as pv

grid = pv.StructuredGrid(X, Y, Z)
grid['Z Values'] = Z.ravel(order='F')

plotter = pv.Plotter(notebook=False, off_screen=True)
plotter.add_mesh(grid, scalars='Z Values', cmap='viridis')
html = plotter.export_html(None, backend='pythreejs')
plotter.close()
```

#### Best For
- Scientific visualization
- Engineering simulations (FEA, CFD)
- CAD model viewing
- Medical imaging (MRI, CT scans)
- Geospatial data visualization

---

### 3. Bokeh ⭐⭐⭐ (6/10)

**Excellent for 2D, Limited for 3D**

#### ✅ Pros
- **Excellent 2D interactivity** - Best-in-class for 2D plots
- **Great web integration** - Purpose-built for web applications
- **Dashboard-friendly** - Perfect for Bokeh Server applications
- **Interactive tooltips** - Rich hover information

#### ❌ Cons
- **NO native 3D support** - Cannot create true interactive 3D plots
- **Limited to 2D projections** - Can only show top-down views with color
- **Not suitable for 3D work** - Must use workarounds (heatmaps, contours)

#### How to Use (2D Representation)
```python
from bokeh.plotting import figure
from bokeh.models import LinearColorMapper

p = figure(title="Top-down view", tooltips=[("Z", "@z")])
p.circle('x', 'y', source=source,
         color={'field': 'z', 'transform': color_mapper})
script, div = components(p)
```

#### Best For
- 2D interactive plots
- Dashboards and monitoring apps
- Time series visualization
- **NOT recommended for 3D visualization**

---

### 4. Matplotlib + mpld3 ⭐⭐ (5/10)

**Not Suitable for Interactive 3D**

#### ✅ Pros
- **Familiar syntax** - If you know matplotlib, easy to use
- **Good for 2D** - Can make 2D plots interactive
- **Static 3D works** - Can create beautiful static 3D images
- **Publication quality** - Great for papers and reports (static)

#### ❌ Cons
- **mpld3 does NOT support 3D** - No 3D interactivity possible
- **3D plots are static only** - Cannot rotate or interact
- **Poor web interactivity** - Limited compared to modern libraries
- **Not recommended for web 3D** - Use Plotly or PyVista instead

#### How to Use
```python
import matplotlib.pyplot as plt
import mpld3

# 2D contour (works)
fig, ax = plt.subplots()
contour = ax.contourf(X, Y, Z, levels=20, cmap='viridis')
html = mpld3.fig_to_html(fig)

# 3D surface (static only - not interactive!)
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis')
plt.savefig('static_3d.png')  # Save as image only
```

#### Best For
- Static 3D plots for papers/reports
- 2D interactive plots (via mpld3)
- **NOT for interactive 3D web visualization**

---

## 🏆 Final Recommendations

### Choose Plotly if you want:
- ✅ Easy-to-use web-based 3D plotting
- ✅ Beautiful, interactive visualizations
- ✅ Quick development and prototyping
- ✅ Universal compatibility
- ✅ **Best overall choice for most use cases**

### Choose PyVista if you want:
- ✅ Professional scientific/engineering visualization
- ✅ Advanced mesh manipulation
- ✅ Complex geometries and simulations
- ✅ Industry-standard VTK backend
- ⚠️ Note: Requires proper environment setup

### Avoid for 3D:
- ❌ Bokeh - No true 3D support
- ❌ Matplotlib + mpld3 - No interactive 3D

---

## 🎯 Running the Examples

### Individual Examples
```bash
# Plotly examples
pixi run python 01_3d_surface.py     # Surface plot
pixi run python 02_3d_scatter.py     # Scatter plot
pixi run python 03_3d_parametric.py  # Parametric surfaces

# Other libraries
pixi run python 04_bokeh_3d.py           # Bokeh (limited 3D)
pixi run python 05_pyvista_3d.py         # PyVista
pixi run python 06_matplotlib_mpld3.py   # Matplotlib

# Generate comparison
pixi run python compare_all_packages.py  # All libraries compared!
```

Then open your browser to `http://localhost:5001` (or the port shown in the terminal).

### Prerender Static Files
```bash
# Original Plotly plots
python3 prerender_plots.py
# Opens: interactive_plots.html

# Comprehensive comparison
python3 compare_all_packages.py
# Opens: comparison_all_packages.html
```

---

## 📐 Mathematical Functions

### Sombrero Function (Used in all examples)
```
z = sin(√(x² + y²)) / √(x² + y²)
```
Creates a classic wave pattern resembling a Mexican sombrero hat.

### Torus (03_3d_parametric.py)
```
x = (R + r·cos(v))·cos(u)
y = (R + r·cos(v))·sin(u)
z = r·sin(v)
```
Where R is the major radius and r is the minor radius.

### Helix (03_3d_parametric.py)
```
x = R·cos(t)
y = R·sin(t)
z = t·k
```
A spiral curve that wraps around a cylinder.

---

## 🎨 Customization Examples

### Plotly
```python
# Change color scheme
fig.update_traces(colorscale='Rainbow')  # or 'Plasma', 'Jet', etc.

# Modify camera angle
fig.update_layout(scene_camera=dict(
    eye=dict(x=2, y=2, z=1.5)
))

# Add custom hover text
fig.update_traces(hovertemplate='X: %{x}<br>Y: %{y}<br>Z: %{z}')
```

### PyVista
```python
# Change colormap
plotter.add_mesh(grid, cmap='plasma')  # or 'coolwarm', 'seismic', etc.

# Add lighting effects
plotter.add_light(pv.Light(position=(10, 10, 10)))

# Adjust camera
plotter.camera_position = 'iso'  # or 'xy', 'xz', 'yz'
```

---

## 📊 Feature Comparison Matrix

| Feature | Plotly | PyVista | Bokeh | Matplotlib |
|---------|--------|---------|-------|------------|
| **3D Surface Plots** | ✅ Excellent | ✅ Excellent | ❌ No | ⚠️ Static only |
| **3D Scatter Plots** | ✅ Yes | ✅ Yes | ❌ No | ⚠️ Static only |
| **Mesh Visualization** | 🟡 Limited | ✅ Excellent | ❌ No | ⚠️ Static only |
| **Web Interactivity** | ✅ Excellent | 🟡 Good | ✅ Excellent (2D) | ❌ Poor |
| **Ease of Setup** | ✅ Very Easy | 🟡 Moderate | ✅ Easy | ✅ Easy |
| **File Size** | 🟡 Medium | 🟡 Large | ✅ Small | ✅ Small |
| **Learning Curve** | ✅ Gentle | 🟡 Steep | ✅ Gentle | ✅ Gentle |
| **Documentation** | ✅ Excellent | ✅ Good | ✅ Good | ✅ Excellent |
| **Performance** | ✅ Good | ✅ Excellent | ✅ Good | 🟡 Fair |

---

## 🛠️ Integration with FastHTML

All examples demonstrate how to integrate plots with FastHTML using `NotStr()`:

```python
from fasthtml.common import *

@rt('/')
def get():
    plot_html = create_plot()  # Generate plot HTML

    return Titled("My 3D Plot",
        Div(NotStr(plot_html))  # Embed without escaping
    )
```

Key points:
- Use `NotStr()` to prevent HTML escaping
- For Plotly: `include_plotlyjs='cdn'` for CDN, or `'cdn'` for self-contained
- For Bokeh: Include Bokeh JS/CSS via Script/Link tags
- For PyVista: HTML string is self-contained

---

## 🎓 Use Cases

### Plotly is Perfect For:
- Data science dashboards
- Business intelligence visualizations
- Educational tools
- Interactive data exploration
- Web applications

### PyVista is Perfect For:
- Finite Element Analysis (FEA)
- Computational Fluid Dynamics (CFD)
- Medical imaging (MRI, CT scans)
- Geophysical modeling
- Molecular structure visualization
- 3D CAD viewing

### Bokeh is Perfect For:
- Real-time data monitoring (2D)
- Time series analysis
- Financial charts
- 2D heatmaps and contours
- **NOT for 3D**

### Matplotlib is Perfect For:
- Static publication figures
- Academic papers
- Reports with embedded images
- **NOT for interactive 3D web apps**

---

## 💡 Pro Tips

1. **For web deployment**: Plotly is the safest choice - works everywhere
2. **For scientific work**: PyVista provides professional-grade capabilities
3. **Avoid assumptions**: Test Bokeh and matplotlib limitations early if considering them
4. **File size matters**: PyVista generates larger files; consider this for web deployment
5. **Environment setup**: PyVista may need system packages (`apt-get install libgl1-mesa-glx xvfb`)

---

## 📚 Technologies Used

- **FastHTML**: Modern Python web framework
- **Plotly**: Industry-leading interactive graphing library
- **PyVista**: 3D visualization and mesh analysis built on VTK
- **Bokeh**: Interactive visualization for modern web browsers
- **Matplotlib**: Comprehensive 2D/3D plotting library
- **mpld3**: Matplotlib to D3.js converter (2D only)
- **NumPy**: Numerical computing
- **Pixi**: Fast package manager

---

## 🎯 Conclusion

**TL;DR: Use Plotly for web-based 3D visualization. Use PyVista for scientific applications. Avoid Bokeh and Matplotlib for interactive 3D.**

Generate the comparison HTML to see all libraries in action:
```bash
python3 compare_all_packages.py
```

Happy visualizing! 🚀
