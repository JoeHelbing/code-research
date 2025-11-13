# 3D Interactive Plots with FastHTML

This experiment demonstrates how to embed interactive 3D visualizations in FastHTML pages using Plotly.

## Overview

These examples show different types of 3D visualizations that can be embedded directly into FastHTML applications:

1. **3D Surface Plot** (`01_3d_surface.py`) - Visualizes the Sombrero (Mexican Hat) function
2. **3D Scatter Plot** (`02_3d_scatter.py`) - Shows multiple data clusters in 3D space
3. **Parametric 3D Surfaces** (`03_3d_parametric.py`) - Displays a torus and helix with custom styling
4. **Prerendered Static HTML** (`prerender_plots.py`) - Generates a single HTML file with all three plots embedded

## Quick Start

### View Prerendered Plots (No Server Required!)

Simply open `interactive_plots.html` in your web browser. This file contains all three interactive visualizations and works completely offline!

### Regenerate the Static HTML

```bash
python3 prerender_plots.py
```

This will regenerate `interactive_plots.html` with all three plots embedded in a single, self-contained file.

## Key Features

- **Fully Interactive**: Rotate, zoom, pan, and hover to explore the visualizations
- **No External Dependencies**: Plots are embedded directly in the HTML using Plotly's CDN
- **Responsive Design**: Works on different screen sizes
- **Customizable**: Easy to modify colors, layouts, and mathematical functions

## How It Works

The integration uses Plotly's `to_html()` method with these key parameters:
- `include_plotlyjs='cdn'` - Loads Plotly.js from CDN (lightweight, no local files needed)
- `div_id='...'` - Sets a unique ID for the plot container
- `full_html=False` - Returns only the plot div, not a complete HTML document

The plot HTML is then embedded in FastHTML using `NotStr()` to prevent HTML escaping:

```python
plot_html = fig.to_html(include_plotlyjs='cdn', div_id='my-plot', full_html=False)
return Titled("My Page",
    Div(NotStr(plot_html))
)
```

## Setup

Install dependencies using pixi:

```bash
cd 3d-interactive-plots
pixi install
```

## Running the Examples

Run any of the examples:

```bash
pixi run python 01_3d_surface.py
# or
pixi run python 02_3d_scatter.py
# or
pixi run python 03_3d_parametric.py
```

Then open your browser to `http://localhost:5001` (or the port shown in the terminal).

## Mathematical Functions

### Sombrero Function (01_3d_surface.py)
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

## Customization

You can easily customize these visualizations:

- **Colors**: Change `colorscale` (e.g., 'Viridis', 'Plasma', 'Rainbow')
- **Camera Angle**: Modify the `camera` dict in `scene`
- **Size**: Adjust `width` and `height` in `update_layout()`
- **Mathematical Functions**: Replace the Z calculation with any function of X and Y

## Use Cases

- Data visualization dashboards
- Scientific computing applications
- Educational tools for mathematics and physics
- Interactive data exploration
- 3D model viewers
- Molecular structure visualization
- Terrain mapping

## Technologies Used

- **FastHTML**: Python web framework
- **Plotly**: Interactive graphing library
- **NumPy**: Numerical computing
- **Pixi**: Package manager
