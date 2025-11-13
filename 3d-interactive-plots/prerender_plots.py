"""
Prerender all 3D plots to a static HTML file with FastHTML.
This script generates all interactive plots and embeds them in a single HTML file.
"""

from fasthtml.common import *
import plotly.graph_objects as go
import numpy as np
from pathlib import Path


def create_3d_surface():
    """Create an interactive 3D surface plot of the Sombrero function."""
    x = np.linspace(-5, 5, 100)
    y = np.linspace(-5, 5, 100)
    X, Y = np.meshgrid(x, y)

    R = np.sqrt(X**2 + Y**2) + 1e-10
    Z = np.sin(R) / R * 5

    fig = go.Figure(data=[go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale='Viridis',
        showscale=True,
        hovertemplate='x: %{x:.2f}<br>y: %{y:.2f}<br>z: %{z:.2f}<extra></extra>'
    )])

    fig.update_layout(
        title='Sombrero Function: z = sin(√(x² + y²)) / √(x² + y²)',
        scene=dict(
            xaxis_title='X Axis',
            yaxis_title='Y Axis',
            zaxis_title='Z Axis',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        width=1000,
        height=600,
        margin=dict(l=0, r=0, b=0, t=40)
    )

    return fig.to_html(include_plotlyjs='cdn', div_id='surface-plot', full_html=False)


def create_3d_scatter():
    """Create an interactive 3D scatter plot with multiple clusters."""
    np.random.seed(42)
    n_points = 100

    # Cluster 1: Around (0, 0, 0)
    x1 = np.random.randn(n_points) * 0.5
    y1 = np.random.randn(n_points) * 0.5
    z1 = np.random.randn(n_points) * 0.5

    # Cluster 2: Around (3, 3, 3)
    x2 = np.random.randn(n_points) * 0.5 + 3
    y2 = np.random.randn(n_points) * 0.5 + 3
    z2 = np.random.randn(n_points) * 0.5 + 3

    # Cluster 3: Around (-2, 3, -2)
    x3 = np.random.randn(n_points) * 0.5 - 2
    y3 = np.random.randn(n_points) * 0.5 + 3
    z3 = np.random.randn(n_points) * 0.5 - 2

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
        x=x1, y=y1, z=z1,
        mode='markers',
        name='Cluster A',
        marker=dict(
            size=5,
            color='#3b82f6',
            symbol='circle',
            line=dict(color='white', width=0.5)
        ),
        hovertemplate='<b>Cluster A</b><br>x: %{x:.2f}<br>y: %{y:.2f}<br>z: %{z:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter3d(
        x=x2, y=y2, z=z2,
        mode='markers',
        name='Cluster B',
        marker=dict(
            size=5,
            color='#10b981',
            symbol='diamond',
            line=dict(color='white', width=0.5)
        ),
        hovertemplate='<b>Cluster B</b><br>x: %{x:.2f}<br>y: %{y:.2f}<br>z: %{z:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter3d(
        x=x3, y=y3, z=z3,
        mode='markers',
        name='Cluster C',
        marker=dict(
            size=5,
            color='#f59e0b',
            symbol='square',
            line=dict(color='white', width=0.5)
        ),
        hovertemplate='<b>Cluster C</b><br>x: %{x:.2f}<br>y: %{y:.2f}<br>z: %{z:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='3D Scatter Plot: Data Clusters in 3D Space',
        scene=dict(
            xaxis_title='Feature X',
            yaxis_title='Feature Y',
            zaxis_title='Feature Z',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
            bgcolor='#f8fafc'
        ),
        width=1000,
        height=600,
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=True,
        legend=dict(x=0.7, y=0.9)
    )

    return fig.to_html(include_plotlyjs=False, div_id='scatter-plot', full_html=False)


def create_torus_and_helix():
    """Create an interactive 3D visualization with a torus and a helix."""
    # Create a torus
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, 2 * np.pi, 100)
    U, V = np.meshgrid(u, v)

    R = 3
    r = 1

    X_torus = (R + r * np.cos(V)) * np.cos(U)
    Y_torus = (R + r * np.cos(V)) * np.sin(U)
    Z_torus = r * np.sin(V)

    # Create a parametric helix
    t = np.linspace(0, 4 * np.pi, 500)
    helix_r = R + r + 0.5
    X_helix = helix_r * np.cos(t)
    Y_helix = helix_r * np.sin(t)
    Z_helix = t * 0.5 - 3

    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=X_torus,
        y=Y_torus,
        z=Z_torus,
        colorscale='Plasma',
        showscale=False,
        opacity=0.8,
        name='Torus',
        hovertemplate='Torus<br>x: %{x:.2f}<br>y: %{y:.2f}<br>z: %{z:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter3d(
        x=X_helix,
        y=Y_helix,
        z=Z_helix,
        mode='lines',
        line=dict(color='cyan', width=6),
        name='Helix',
        hovertemplate='Helix<br>x: %{x:.2f}<br>y: %{y:.2f}<br>z: %{z:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title='Parametric 3D Shapes: Torus & Helix',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(eye=dict(x=1.8, y=1.8, z=1.2)),
            aspectmode='data',
            bgcolor='#f8fafc'
        ),
        width=1000,
        height=600,
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=True
    )

    return fig.to_html(include_plotlyjs=False, div_id='parametric-plot', full_html=False)


def generate_html_page():
    """Generate the complete HTML page with all plots embedded."""
    print("Generating 3D plots...")

    # Generate all plots
    surface_html = create_3d_surface()
    scatter_html = create_3d_scatter()
    parametric_html = create_torus_and_helix()

    print("Building HTML page...")

    # Build the complete HTML page using FastHTML
    page = Html(
        Head(
            Title("Interactive 3D Visualizations - Prerendered"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Style("""
                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }

                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }

                .header {
                    text-align: center;
                    color: white;
                    margin-bottom: 50px;
                }

                .header h1 {
                    font-size: 48px;
                    margin: 0 0 15px 0;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }

                .header p {
                    font-size: 20px;
                    opacity: 0.9;
                    margin: 0;
                }

                .plot-section {
                    background: white;
                    border-radius: 16px;
                    padding: 30px;
                    margin-bottom: 40px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }

                .plot-section h2 {
                    color: #2563eb;
                    margin-top: 0;
                    margin-bottom: 20px;
                    font-size: 28px;
                }

                .plot-description {
                    color: #64748b;
                    line-height: 1.6;
                    margin-bottom: 25px;
                    font-size: 16px;
                }

                .plot-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 600px;
                }

                .instructions {
                    background: #f8fafc;
                    border-left: 4px solid #7c3aed;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }

                .instructions h3 {
                    color: #7c3aed;
                    margin-top: 0;
                    margin-bottom: 15px;
                }

                .instructions ul {
                    margin: 0;
                    padding-left: 20px;
                    color: #475569;
                }

                .instructions li {
                    margin: 8px 0;
                }

                .footer {
                    text-align: center;
                    color: white;
                    padding: 30px 20px;
                    margin-top: 40px;
                    background: rgba(0,0,0,0.2);
                    border-radius: 16px;
                }

                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-top: 20px;
                }

                .stat-card {
                    padding: 15px;
                    border-radius: 8px;
                    background: #f0fdf4;
                    border: 1px solid #86efac;
                }

                .stat-card h4 {
                    margin: 0 0 8px 0;
                    color: #059669;
                }

                .stat-card p {
                    margin: 0;
                    color: #475569;
                    font-size: 14px;
                }

                .math-equation {
                    background: #eff6ff;
                    padding: 15px;
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                    color: #1e40af;
                    margin: 10px 0;
                    text-align: center;
                }
            """)
        ),
        Body(
            Div(
                # Header
                Div(
                    H1("Interactive 3D Visualizations"),
                    P("Prerendered plots with full interactivity - Powered by Plotly + FastHTML"),
                    cls="header"
                ),

                # Instructions
                Div(
                    H3("How to interact with these plots:"),
                    Ul(
                        Li("Click and drag to rotate any 3D plot"),
                        Li("Scroll or pinch to zoom in and out"),
                        Li("Hover over data points and surfaces to see coordinates"),
                        Li("Use the toolbar (top-right of each plot) to pan, reset view, or save as image"),
                        Li("Toggle legend items to show/hide specific data series")
                    ),
                    cls="instructions"
                ),

                # Plot 1: Surface
                Div(
                    H2("1. Sombrero Function Surface"),
                    P(
                        "The Sombrero (Mexican Hat) function is a classic example in signal processing "
                        "and wavelet analysis. It's defined as the sinc function in radial coordinates, "
                        "creating a characteristic shape with a central peak and rippling waves.",
                        cls="plot-description"
                    ),
                    Div(
                        cls="math-equation",
                        children=[NotStr("z = sin(√(x² + y²)) / √(x² + y²)")]
                    ),
                    Div(
                        NotStr(surface_html),
                        cls="plot-container"
                    ),
                    cls="plot-section"
                ),

                # Plot 2: Scatter
                Div(
                    H2("2. 3D Scatter Plot - Data Clusters"),
                    P(
                        "This visualization shows three distinct clusters of points in 3D space. "
                        "Each cluster contains 100 randomly generated points with different centers "
                        "and colors. This type of plot is commonly used in data science for visualizing "
                        "clustering algorithms, classification results, or multi-dimensional data exploration.",
                        cls="plot-description"
                    ),
                    Div(
                        Div(
                            H4("Cluster A (Blue)"),
                            P("100 points centered at (0, 0, 0)"),
                            cls="stat-card",
                            style="background: #eff6ff; border-color: #93c5fd;"
                        ),
                        Div(
                            H4("Cluster B (Green)"),
                            P("100 points centered at (3, 3, 3)"),
                            cls="stat-card",
                            style="background: #f0fdf4; border-color: #86efac;"
                        ),
                        Div(
                            H4("Cluster C (Orange)"),
                            P("100 points centered at (-2, 3, -2)"),
                            cls="stat-card",
                            style="background: #fffbeb; border-color: #fcd34d;"
                        ),
                        cls="stats-grid"
                    ),
                    Div(
                        NotStr(scatter_html),
                        cls="plot-container"
                    ),
                    cls="plot-section"
                ),

                # Plot 3: Parametric
                Div(
                    H2("3. Parametric Surfaces - Torus & Helix"),
                    P(
                        "Parametric surfaces are defined by equations that express coordinates as functions of parameters. "
                        "The torus (doughnut shape) is created by rotating a circle around an axis in 3D space. "
                        "The cyan helix wraps around the torus, demonstrating how multiple 3D objects can be "
                        "composed in a single interactive visualization.",
                        cls="plot-description"
                    ),
                    Div(
                        Div(
                            Strong("Torus equations:"),
                            Br(),
                            NotStr("x = (R + r·cos(v))·cos(u)"),
                            Br(),
                            NotStr("y = (R + r·cos(v))·sin(u)"),
                            Br(),
                            NotStr("z = r·sin(v)"),
                            cls="math-equation",
                            style="display: inline-block; width: 48%; margin-right: 2%;"
                        ),
                        Div(
                            Strong("Helix equations:"),
                            Br(),
                            NotStr("x = R·cos(t)"),
                            Br(),
                            NotStr("y = R·sin(t)"),
                            Br(),
                            NotStr("z = t·0.5"),
                            cls="math-equation",
                            style="display: inline-block; width: 48%;"
                        )
                    ),
                    Div(
                        NotStr(parametric_html),
                        cls="plot-container"
                    ),
                    cls="plot-section"
                ),

                # Footer
                Div(
                    P("These visualizations are prerendered and embedded as static HTML with full interactivity."),
                    P("No server required - all plots work offline!"),
                    cls="footer"
                ),

                cls="container"
            )
        )
    )

    return to_xml(page)


def main():
    """Main function to generate and save the HTML file."""
    output_file = Path(__file__).parent / "interactive_plots.html"

    print("=" * 60)
    print("3D Interactive Plots - Prerendering")
    print("=" * 60)

    html_content = generate_html_page()

    # Write to file
    print(f"\nWriting HTML to: {output_file}")
    output_file.write_text(html_content)

    print(f"\n✓ Successfully generated: {output_file}")
    print(f"✓ File size: {output_file.stat().st_size / 1024:.1f} KB")
    print("\nTo view the plots:")
    print(f"  Open {output_file.name} in your web browser")
    print("\nAll plots are fully interactive and work offline!")
    print("=" * 60)


if __name__ == '__main__':
    main()
