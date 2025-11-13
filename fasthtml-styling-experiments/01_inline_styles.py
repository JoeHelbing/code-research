"""
Experiment 1: Inline Styling with Python
This demonstrates how to apply styles directly to FastHTML components using Python.
"""

from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get():
    return Titled("Inline Styling Example",
        # Heading with inline style
        H1("Welcome to FastHTML",
           style="color: #2563eb; font-size: 48px; text-align: center; margin-bottom: 20px;"),

        # Paragraph with inline style
        P("This paragraph demonstrates inline styling using Python strings.",
          style="color: #475569; font-size: 18px; line-height: 1.6; padding: 15px; background-color: #f1f5f9; border-radius: 8px;"),

        # Div with multiple styled children
        Div(
            H2("Styled Card", style="color: #dc2626; margin-bottom: 10px;"),
            P("This is a card with custom styling applied through Python.",
              style="color: #334155; margin-bottom: 15px;"),
            Button("Click Me",
                   style="background-color: #10b981; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px;"),
            style="border: 2px solid #e2e8f0; padding: 20px; border-radius: 12px; max-width: 600px; margin: 20px auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);"
        ),

        # List with styled items
        Div(
            H3("Feature List", style="color: #7c3aed; margin-bottom: 15px;"),
            Ul(
                Li("No external CSS files needed", style="color: #059669; padding: 8px; font-size: 16px;"),
                Li("All styling in Python", style="color: #059669; padding: 8px; font-size: 16px;"),
                Li("Easy to maintain and update", style="color: #059669; padding: 8px; font-size: 16px;"),
                style="list-style-type: square; padding-left: 20px;"
            ),
            style="margin: 30px auto; max-width: 600px; padding: 20px; background-color: #faf5ff; border-radius: 8px;"
        ),

        # Footer with gradient background
        Div(
            P("Styled entirely with Python! 🎨", style="color: white; font-size: 14px; margin: 0;"),
            style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin-top: 40px; border-radius: 8px;"
        )
    )

if __name__ == '__main__':
    serve()
