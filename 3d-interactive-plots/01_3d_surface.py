"""
Experiment: Interactive 3D Surface Plot with FastHTML
This demonstrates how to embed an interactive Plotly 3D surface plot in a FastHTML page.
"""

from fasthtml.common import *
import plotly.graph_objects as go
import numpy as np

app, rt = fast_app()


def create_3d_surface():
    """Create an interactive 3D surface plot of a mathematical function."""
    # Create data for a 3D surface (a saddle/paraboloid)
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)

    # Create an interesting mathematical surface: z = sin(sqrt(x^2 + y^2)) / sqrt(x^2 + y^2)
    # This creates a "sombrero" or "Mexican hat" function
    R = np.sqrt(X**2 + Y**2) + 1e-10  # Add small epsilon to avoid division by zero
    Z = np.sin(R) / R * 5

    # Create the 3D surface plot
    fig = go.Figure(data=[go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale='Viridis',
        showscale=True,
        hovertemplate='x: %{x:.2f}<br>y: %{y:.2f}<br>z: %{z:.2f}<extra></extra>'
    )])

    # Update layout for better visualization
    fig.update_layout(
        title='Interactive 3D Surface: Sombrero Function',
        scene=dict(
            xaxis_title='X Axis',
            yaxis_title='Y Axis',
            zaxis_title='Z Axis',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.3)
            )
        ),
        width=900,
        height=700,
        margin=dict(l=0, r=0, b=0, t=40)
    )

    # Convert to HTML div (without the full HTML template)
    return fig.to_html(include_plotlyjs='cdn', div_id='surface-plot', full_html=False)


@rt('/')
def get():
    plot_html = create_3d_surface()

    return Titled("3D Interactive Surface Plot",
        # Header section
        Div(
            H1("Interactive 3D Visualization with FastHTML",
               style="color: #2563eb; text-align: center; margin-bottom: 10px;"),
            P("Explore the Sombrero function: z = sin(√(x² + y²)) / √(x² + y²)",
              style="text-align: center; color: #64748b; font-size: 18px; margin-bottom: 30px;"),
            style="padding: 20px;"
        ),

        # Instructions
        Div(
            H3("How to interact:", style="color: #7c3aed; margin-bottom: 15px;"),
            Ul(
                Li("Click and drag to rotate the 3D plot"),
                Li("Scroll to zoom in and out"),
                Li("Hover over the surface to see coordinates"),
                Li("Use the toolbar in the top-right to pan, reset, or save the image"),
                style="color: #475569; font-size: 16px; line-height: 1.8;"
            ),
            style="max-width: 900px; margin: 0 auto 30px auto; padding: 20px; background-color: #f8fafc; border-radius: 8px; border-left: 4px solid #7c3aed;"
        ),

        # The 3D plot container
        Div(
            NotStr(plot_html),  # Use NotStr to prevent HTML escaping
            style="display: flex; justify-content: center; margin: 20px auto; max-width: 950px;"
        ),

        # Info section
        Div(
            H3("About this visualization", style="color: #059669; margin-bottom: 15px;"),
            P("This 3D surface plot is generated using Plotly, a powerful interactive graphing library. "
              "The plot is fully interactive and embedded directly into this FastHTML page without any "
              "external iframe or separate page.",
              style="color: #334155; line-height: 1.6; margin-bottom: 10px;"),
            P("The Sombrero function (also known as the Mexican Hat function) is commonly used in "
              "signal processing and wavelet analysis. Its shape resembles a sombrero, with a central "
              "peak surrounded by a trough and diminishing ripples.",
              style="color: #334155; line-height: 1.6;"),
            style="max-width: 900px; margin: 30px auto; padding: 20px; background-color: #f0fdfa; border-radius: 8px;"
        ),

        # Footer
        Div(
            P("Built with FastHTML + Plotly", style="color: white; margin: 0;"),
            style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin-top: 40px;"
        )
    )


if __name__ == '__main__':
    serve()
