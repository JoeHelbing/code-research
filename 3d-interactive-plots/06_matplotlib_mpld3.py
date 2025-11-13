"""
Experiment: 3D Plot with Matplotlib + mpld3
This demonstrates the limitations of using Matplotlib with mpld3 for 3D interactive plots.
mpld3 does NOT support 3D plots, so we show a 2D contour/heatmap instead.
"""

from fasthtml.common import *
import matplotlib.pyplot as plt
import numpy as np
import mpld3
from io import BytesIO
import base64

app, rt = fast_app()


def create_matplotlib_2d_representation():
    """
    Create a 2D representation since mpld3 doesn't support 3D plots.
    Shows both a contour plot and a surface plot image.
    """
    # Create data
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)

    # Sombrero function
    R = np.sqrt(X**2 + Y**2) + 1e-10
    Z = np.sin(R) / R * 5

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Contour plot (interactive with mpld3)
    contour = ax1.contourf(X, Y, Z, levels=20, cmap='viridis')
    ax1.set_xlabel('X')
    ax1.set_ylabel('Y')
    ax1.set_title('Interactive 2D Contour (mpld3)')
    plt.colorbar(contour, ax=ax1, label='Z value')

    # 3D plot as static image (matplotlib 3D doesn't work with mpld3)
    from mpl_toolkits.mplot3d import Axes3D
    ax2 = fig.add_subplot(122, projection='3d')
    surf = ax2.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    ax2.set_xlabel('X')
    ax2.set_ylabel('Y')
    ax2.set_zlabel('Z')
    ax2.set_title('Static 3D Surface (not interactive)')
    ax2.view_init(elev=30, azim=45)

    plt.tight_layout()

    # Convert to HTML using mpld3
    html_str = mpld3.fig_to_html(fig)
    plt.close()

    return html_str


def create_3d_matplotlib_static():
    """Create a static 3D plot to show what matplotlib CAN do (but not interactively)."""
    from mpl_toolkits.mplot3d import Axes3D

    x = np.linspace(-5, 5, 50)
    y = np.linspace(-5, 5, 50)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2) + 1e-10
    Z = np.sin(R) / R * 5

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.9, linewidth=0, antialiased=True)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Matplotlib 3D Surface (Static Image)')
    ax.view_init(elev=25, azim=135)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

    # Convert to base64 image
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()

    return f'<img src="data:image/png;base64,{img_str}" style="max-width: 100%; height: auto;" />'


@rt('/')
def get():
    plot_html = create_matplotlib_2d_representation()
    static_3d = create_3d_matplotlib_static()

    return Titled("Matplotlib + mpld3 Limitations",
        # Header section
        Div(
            H1("Matplotlib with mpld3",
               style="color: #2563eb; text-align: center; margin-bottom: 10px;"),
            P("Demonstrating the limitations: mpld3 does NOT support 3D plots",
              style="text-align: center; color: #64748b; font-size: 18px; margin-bottom: 30px;"),
            style="padding: 20px;"
        ),

        # Warning box
        Div(
            H3("⚠️ Important Limitation:", style="color: #dc2626; margin-bottom: 15px;"),
            P("mpld3 is designed to convert 2D matplotlib plots to interactive D3.js visualizations. "
              "It does NOT support 3D plots at all. The 3D projection axis is not recognized.",
              style="color: #991b1b; font-size: 16px; line-height: 1.8; margin-bottom: 10px;"),
            P("Below you'll see: (1) an interactive 2D contour plot, and (2) a static 3D image.",
              style="color: #475569; font-size: 16px; line-height: 1.8;"),
            style="max-width: 900px; margin: 0 auto 30px auto; padding: 20px; background-color: #fef2f2; border-radius: 8px; border-left: 4px solid #dc2626;"
        ),

        # The matplotlib plot
        Div(
            NotStr(plot_html),
            style="margin: 20px auto; max-width: 950px; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
        ),

        # Static 3D example
        Div(
            H3("Matplotlib CAN do 3D... but only as static images", style="color: #059669; margin-bottom: 15px;"),
            Div(
                NotStr(static_3d),
                style="text-align: center; margin: 20px 0;"
            ),
            P("The image above is a static PNG render. Matplotlib's 3D capabilities are excellent "
              "for static visualizations, but they cannot be made interactive in web browsers via mpld3.",
              style="color: #334155; line-height: 1.6;"),
            style="max-width: 900px; margin: 30px auto; padding: 20px; background-color: #f0fdfa; border-radius: 8px;"
        ),

        # Recommendations
        Div(
            H3("Recommendation", style="color: #7c3aed; margin-bottom: 15px;"),
            P("For interactive 3D plots in web applications, use:",
              style="color: #334155; font-weight: bold; margin-bottom: 10px;"),
            Ul(
                Li("Plotly - Best overall for web-based 3D interactivity"),
                Li("PyVista - Excellent for scientific/engineering visualization"),
                Li("Bokeh - Limited 3D, but good for 2D interactive plots"),
                style="color: #475569; font-size: 16px; line-height: 1.8;"
            ),
            style="max-width: 900px; margin: 30px auto; padding: 20px; background-color: #faf5ff; border-radius: 8px;"
        ),

        # Footer
        Div(
            P("Built with FastHTML + Matplotlib + mpld3", style="color: white; margin: 0;"),
            style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin-top: 40px;"
        )
    )


if __name__ == '__main__':
    serve()
