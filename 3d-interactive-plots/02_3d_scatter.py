"""
Experiment: Interactive 3D Scatter Plot with FastHTML
This demonstrates a 3D scatter plot showing multiple data clusters.
"""

from fasthtml.common import *
import plotly.graph_objects as go
import numpy as np

app, rt = fast_app()


def create_3d_scatter():
    """Create an interactive 3D scatter plot with multiple clusters."""
    np.random.seed(42)

    # Generate three clusters of points in 3D space
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

    # Create the 3D scatter plot
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

    # Update layout
    fig.update_layout(
        title='3D Scatter Plot: Data Clusters',
        scene=dict(
            xaxis_title='Feature X',
            yaxis_title='Feature Y',
            zaxis_title='Feature Z',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            ),
            bgcolor='#f8fafc'
        ),
        width=900,
        height=700,
        margin=dict(l=0, r=0, b=0, t=40),
        showlegend=True,
        legend=dict(x=0.7, y=0.9)
    )

    return fig.to_html(include_plotlyjs='cdn', div_id='scatter-plot', full_html=False)


@rt('/')
def get():
    plot_html = create_3d_scatter()

    return Titled("3D Scatter Plot Visualization",
        # Header
        Div(
            H1("3D Scatter Plot Analysis",
               style="color: #2563eb; text-align: center; margin-bottom: 10px;"),
            P("Visualizing three distinct data clusters in 3D space",
              style="text-align: center; color: #64748b; font-size: 18px; margin-bottom: 30px;"),
            style="padding: 20px;"
        ),

        # The 3D plot
        Div(
            NotStr(plot_html),
            style="display: flex; justify-content: center; margin: 20px auto; max-width: 950px;"
        ),

        # Statistics panel
        Div(
            H3("Dataset Statistics", style="color: #7c3aed; margin-bottom: 15px;"),
            Div(
                Div(
                    H4("Cluster A", style="color: #3b82f6; margin-bottom: 8px;"),
                    P("100 points | Center: (0, 0, 0)", style="color: #475569;"),
                    style="padding: 15px; background-color: #eff6ff; border-radius: 8px; margin-bottom: 10px;"
                ),
                Div(
                    H4("Cluster B", style="color: #10b981; margin-bottom: 8px;"),
                    P("100 points | Center: (3, 3, 3)", style="color: #475569;"),
                    style="padding: 15px; background-color: #f0fdf4; border-radius: 8px; margin-bottom: 10px;"
                ),
                Div(
                    H4("Cluster C", style="color: #f59e0b; margin-bottom: 8px;"),
                    P("100 points | Center: (-2, 3, -2)", style="color: #475569;"),
                    style="padding: 15px; background-color: #fffbeb; border-radius: 8px;"
                ),
                style="display: grid; gap: 10px;"
            ),
            style="max-width: 900px; margin: 30px auto; padding: 20px; background-color: #faf5ff; border-radius: 8px;"
        ),

        # Footer
        Div(
            P("Interactive 3D visualizations powered by Plotly + FastHTML",
              style="color: white; margin: 0;"),
            style="text-align: center; padding: 20px; background: linear-gradient(135deg, #f59e0b 0%, #dc2626 100%); margin-top: 40px;"
        )
    )


if __name__ == '__main__':
    serve()
