"""
Experiment 4: Using Python Dictionaries for Styles
This demonstrates converting Python dictionaries to CSS style strings.
"""

from fasthtml.common import *

app, rt = fast_app()

def dict_to_style(style_dict):
    """
    Convert a Python dictionary to a CSS style string.
    Example: {'color': 'red', 'font-size': '16px'} -> "color: red; font-size: 16px;"
    """
    return "; ".join(f"{key}: {value}" for key, value in style_dict.items()) + ";"

# Define reusable style dictionaries
BUTTON_STYLES = {
    'primary': {
        'background-color': '#3b82f6',
        'color': 'white',
        'padding': '12px 24px',
        'border': 'none',
        'border-radius': '8px',
        'font-weight': '600',
        'cursor': 'pointer',
        'transition': 'all 0.3s ease',
    },
    'secondary': {
        'background-color': '#6b7280',
        'color': 'white',
        'padding': '12px 24px',
        'border': 'none',
        'border-radius': '8px',
        'font-weight': '600',
        'cursor': 'pointer',
    },
    'success': {
        'background-color': '#10b981',
        'color': 'white',
        'padding': '12px 24px',
        'border': 'none',
        'border-radius': '8px',
        'font-weight': '600',
        'cursor': 'pointer',
    },
    'danger': {
        'background-color': '#ef4444',
        'color': 'white',
        'padding': '12px 24px',
        'border': 'none',
        'border-radius': '8px',
        'font-weight': '600',
        'cursor': 'pointer',
    }
}

CARD_STYLE = {
    'background': 'white',
    'border': '1px solid #e5e7eb',
    'border-radius': '16px',
    'padding': '30px',
    'margin': '20px auto',
    'max-width': '700px',
    'box-shadow': '0 4px 6px rgba(0,0,0,0.1)',
}

HEADING_STYLES = {
    'h1': {
        'color': '#1f2937',
        'font-size': '36px',
        'font-weight': 'bold',
        'margin-bottom': '20px',
        'text-align': 'center',
    },
    'h2': {
        'color': '#3b82f6',
        'font-size': '28px',
        'font-weight': '600',
        'margin-top': '30px',
        'margin-bottom': '15px',
        'border-bottom': '2px solid #dbeafe',
        'padding-bottom': '10px',
    }
}

ALERT_STYLES = {
    'info': {
        'background-color': '#dbeafe',
        'border-left': '4px solid #3b82f6',
        'color': '#1e40af',
        'padding': '15px',
        'border-radius': '4px',
        'margin': '15px 0',
    },
    'success': {
        'background-color': '#d1fae5',
        'border-left': '4px solid #10b981',
        'color': '#065f46',
        'padding': '15px',
        'border-radius': '4px',
        'margin': '15px 0',
    },
    'warning': {
        'background-color': '#fef3c7',
        'border-left': '4px solid #f59e0b',
        'color': '#92400e',
        'padding': '15px',
        'border-radius': '4px',
        'margin': '15px 0',
    },
}

# Style composition - merge dictionaries
def merge_styles(*style_dicts):
    """Merge multiple style dictionaries"""
    result = {}
    for d in style_dicts:
        result.update(d)
    return result

@rt('/')
def get():
    # Custom modifications to base styles
    custom_card = merge_styles(CARD_STYLE, {
        'background': 'linear-gradient(to bottom, #ffffff, #f9fafb)',
    })

    return Titled("Style Dictionary Example",
        Div(
            H1("Python Dictionary Styles", style=dict_to_style(HEADING_STYLES['h1'])),
            P("This page uses Python dictionaries converted to CSS styles!",
              style=dict_to_style({'text-align': 'center', 'color': '#64748b', 'font-size': '18px'})),
            style=dict_to_style(custom_card)
        ),

        Div(
            H2("Reusable Button Styles", style=dict_to_style(HEADING_STYLES['h2'])),
            Div(
                Button("Primary Button", style=dict_to_style(BUTTON_STYLES['primary'])),
                Span(" ", style="display: inline-block; width: 10px;"),
                Button("Secondary Button", style=dict_to_style(BUTTON_STYLES['secondary'])),
                Span(" ", style="display: inline-block; width: 10px;"),
                Button("Success Button", style=dict_to_style(BUTTON_STYLES['success'])),
                Span(" ", style="display: inline-block; width: 10px;"),
                Button("Danger Button", style=dict_to_style(BUTTON_STYLES['danger'])),
                style=dict_to_style({'text-align': 'center', 'margin': '20px 0'})
            ),
            style=dict_to_style(CARD_STYLE)
        ),

        Div(
            H2("Alert Components", style=dict_to_style(HEADING_STYLES['h2'])),
            Div("ℹ️ This is an informational alert using dictionary styles!",
                style=dict_to_style(ALERT_STYLES['info'])),
            Div("✅ Success! Your operation completed successfully.",
                style=dict_to_style(ALERT_STYLES['success'])),
            Div("⚠️ Warning: Please review the information carefully.",
                style=dict_to_style(ALERT_STYLES['warning'])),
            style=dict_to_style(CARD_STYLE)
        ),

        Div(
            H2("Style Composition", style=dict_to_style(HEADING_STYLES['h2'])),
            P("You can merge multiple style dictionaries to create complex styles!",
              style=dict_to_style(merge_styles(
                  {'color': '#1f2937', 'font-size': '16px'},
                  {'background-color': '#f3f4f6', 'padding': '15px', 'border-radius': '8px'}
              ))),
            Div(
                "This box uses merged styles from multiple dictionaries",
                style=dict_to_style(merge_styles(
                    {'padding': '20px', 'border-radius': '12px'},
                    {'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'},
                    {'color': 'white', 'text-align': 'center', 'font-weight': '600', 'font-size': '18px'}
                ))
            ),
            style=dict_to_style(CARD_STYLE)
        )
    )

if __name__ == '__main__':
    serve()
