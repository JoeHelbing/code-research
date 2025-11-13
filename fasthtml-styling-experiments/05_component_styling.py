"""
Experiment 5: Component-Based Styling System
This demonstrates creating reusable styled components with Python.
"""

from fasthtml.common import *

app, rt = fast_app()

# ============================================================================
# STYLED COMPONENT LIBRARY
# ============================================================================

class StyledComponents:
    """A library of reusable styled components"""

    @staticmethod
    def Card(title, *children, variant='default'):
        """Styled card component with variants"""
        variants = {
            'default': {
                'background': 'white',
                'border': '1px solid #e5e7eb',
            },
            'colored': {
                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'border': 'none',
                'color': 'white',
            },
            'elevated': {
                'background': 'white',
                'border': 'none',
                'box-shadow': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            }
        }

        base_style = {
            'padding': '25px',
            'border-radius': '16px',
            'margin': '20px 0',
        }

        card_style = {**base_style, **variants.get(variant, variants['default'])}
        style_str = "; ".join(f"{k}: {v}" for k, v in card_style.items()) + ";"

        title_color = 'white' if variant == 'colored' else '#1f2937'

        return Div(
            H3(title, style=f"color: {title_color}; font-size: 24px; font-weight: 700; margin-bottom: 15px;"),
            *children,
            style=style_str
        )

    @staticmethod
    def Button(text, variant='primary', size='medium', **kwargs):
        """Styled button component with variants and sizes"""
        variants = {
            'primary': {'bg': '#3b82f6', 'hover': '#2563eb'},
            'success': {'bg': '#10b981', 'hover': '#059669'},
            'danger': {'bg': '#ef4444', 'hover': '#dc2626'},
            'outline': {'bg': 'transparent', 'border': '2px solid #3b82f6', 'color': '#3b82f6'},
        }

        sizes = {
            'small': {'padding': '8px 16px', 'font-size': '14px'},
            'medium': {'padding': '12px 24px', 'font-size': '16px'},
            'large': {'padding': '16px 32px', 'font-size': '18px'},
        }

        var = variants.get(variant, variants['primary'])
        sz = sizes.get(size, sizes['medium'])

        style = {
            'background-color': var['bg'],
            'color': var.get('color', 'white'),
            'padding': sz['padding'],
            'font-size': sz['font-size'],
            'border': var.get('border', 'none'),
            'border-radius': '8px',
            'font-weight': '600',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease',
            'margin': '5px',
        }

        style_str = "; ".join(f"{k}: {v}" for k, v in style.items()) + ";"
        return Button(text, style=style_str, **kwargs)

    @staticmethod
    def Badge(text, color='blue'):
        """Small badge component"""
        colors = {
            'blue': {'bg': '#dbeafe', 'text': '#1e40af'},
            'green': {'bg': '#d1fae5', 'text': '#065f46'},
            'red': {'bg': '#fee2e2', 'text': '#991b1b'},
            'yellow': {'bg': '#fef3c7', 'text': '#92400e'},
            'purple': {'bg': '#ede9fe', 'text': '#5b21b6'},
        }

        c = colors.get(color, colors['blue'])
        style = f"background-color: {c['bg']}; color: {c['text']}; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block; margin: 0 5px;"
        return Span(text, style=style)

    @staticmethod
    def Alert(message, type='info', icon=None):
        """Alert component with different types"""
        types = {
            'info': {'bg': '#dbeafe', 'border': '#3b82f6', 'text': '#1e40af', 'icon': 'ℹ️'},
            'success': {'bg': '#d1fae5', 'border': '#10b981', 'text': '#065f46', 'icon': '✅'},
            'warning': {'bg': '#fef3c7', 'border': '#f59e0b', 'text': '#92400e', 'icon': '⚠️'},
            'error': {'bg': '#fee2e2', 'border': '#ef4444', 'text': '#991b1b', 'icon': '❌'},
        }

        t = types.get(type, types['info'])
        display_icon = icon or t['icon']

        style = f"background-color: {t['bg']}; border-left: 4px solid {t['border']}; color: {t['text']}; padding: 15px; border-radius: 4px; margin: 15px 0; display: flex; align-items: center; gap: 10px;"
        return Div(
            Span(display_icon, style="font-size: 20px;"),
            Span(message, style="flex: 1;"),
            style=style
        )

    @staticmethod
    def Grid(*items, columns=3, gap='20px'):
        """Responsive grid layout"""
        style = f"display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: {gap}; margin: 20px 0;"
        return Div(*items, style=style)

    @staticmethod
    def ProgressBar(percentage, color='blue', height='20px'):
        """Progress bar component"""
        colors = {
            'blue': '#3b82f6',
            'green': '#10b981',
            'red': '#ef4444',
            'purple': '#8b5cf6',
        }

        container_style = f"width: 100%; background-color: #e5e7eb; border-radius: 10px; overflow: hidden; height: {height};"
        bar_style = f"width: {percentage}%; background-color: {colors.get(color, colors['blue'])}; height: 100%; transition: width 0.3s ease; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: 600;"

        return Div(
            Div(f"{percentage}%" if percentage > 15 else "", style=bar_style),
            style=container_style
        )

# ============================================================================
# DEMO PAGE
# ============================================================================

@rt('/')
def get():
    return Titled("Component-Based Styling",
        Div(
            H1("Styled Components Library",
               style="color: #1f2937; font-size: 42px; text-align: center; margin-bottom: 10px;"),
            P("Reusable components with encapsulated styling",
              style="text-align: center; color: #64748b; font-size: 18px; margin-bottom: 30px;"),
            style="max-width: 900px; margin: 0 auto; padding: 20px;"
        ),

        Div(
            StyledComponents.Card(
                "Default Card",
                P("This is a default card with standard styling."),
                Div(
                    StyledComponents.Button("Click Me", variant='primary', size='medium'),
                    StyledComponents.Button("Learn More", variant='outline', size='medium'),
                ),
                variant='default'
            ),

            StyledComponents.Card(
                "Colored Card",
                P("This card has a beautiful gradient background!"),
                StyledComponents.Button("Get Started", variant='success', size='large'),
                variant='colored'
            ),

            StyledComponents.Card(
                "Elevated Card",
                P("This card has an elevated shadow effect for depth."),
                Div(
                    StyledComponents.Button("Small", variant='danger', size='small'),
                    StyledComponents.Button("Medium", variant='primary', size='medium'),
                    StyledComponents.Button("Large", variant='success', size='large'),
                ),
                variant='elevated'
            ),

            style="max-width: 900px; margin: 0 auto; padding: 20px;"
        ),

        Div(
            H2("Badges", style="color: #1f2937; font-size: 28px; margin-bottom: 15px;"),
            Div(
                StyledComponents.Badge("New", color='blue'),
                StyledComponents.Badge("Success", color='green'),
                StyledComponents.Badge("Error", color='red'),
                StyledComponents.Badge("Warning", color='yellow'),
                StyledComponents.Badge("Featured", color='purple'),
            ),
            style="max-width: 900px; margin: 30px auto; padding: 20px;"
        ),

        Div(
            H2("Alerts", style="color: #1f2937; font-size: 28px; margin-bottom: 15px;"),
            StyledComponents.Alert("This is an informational message.", type='info'),
            StyledComponents.Alert("Operation completed successfully!", type='success'),
            StyledComponents.Alert("Please review your input.", type='warning'),
            StyledComponents.Alert("An error occurred while processing.", type='error'),
            style="max-width: 900px; margin: 30px auto; padding: 20px;"
        ),

        Div(
            H2("Progress Bars", style="color: #1f2937; font-size: 28px; margin-bottom: 15px;"),
            P("Blue - 75%", style="margin-top: 20px; margin-bottom: 5px; color: #4b5563;"),
            StyledComponents.ProgressBar(75, color='blue'),
            P("Green - 100%", style="margin-top: 20px; margin-bottom: 5px; color: #4b5563;"),
            StyledComponents.ProgressBar(100, color='green'),
            P("Red - 45%", style="margin-top: 20px; margin-bottom: 5px; color: #4b5563;"),
            StyledComponents.ProgressBar(45, color='red'),
            P("Purple - 60%", style="margin-top: 20px; margin-bottom: 5px; color: #4b5563;"),
            StyledComponents.ProgressBar(60, color='purple'),
            style="max-width: 900px; margin: 30px auto; padding: 20px;"
        ),

        Div(
            H2("Grid Layout", style="color: #1f2937; font-size: 28px; margin-bottom: 15px;"),
            StyledComponents.Grid(
                Div("Grid Item 1", style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; text-align: center; font-weight: 600;"),
                Div("Grid Item 2", style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px; border-radius: 12px; text-align: center; font-weight: 600;"),
                Div("Grid Item 3", style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 40px; border-radius: 12px; text-align: center; font-weight: 600;"),
                Div("Grid Item 4", style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); color: white; padding: 40px; border-radius: 12px; text-align: center; font-weight: 600;"),
                Div("Grid Item 5", style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 40px; border-radius: 12px; text-align: center; font-weight: 600;"),
                Div("Grid Item 6", style="background: linear-gradient(135deg, #30cfd0 0%, #330867 100%); color: white; padding: 40px; border-radius: 12px; text-align: center; font-weight: 600;"),
                columns=3,
                gap='15px'
            ),
            style="max-width: 900px; margin: 30px auto; padding: 20px;"
        )
    )

if __name__ == '__main__':
    serve()
