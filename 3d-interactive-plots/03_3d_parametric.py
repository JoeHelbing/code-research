"""
Experiment: Interactive 3D Parametric Surface with FastHTML
This demonstrates a 3D parametric torus and helix visualization.
"""

from fasthtml.common import *
import plotly.graph_objects as go
import numpy as np

app, rt = fast_app()


def create_torus_and_helix():
    """Create an interactive 3D visualization with a torus and a helix."""
    # Create a torus
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, 2 * np.pi, 100)
    U, V = np.meshgrid(u, v)

    # Torus parameters (R = major radius, r = minor radius)
    R = 3
    r = 1

    # Parametric equations for a torus
    X_torus = (R + r * np.cos(V)) * np.cos(U)
    Y_torus = (R + r * np.cos(V)) * np.sin(U)
    Z_torus = r * np.sin(V)

    # Create a parametric helix that wraps around the torus
    t = np.linspace(0, 4 * np.pi, 500)
    helix_r = R + r + 0.5  # Slightly larger than torus
    X_helix = helix_r * np.cos(t)
    Y_helix = helix_r * np.sin(t)
    Z_helix = t * 0.5 - 3  # Vertical component

    # Create the figure
    fig = go.Figure()

    # Add the torus surface
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

    # Add the helix
    fig.add_trace(go.Scatter3d(
        x=X_helix,
        y=Y_helix,
        z=Z_helix,
        mode='lines',
        line=dict(
            color='cyan',
            width=6
        ),
        name='Helix',
        hovertemplate='Helix<br>x: %{x:.2f}<br>y: %{y:.2f}<br>z: %{z:.2f}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        title='Parametric 3D Shapes: Torus & Helix',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(
                eye=dict(x=1.8, y=1.8, z=1.2)
            ),
            aspectmode='data',
            bgcolor='#0f172a'
        ),
        width=900,
        height=700,
        margin=dict(l=0, r=0, b=0, t=40),
        paper_bgcolor='#1e293b',
        font=dict(color='white'),
        showlegend=True
    )

    return fig.to_html(include_plotlyjs='cdn', div_id='parametric-plot', full_html=False)


@rt('/')
def get():
    plot_html = create_torus_and_helix()

    return Html(
        Head(
            Title("3D Parametric Visualization"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Style("""
                body {
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
                    color: white;
                    min-height: 100vh;
                }
            """)
        ),
        Body(
            # Header
            Div(
                H1("Parametric 3D Surfaces",
                   style="color: #60a5fa; text-align: center; margin-bottom: 10px; font-size: 42px;"),
                P("Exploring mathematical beauty: Torus & Helix",
                  style="text-align: center; color: #94a3b8; font-size: 20px; margin-bottom: 30px;"),
                style="padding: 40px 20px 20px 20px;"
            ),

            # Mathematical equations
            Div(
                H3("Parametric Equations", style="color: #a78bfa; margin-bottom: 20px;"),
                Div(
                    Div(
                        H4("Torus", style="color: #c084fc; margin-bottom: 10px;"),
                        P("x = (R + r·cos(v))·cos(u)", style="font-family: monospace; color: #e2e8f0; margin: 5px 0;"),
                        P("y = (R + r·cos(v))·sin(u)", style="font-family: monospace; color: #e2e8f0; margin: 5px 0;"),
                        P("z = r·sin(v)", style="font-family: monospace; color: #e2e8f0; margin: 5px 0;"),
                        P("where R=3 (major radius), r=1 (minor radius)", style="color: #94a3b8; margin-top: 10px; font-size: 14px;"),
                        style="padding: 20px; background-color: #1e293b; border-radius: 8px; border: 1px solid #334155;"
                    ),
                    Div(
                        H4("Helix", style="color: #22d3ee; margin-bottom: 10px;"),
                        P("x = R·cos(t)", style="font-family: monospace; color: #e2e8f0; margin: 5px 0;"),
                        P("y = R·sin(t)", style="font-family: monospace; color: #e2e8f0; margin: 5px 0;"),
                        P("z = t·0.5", style="font-family: monospace; color: #e2e8f0; margin: 5px 0;"),
                        P("where t ∈ [0, 4π]", style="color: #94a3b8; margin-top: 10px; font-size: 14px;"),
                        style="padding: 20px; background-color: #1e293b; border-radius: 8px; border: 1px solid #334155;"
                    ),
                    style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;"
                ),
                style="max-width: 900px; margin: 0 auto 30px auto; padding: 20px; background-color: #0f172a; border-radius: 12px; border: 2px solid #475569;"
            ),

            # The 3D plot
            Div(
                NotStr(plot_html),
                style="display: flex; justify-content: center; margin: 20px auto; max-width: 950px;"
            ),

            # Info section
            Div(
                H3("About Parametric Surfaces", style="color: #60a5fa; margin-bottom: 15px;"),
                P("Parametric surfaces are defined by equations that express coordinates as functions of parameters. "
                  "Unlike explicit functions (z = f(x,y)), parametric forms allow us to represent complex shapes like "
                  "the torus (doughnut shape) and helix (spring shape).",
                  style="color: #cbd5e1; line-height: 1.8; margin-bottom: 15px;"),
                P("The torus is generated by rotating a circle around an axis in 3D space. The helix wraps around "
                  "the torus, demonstrating how multiple 3D objects can be composed in a single interactive visualization.",
                  style="color: #cbd5e1; line-height: 1.8;"),
                style="max-width: 900px; margin: 30px auto; padding: 25px; background-color: #1e293b; border-radius: 12px; border-left: 4px solid #60a5fa;"
            ),

            # Footer
            Div(
                P("FastHTML + Plotly = Beautiful 3D Math",
                  style="color: #e2e8f0; margin: 0; font-size: 16px;"),
                style="text-align: center; padding: 30px; background-color: #0f172a; margin-top: 40px; border-top: 2px solid #334155;"
            )
        )
    )


if __name__ == '__main__':
    serve()
