"""
Experiment: Interactive 3D Surface Plot with PyVista
This demonstrates how to embed an interactive PyVista 3D surface plot in a FastHTML page.
PyVista provides excellent 3D visualization with VTK.js backend for web.
"""

from fasthtml.common import *
import pyvista as pv
import numpy as np
import tempfile
import os

app, rt = fast_app()


def create_pyvista_3d_surface():
    """Create an interactive 3D surface plot using PyVista."""
    # Create data for a 3D surface
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)

    # Sombrero function
    R = np.sqrt(X**2 + Y**2) + 1e-10
    Z = np.sin(R) / R * 5

    # Create PyVista structured grid
    grid = pv.StructuredGrid(X, Y, Z)

    # Add the Z values as a scalar field for coloring
    grid['Z Values'] = Z.ravel(order='F')

    # Create a plotter
    plotter = pv.Plotter(notebook=False, off_screen=True)
    plotter.add_mesh(grid, scalars='Z Values', cmap='viridis', show_edges=False)
    plotter.view_isometric()
    plotter.add_axes()

    # Export to HTML string
    html_str = plotter.export_html(None, backend='pythreejs')
    plotter.close()

    return html_str


@rt('/')
def get():
    try:
        plot_html = create_pyvista_3d_surface()

        return Titled("3D Surface with PyVista",
            # Header section
            Div(
                H1("PyVista 3D Visualization",
                   style="color: #2563eb; text-align: center; margin-bottom: 10px;"),
                P("High-quality 3D visualization using PyVista with pythreejs backend",
                  style="text-align: center; color: #64748b; font-size: 18px; margin-bottom: 30px;"),
                style="padding: 20px;"
            ),

            # Instructions
            Div(
                H3("Features:", style="color: #7c3aed; margin-bottom: 15px;"),
                Ul(
                    Li("Fully interactive 3D mesh visualization"),
                    Li("Powered by VTK and Three.js"),
                    Li("Excellent for scientific visualization"),
                    Li("Supports complex geometries and meshes"),
                    style="color: #475569; font-size: 16px; line-height: 1.8;"
                ),
                style="max-width: 900px; margin: 0 auto 30px auto; padding: 20px; background-color: #f8fafc; border-radius: 8px; border-left: 4px solid #7c3aed;"
            ),

            # The PyVista plot
            Div(
                NotStr(plot_html),
                style="margin: 20px auto; max-width: 950px;"
            ),

            # Info section
            Div(
                H3("About PyVista", style="color: #059669; margin-bottom: 15px;"),
                P("PyVista is a powerful 3D visualization library built on VTK (Visualization Toolkit). "
                  "It provides sophisticated mesh handling and rendering capabilities, making it ideal "
                  "for scientific computing, engineering simulations, and medical imaging.",
                  style="color: #334155; line-height: 1.6; margin-bottom: 10px;"),
                P("The HTML export uses pythreejs (Three.js) for WebGL-based rendering, providing "
                  "excellent performance for complex 3D scenes.",
                  style="color: #334155; line-height: 1.6;"),
                style="max-width: 900px; margin: 30px auto; padding: 20px; background-color: #f0fdfa; border-radius: 8px;"
            ),

            # Footer
            Div(
                P("Built with FastHTML + PyVista", style="color: white; margin: 0;"),
                style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin-top: 40px;"
            )
        )
    except Exception as e:
        return Titled("PyVista Error",
            Div(
                H1("PyVista Configuration Error", style="color: #dc2626;"),
                P(f"Error: {str(e)}", style="color: #991b1b; font-family: monospace;"),
                P("PyVista requires additional system dependencies and may need a display server. "
                  "It works best in environments with proper graphics support.",
                  style="margin-top: 20px; color: #64748b;"),
                style="padding: 40px; max-width: 800px; margin: 0 auto;"
            )
        )


if __name__ == '__main__':
    serve()
