"""
Experiment 2: Global Styles with Python
This demonstrates using the Style component to define global CSS rules in Python.
"""

from fasthtml.common import *

# Define global styles as a Python string
global_css = Style("""
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: linear-gradient(to bottom, #ece9e6, #ffffff);
        padding: 20px;
        margin: 0;
    }

    .card {
        background: white;
        border-radius: 16px;
        padding: 30px;
        margin: 20px auto;
        max-width: 700px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }

    .primary-heading {
        color: #1e40af;
        font-size: 42px;
        text-align: center;
        margin-bottom: 10px;
        font-weight: bold;
    }

    .secondary-heading {
        color: #7c3aed;
        font-size: 28px;
        margin-top: 20px;
        margin-bottom: 15px;
        border-bottom: 3px solid #c4b5fd;
        padding-bottom: 10px;
    }

    .highlight {
        background: linear-gradient(120deg, #fef3c7 0%, #fde68a 100%);
        padding: 5px 10px;
        border-radius: 4px;
        font-weight: 600;
    }

    .button-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s;
    }

    .button-primary:hover {
        transform: scale(1.05);
    }

    .info-box {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
        padding: 15px;
        margin: 20px 0;
        border-radius: 4px;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }

    .feature-item {
        background: linear-gradient(135deg, #fecaca 0%, #fca5a5 100%);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        color: #991b1b;
    }
""")

# Create app with global styles in headers
app, rt = fast_app(hdrs=[global_css])

@rt('/')
def get():
    return Titled("Global Styles Example",
        Div(
            H1("Global Styling in Python", cls="primary-heading"),
            P("This entire page is styled using global CSS defined in Python!",
              style="text-align: center; color: #64748b; font-size: 18px;"),
            cls="card"
        ),

        Div(
            H2("Why Global Styles?", cls="secondary-heading"),
            P("Global styles are ", Span("perfect", cls="highlight"),
              " for consistent theming across your entire application."),

            Div(
                P("💡 Define your styles once in Python and reuse them everywhere with CSS classes.",
                  style="margin: 0; font-size: 15px; color: #1e40af;"),
                cls="info-box"
            ),

            H2("Feature Showcase", cls="secondary-heading"),
            Div(
                Div("Responsive Grid", cls="feature-item"),
                Div("Gradient Backgrounds", cls="feature-item"),
                Div("Hover Effects", cls="feature-item"),
                Div("Custom Classes", cls="feature-item"),
                cls="feature-grid"
            ),

            Div(
                Button("Try This Button", cls="button-primary"),
                style="text-align: center; margin-top: 30px;"
            ),
            cls="card"
        )
    )

if __name__ == '__main__':
    serve()
