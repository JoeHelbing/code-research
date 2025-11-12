"""
Experiment 3: Dynamic Styling with Python Logic
This demonstrates how to generate styles dynamically using Python code.
"""

from fasthtml.common import *

app, rt = fast_app()

def create_color_style(color, intensity=500):
    """Generate a style string based on color and intensity"""
    colors = {
        'blue': f'#3b82f6' if intensity == 500 else f'#60a5fa',
        'green': f'#10b981' if intensity == 500 else f'#34d399',
        'red': f'#ef4444' if intensity == 500 else f'#f87171',
        'purple': f'#8b5cf6' if intensity == 500 else f'#a78bfa',
    }
    return f"background-color: {colors.get(color, '#6b7280')}; color: white; padding: 15px; border-radius: 8px; margin: 10px 0; text-align: center; font-weight: 600;"

def create_card_style(shadow_level='medium'):
    """Generate card styling based on shadow level"""
    shadows = {
        'light': '0 1px 3px rgba(0,0,0,0.1)',
        'medium': '0 4px 6px rgba(0,0,0,0.1)',
        'heavy': '0 10px 25px rgba(0,0,0,0.2)',
    }
    return f"border: 1px solid #e5e7eb; padding: 20px; border-radius: 12px; margin: 15px 0; box-shadow: {shadows.get(shadow_level, shadows['medium'])};"

def generate_gradient(start_color, end_color):
    """Generate a gradient background style"""
    return f"background: linear-gradient(135deg, {start_color} 0%, {end_color} 100%); color: white; padding: 20px; border-radius: 8px;"

@rt('/')
def get():
    # Dynamic data that affects styling
    items = [
        {'name': 'Python', 'color': 'blue', 'priority': 'high'},
        {'name': 'FastHTML', 'color': 'green', 'priority': 'high'},
        {'name': 'CSS', 'color': 'purple', 'priority': 'medium'},
        {'name': 'JavaScript', 'color': 'red', 'priority': 'low'},
    ]

    # Generate dynamic styling based on priority
    priority_styles = {
        'high': "border-left: 5px solid #10b981; background-color: #f0fdf4;",
        'medium': "border-left: 5px solid #f59e0b; background-color: #fffbeb;",
        'low': "border-left: 5px solid #ef4444; background-color: #fef2f2;",
    }

    return Titled("Dynamic Styling Example",
        # Header with generated gradient
        Div(
            H1("Dynamic Python Styling", style="margin: 0; font-size: 36px;"),
            P("Styles generated on-the-fly with Python logic!", style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;"),
            style=generate_gradient('#6366f1', '#8b5cf6')
        ),

        # Cards with different shadow levels
        Div(
            H2("Shadow Levels", style="color: #1f2937; margin-bottom: 20px;"),
            Div("Light Shadow", style=create_card_style('light')),
            Div("Medium Shadow", style=create_card_style('medium')),
            Div("Heavy Shadow", style=create_card_style('heavy')),
            style="max-width: 700px; margin: 30px auto;"
        ),

        # Dynamic color boxes
        Div(
            H2("Dynamic Color Styling", style="color: #1f2937; margin-bottom: 20px;"),
            Div("Blue Variant", style=create_color_style('blue', 500)),
            Div("Green Variant", style=create_color_style('green', 500)),
            Div("Red Variant", style=create_color_style('red', 500)),
            Div("Purple Variant", style=create_color_style('purple', 500)),
            style="max-width: 700px; margin: 30px auto;"
        ),

        # List items with priority-based styling
        Div(
            H2("Priority-Based Styling", style="color: #1f2937; margin-bottom: 20px;"),
            *[
                Div(
                    Div(
                        Strong(item['name'], style="font-size: 18px; color: #1f2937;"),
                        Span(f" - {item['priority']} priority",
                             style=f"color: {'#059669' if item['priority'] == 'high' else '#d97706' if item['priority'] == 'medium' else '#dc2626'}; font-size: 14px; margin-left: 10px;"),
                    ),
                    style=priority_styles[item['priority']] + " padding: 15px; margin: 10px 0; border-radius: 6px;"
                )
                for item in items
            ],
            style="max-width: 700px; margin: 30px auto;"
        ),

        # Grid with programmatically generated items
        Div(
            H2("Generated Grid", style="color: #1f2937; margin-bottom: 20px;"),
            Div(
                *[
                    Div(
                        f"Item {i+1}",
                        style=f"background: linear-gradient(135deg, hsl({i*40}, 70%, 60%), hsl({i*40 + 20}, 70%, 50%)); color: white; padding: 30px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 18px;"
                    )
                    for i in range(6)
                ],
                style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;"
            ),
            style="max-width: 700px; margin: 30px auto;"
        )
    )

if __name__ == '__main__':
    serve()
