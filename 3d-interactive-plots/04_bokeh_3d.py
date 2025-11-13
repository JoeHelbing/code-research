"""
Experiment: Interactive 3D Surface Plot with Bokeh
This demonstrates how to embed an interactive Bokeh 3D surface plot in a FastHTML page.
Note: Bokeh has limited native 3D support, so we use a Surface3d plot.
"""

from fasthtml.common import *
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
import numpy as np

app, rt = fast_app()


def create_bokeh_3d_surface():
    """Create an interactive surface visualization using Bokeh."""
    # Create data for a 3D surface
    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)

    # Sombrero function
    R = np.sqrt(X**2 + Y**2) + 1e-10
    Z = np.sin(R) / R * 5

    # Bokeh doesn't have native 3D plotting like Plotly,
    # but we can create a heatmap/contour representation
    from bokeh.models import LinearColorMapper
    from bokeh.palettes import Viridis256

    # Flatten the arrays for Bokeh
    x_flat = X.flatten()
    y_flat = Y.flatten()
    z_flat = Z.flatten()

    source = ColumnDataSource(data=dict(
        x=x_flat,
        y=y_flat,
        z=z_flat,
    ))

    # Create color mapper
    color_mapper = LinearColorMapper(palette=Viridis256, low=z_flat.min(), high=z_flat.max())

    # Create figure with hover tool
    p = figure(
        width=800,
        height=700,
        title="Bokeh Surface (Top-down view with color representing Z)",
        x_axis_label='X',
        y_axis_label='Y',
        tools="pan,wheel_zoom,box_zoom,reset,save",
        tooltips=[("X", "@x{0.00}"), ("Y", "@y{0.00}"), ("Z", "@z{0.00}")]
    )

    # Plot as circles with color representing Z value
    p.circle('x', 'y', size=3, source=source,
             color={'field': 'z', 'transform': color_mapper},
             alpha=0.8)

    # Get the script and div components
    script, div = components(p)

    return script, div


@rt('/')
def get():
    script, div = create_bokeh_3d_surface()

    return Titled("3D Surface with Bokeh",
        # Include Bokeh JS/CSS
        Script(src="https://cdn.bokeh.org/bokeh/release/bokeh-3.3.0.min.js"),
        Link(rel="stylesheet", href="https://cdn.bokeh.org/bokeh/release/bokeh-3.3.0.min.css"),

        # Header section
        Div(
            H1("Bokeh Visualization (Limited 3D)",
               style="color: #2563eb; text-align: center; margin-bottom: 10px;"),
            P("Bokeh provides limited 3D support - shown here as a top-down heatmap",
              style="text-align: center; color: #64748b; font-size: 18px; margin-bottom: 30px;"),
            style="padding: 20px;"
        ),

        # Instructions
        Div(
            H3("Note:", style="color: #dc2626; margin-bottom: 15px;"),
            P("Bokeh doesn't have native 3D plotting support like Plotly. "
              "This visualization shows a top-down view where color represents the Z value. "
              "For true 3D interactive plots, Plotly or PyVista are better choices.",
              style="color: #475569; font-size: 16px; line-height: 1.8;"),
            style="max-width: 900px; margin: 0 auto 30px auto; padding: 20px; background-color: #fef2f2; border-radius: 8px; border-left: 4px solid #dc2626;"
        ),

        # The Bokeh plot
        Div(
            NotStr(script),
            NotStr(div),
            style="display: flex; justify-content: center; margin: 20px auto; max-width: 950px;"
        ),

        # Footer
        Div(
            P("Built with FastHTML + Bokeh", style="color: white; margin: 0;"),
            style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin-top: 40px;"
        )
    )


if __name__ == '__main__':
    serve()
