"""
Comprehensive comparison of 3D plotting packages
Generates a single HTML file comparing all different plotting libraries.
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Common data for all plots
x = np.linspace(-5, 5, 80)
y = np.linspace(-5, 5, 80)
X, Y = np.meshgrid(x, y)
R = np.sqrt(X**2 + Y**2) + 1e-10
Z = np.sin(R) / R * 5


def generate_plotly_plot():
    """Generate Plotly 3D surface plot."""
    try:
        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Viridis',
            showscale=True
        )])

        fig.update_layout(
            title='Plotly: Interactive 3D Surface',
            scene=dict(
                xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
            ),
            width=700, height=600,
            margin=dict(l=0, r=0, b=0, t=40)
        )

        return fig.to_html(include_plotlyjs='cdn', div_id='plotly-plot', full_html=False)
    except Exception as e:
        return f'<div style="color: red;">Plotly Error: {str(e)}</div>'


def generate_bokeh_plot():
    """Generate Bokeh heatmap (3D limitation)."""
    try:
        from bokeh.plotting import figure
        from bokeh.embed import components
        from bokeh.models import LinearColorMapper, ColumnDataSource
        from bokeh.palettes import Viridis256

        x_flat = X.flatten()
        y_flat = Y.flatten()
        z_flat = Z.flatten()

        source = ColumnDataSource(data=dict(x=x_flat, y=y_flat, z=z_flat))
        color_mapper = LinearColorMapper(palette=Viridis256, low=z_flat.min(), high=z_flat.max())

        p = figure(
            width=700, height=600,
            title="Bokeh: Top-down Heatmap (Limited 3D)",
            x_axis_label='X', y_axis_label='Y',
            tools="pan,wheel_zoom,box_zoom,reset",
            tooltips=[("X", "@x{0.00}"), ("Y", "@y{0.00}"), ("Z", "@z{0.00}")]
        )

        p.circle('x', 'y', size=2, source=source,
                color={'field': 'z', 'transform': color_mapper}, alpha=0.8)

        script, div = components(p)
        return f'<script src="https://cdn.bokeh.org/bokeh/release/bokeh-3.3.0.min.js"></script>\n{script}\n{div}'
    except Exception as e:
        return f'<div style="color: red;">Bokeh Error: {str(e)}</div>'


def generate_pyvista_plot():
    """Generate PyVista 3D surface plot."""
    try:
        import pyvista as pv

        grid = pv.StructuredGrid(X, Y, Z)
        grid['Z Values'] = Z.ravel(order='F')

        plotter = pv.Plotter(notebook=False, off_screen=True)
        plotter.add_mesh(grid, scalars='Z Values', cmap='viridis', show_edges=False)
        plotter.view_isometric()

        html_str = plotter.export_html(None, backend='pythreejs')
        plotter.close()

        return html_str
    except Exception as e:
        return f'<div style="color: red;">PyVista Error: {str(e)}<br>Note: PyVista requires display/graphics support</div>'


def generate_matplotlib_plot():
    """Generate Matplotlib with mpld3 (2D only)."""
    try:
        import matplotlib.pyplot as plt
        import mpld3
        from mpl_toolkits.mplot3d import Axes3D
        from io import BytesIO
        import base64

        # Create contour plot for mpld3
        fig, ax = plt.subplots(figsize=(7, 6))
        contour = ax.contourf(X, Y, Z, levels=20, cmap='viridis')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Matplotlib + mpld3: 2D Contour Only')
        plt.colorbar(contour, ax=ax, label='Z value')
        plt.tight_layout()

        html_str = mpld3.fig_to_html(fig)
        plt.close()

        # Add static 3D image
        fig3d = plt.figure(figsize=(7, 6))
        ax3d = fig3d.add_subplot(111, projection='3d')
        surf = ax3d.plot_surface(X, Y, Z, cmap='viridis', alpha=0.9)
        ax3d.set_xlabel('X')
        ax3d.set_ylabel('Y')
        ax3d.set_zlabel('Z')
        ax3d.set_title('Static 3D (NOT interactive)')
        ax3d.view_init(elev=25, azim=135)

        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=120, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close()

        static_3d = f'<div style="margin-top: 20px;"><img src="data:image/png;base64,{img_str}" style="max-width: 100%; height: auto;" /></div>'

        return html_str + static_3d
    except Exception as e:
        return f'<div style="color: red;">Matplotlib Error: {str(e)}</div>'


def generate_comparison_html():
    """Generate comprehensive comparison HTML."""

    print("Generating plots...")
    print("- Plotly...")
    plotly_html = generate_plotly_plot()
    print("- Bokeh...")
    bokeh_html = generate_bokeh_plot()
    print("- PyVista...")
    pyvista_html = generate_pyvista_plot()
    print("- Matplotlib...")
    matplotlib_html = generate_matplotlib_plot()

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Plotting Libraries Comparison</title>
    <link rel="stylesheet" href="https://cdn.bokeh.org/bokeh/release/bokeh-3.3.0.min.css">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            text-align: center;
            color: white;
            padding: 40px 20px;
        }}
        h1 {{
            font-size: 3em;
            margin: 0 0 10px 0;
        }}
        .subtitle {{
            font-size: 1.3em;
            opacity: 0.9;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(750px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }}
        .plot-card {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .plot-card h2 {{
            margin-top: 0;
            color: #2563eb;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 10px;
        }}
        .plot-container {{
            margin: 20px 0;
        }}
        .pros-cons {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }}
        .pros, .cons {{
            padding: 15px;
            border-radius: 8px;
        }}
        .pros {{
            background: #d1fae5;
            border-left: 4px solid #059669;
        }}
        .cons {{
            background: #fee2e2;
            border-left: 4px solid #dc2626;
        }}
        .pros h3, .cons h3 {{
            margin-top: 0;
            font-size: 1em;
        }}
        .pros h3 {{
            color: #059669;
        }}
        .cons h3 {{
            color: #dc2626;
        }}
        ul {{
            margin: 5px 0;
            padding-left: 20px;
        }}
        li {{
            margin: 5px 0;
        }}
        .rating {{
            display: inline-block;
            background: #fbbf24;
            color: #78350f;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}
        footer {{
            text-align: center;
            color: white;
            padding: 40px 20px;
            margin-top: 40px;
        }}
        .summary {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin: 30px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .summary h2 {{
            color: #7c3aed;
            margin-top: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{
            background: #f3f4f6;
            font-weight: bold;
            color: #1f2937;
        }}
        .check {{
            color: #059669;
            font-weight: bold;
        }}
        .cross {{
            color: #dc2626;
            font-weight: bold;
        }}
        .partial {{
            color: #f59e0b;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎨 3D Plotting Libraries Comparison</h1>
            <p class="subtitle">A comprehensive comparison of Python libraries for interactive 3D visualization</p>
        </header>

        <div class="summary">
            <h2>📊 Quick Comparison Table</h2>
            <table>
                <thead>
                    <tr>
                        <th>Library</th>
                        <th>True 3D Interactive</th>
                        <th>Web Integration</th>
                        <th>Ease of Use</th>
                        <th>Performance</th>
                        <th>Best For</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Plotly</strong></td>
                        <td><span class="check">✓ Excellent</span></td>
                        <td><span class="check">✓ Excellent</span></td>
                        <td><span class="check">✓ Very Easy</span></td>
                        <td><span class="check">✓ Good</span></td>
                        <td>General purpose, dashboards</td>
                    </tr>
                    <tr>
                        <td><strong>PyVista</strong></td>
                        <td><span class="check">✓ Excellent</span></td>
                        <td><span class="partial">~ Good</span></td>
                        <td><span class="partial">~ Moderate</span></td>
                        <td><span class="check">✓ Excellent</span></td>
                        <td>Scientific visualization, CAD</td>
                    </tr>
                    <tr>
                        <td><strong>Bokeh</strong></td>
                        <td><span class="cross">✗ Limited (2D)</span></td>
                        <td><span class="check">✓ Excellent</span></td>
                        <td><span class="check">✓ Easy</span></td>
                        <td><span class="check">✓ Good</span></td>
                        <td>2D interactive plots</td>
                    </tr>
                    <tr>
                        <td><strong>Matplotlib + mpld3</strong></td>
                        <td><span class="cross">✗ No (2D only)</span></td>
                        <td><span class="partial">~ Fair</span></td>
                        <td><span class="check">✓ Very Easy</span></td>
                        <td><span class="partial">~ Fair</span></td>
                        <td>Static 3D, 2D interactive</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="comparison-grid">
            <!-- Plotly -->
            <div class="plot-card">
                <h2>1. Plotly <span class="rating">⭐ 9.5/10</span></h2>
                <div class="plot-container">
                    {plotly_html}
                </div>
                <div class="pros-cons">
                    <div class="pros">
                        <h3>✅ Pros</h3>
                        <ul>
                            <li>Excellent 3D interactivity</li>
                            <li>Easy web integration</li>
                            <li>Clean, modern interface</li>
                            <li>Great documentation</li>
                            <li>Works out of the box</li>
                        </ul>
                    </div>
                    <div class="cons">
                        <h3>❌ Cons</h3>
                        <ul>
                            <li>Limited mesh editing</li>
                            <li>Less suitable for complex scientific viz</li>
                            <li>Requires CDN or large JS file</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- PyVista -->
            <div class="plot-card">
                <h2>2. PyVista <span class="rating">⭐ 8.5/10</span></h2>
                <div class="plot-container">
                    {pyvista_html}
                </div>
                <div class="pros-cons">
                    <div class="pros">
                        <h3>✅ Pros</h3>
                        <ul>
                            <li>Professional scientific viz</li>
                            <li>Powerful mesh handling</li>
                            <li>VTK backend (industry standard)</li>
                            <li>Excellent for engineering</li>
                        </ul>
                    </div>
                    <div class="cons">
                        <h3>❌ Cons</h3>
                        <ul>
                            <li>Requires system dependencies</li>
                            <li>Steeper learning curve</li>
                            <li>May need display server</li>
                            <li>Larger file sizes</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Bokeh -->
            <div class="plot-card">
                <h2>3. Bokeh <span class="rating">⭐ 6/10</span></h2>
                <div class="plot-container">
                    {bokeh_html}
                </div>
                <div class="pros-cons">
                    <div class="pros">
                        <h3>✅ Pros</h3>
                        <ul>
                            <li>Excellent for 2D plots</li>
                            <li>Good web integration</li>
                            <li>Interactive tooltips</li>
                            <li>Dashboard-friendly</li>
                        </ul>
                    </div>
                    <div class="cons">
                        <h3>❌ Cons</h3>
                        <ul>
                            <li>NO native 3D support</li>
                            <li>Limited to 2D projections</li>
                            <li>Not suitable for true 3D viz</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Matplotlib + mpld3 -->
            <div class="plot-card">
                <h2>4. Matplotlib + mpld3 <span class="rating">⭐ 5/10</span></h2>
                <div class="plot-container">
                    {matplotlib_html}
                </div>
                <div class="pros-cons">
                    <div class="pros">
                        <h3>✅ Pros</h3>
                        <ul>
                            <li>Familiar matplotlib syntax</li>
                            <li>Good for 2D plots</li>
                            <li>Easy to learn</li>
                            <li>Can create static 3D images</li>
                        </ul>
                    </div>
                    <div class="cons">
                        <h3>❌ Cons</h3>
                        <ul>
                            <li>mpld3 does NOT support 3D</li>
                            <li>3D plots are static only</li>
                            <li>Poor web interactivity</li>
                            <li>Not recommended for 3D</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <div class="summary">
            <h2>🎯 Recommendations</h2>
            <h3 style="color: #2563eb;">For Web-Based 3D Visualization → Use Plotly</h3>
            <p>Plotly offers the best balance of ease-of-use, interactivity, and web integration. It's perfect for dashboards, data exploration, and general-purpose 3D visualization.</p>

            <h3 style="color: #059669;">For Scientific/Engineering Applications → Use PyVista</h3>
            <p>PyVista provides professional-grade 3D visualization with powerful mesh manipulation. Ideal for CAD, simulations, and scientific computing where you need advanced 3D capabilities.</p>

            <h3 style="color: #f59e0b;">For 2D Interactive Plots → Use Bokeh</h3>
            <p>Bokeh excels at 2D interactive visualizations and is perfect for dashboards and data applications, but avoid it for 3D work.</p>

            <h3 style="color: #dc2626;">Avoid for 3D Web Visualization → Matplotlib + mpld3</h3>
            <p>While matplotlib is great for static plots and publications, mpld3 simply doesn't support 3D interactivity. Use it for 2D only.</p>
        </div>

        <footer>
            <p style="font-size: 1.2em;">Built with FastHTML | Generated: {np.datetime64('now')}</p>
            <p>Experiment: 3d-interactive-plots</p>
        </footer>
    </div>
</body>
</html>"""

    return html_template


if __name__ == '__main__':
    print("Generating comprehensive comparison HTML...")
    html_content = generate_comparison_html()

    output_file = 'comparison_all_packages.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ Successfully generated: {output_file}")
    print(f"📂 Open the file in your browser to view the comparison!")
