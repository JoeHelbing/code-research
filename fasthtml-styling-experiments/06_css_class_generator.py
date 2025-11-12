"""
Experiment 6: Python-Based CSS Class Generator
This demonstrates generating CSS classes dynamically from Python code.
"""

from fasthtml.common import *

# ============================================================================
# CSS CLASS GENERATOR
# ============================================================================

class CSSGenerator:
    """Generate CSS classes dynamically from Python"""

    def __init__(self):
        self.classes = {}

    def add_class(self, name, **styles):
        """Add a CSS class with the given styles"""
        self.classes[name] = styles
        return self

    def add_utility_classes(self):
        """Generate utility classes similar to Tailwind"""
        # Text colors
        colors = {
            'blue': '#3b82f6', 'green': '#10b981', 'red': '#ef4444',
            'yellow': '#f59e0b', 'purple': '#8b5cf6', 'gray': '#6b7280'
        }
        for name, color in colors.items():
            self.add_class(f'text-{name}', color=color)

        # Background colors
        for name, color in colors.items():
            self.add_class(f'bg-{name}', **{'background-color': color})

        # Spacing utilities
        for i in [0, 1, 2, 3, 4, 5]:
            size = i * 4
            self.add_class(f'p-{i}', padding=f'{size}px')
            self.add_class(f'm-{i}', margin=f'{size}px')

        # Border radius
        self.add_class('rounded', **{'border-radius': '4px'})
        self.add_class('rounded-lg', **{'border-radius': '8px'})
        self.add_class('rounded-xl', **{'border-radius': '12px'})
        self.add_class('rounded-full', **{'border-radius': '9999px'})

        # Font weights
        self.add_class('font-normal', **{'font-weight': '400'})
        self.add_class('font-medium', **{'font-weight': '500'})
        self.add_class('font-semibold', **{'font-weight': '600'})
        self.add_class('font-bold', **{'font-weight': '700'})

        # Text alignment
        self.add_class('text-left', **{'text-align': 'left'})
        self.add_class('text-center', **{'text-align': 'center'})
        self.add_class('text-right', **{'text-align': 'right'})

        return self

    def generate_responsive_classes(self):
        """Generate responsive utility classes"""
        # Flex utilities
        self.add_class('flex', display='flex')
        self.add_class('flex-col', display='flex', **{'flex-direction': 'column'})
        self.add_class('flex-row', display='flex', **{'flex-direction': 'row'})
        self.add_class('items-center', **{'align-items': 'center'})
        self.add_class('justify-center', **{'justify-content': 'center'})
        self.add_class('justify-between', **{'justify-content': 'space-between'})

        # Grid utilities
        self.add_class('grid', display='grid')
        self.add_class('grid-cols-2', display='grid', **{'grid-template-columns': 'repeat(2, 1fr)'})
        self.add_class('grid-cols-3', display='grid', **{'grid-template-columns': 'repeat(3, 1fr)'})
        self.add_class('gap-4', gap='16px')

        return self

    def generate_component_classes(self):
        """Generate common component classes"""
        self.add_class('btn', **{
            'padding': '10px 20px',
            'border': 'none',
            'border-radius': '6px',
            'font-weight': '600',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease',
        })

        self.add_class('btn-primary', **{
            'background-color': '#3b82f6',
            'color': 'white',
        })

        self.add_class('btn-secondary', **{
            'background-color': '#6b7280',
            'color': 'white',
        })

        self.add_class('card', **{
            'background': 'white',
            'border': '1px solid #e5e7eb',
            'border-radius': '12px',
            'padding': '20px',
            'box-shadow': '0 1px 3px rgba(0,0,0,0.1)',
        })

        self.add_class('badge', **{
            'display': 'inline-block',
            'padding': '4px 12px',
            'border-radius': '12px',
            'font-size': '12px',
            'font-weight': '600',
        })

        return self

    def to_css(self):
        """Convert all classes to CSS string"""
        css_lines = []
        for class_name, styles in self.classes.items():
            style_str = "; ".join(f"{k}: {v}" for k, v in styles.items())
            css_lines.append(f".{class_name} {{ {style_str}; }}")
        return "\n".join(css_lines)

    def get_style_tag(self):
        """Return a Style component with all generated CSS"""
        return Style(self.to_css())

# ============================================================================
# GENERATE CSS
# ============================================================================

css_gen = CSSGenerator()
css_gen.add_utility_classes()
css_gen.generate_responsive_classes()
css_gen.generate_component_classes()

# Add custom classes
css_gen.add_class('hero', **{
    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'color': 'white',
    'padding': '60px 20px',
    'text-align': 'center',
    'border-radius': '16px',
    'margin-bottom': '30px',
})

css_gen.add_class('feature-box', **{
    'padding': '30px',
    'border': '2px solid #e5e7eb',
    'border-radius': '12px',
    'text-align': 'center',
    'transition': 'all 0.3s ease',
})

css_gen.add_class('feature-box:hover', **{
    'border-color': '#3b82f6',
    'box-shadow': '0 10px 20px rgba(59, 130, 246, 0.2)',
    'transform': 'translateY(-5px)',
})

# ============================================================================
# APP
# ============================================================================

app, rt = fast_app(hdrs=[css_gen.get_style_tag()])

@rt('/')
def get():
    return Titled("CSS Class Generator",
        Div(
            Div(
                H1("Python CSS Class Generator", cls="font-bold"),
                P("Generate utility classes like Tailwind, entirely in Python!", cls="font-medium"),
                cls="hero"
            ),

            Div(
                H2("Utility Classes", cls="text-blue font-semibold text-center m-3"),
                Div(
                    Div(
                        Span("Text Blue", cls="text-blue font-bold"),
                        P("Using utility classes", cls="text-gray"),
                        cls="card"
                    ),
                    Div(
                        Span("Background Green", cls="bg-green rounded-lg p-3 text-center"),
                        P("With padding and rounded corners", cls="text-gray m-2"),
                        cls="card"
                    ),
                    Div(
                        Span("Purple Badge", cls="badge bg-purple"),
                        Span("Red Badge", cls="badge bg-red m-1"),
                        P("Badge components", cls="text-gray m-2"),
                        cls="card"
                    ),
                    cls="grid grid-cols-3 gap-4"
                ),
                style="max-width: 1000px; margin: 0 auto; padding: 20px;"
            ),

            Div(
                H2("Button Components", cls="text-purple font-semibold text-center m-3"),
                Div(
                    Button("Primary", cls="btn btn-primary m-2"),
                    Button("Secondary", cls="btn btn-secondary m-2"),
                    cls="text-center"
                ),
                style="max-width: 1000px; margin: 0 auto; padding: 20px;"
            ),

            Div(
                H2("Flexbox Layout", cls="text-green font-semibold text-center m-3"),
                Div(
                    Div("Item 1", cls="bg-blue rounded p-3"),
                    Div("Item 2", cls="bg-purple rounded p-3"),
                    Div("Item 3", cls="bg-green rounded p-3"),
                    cls="flex justify-between gap-4"
                ),
                style="max-width: 1000px; margin: 0 auto; padding: 20px;"
            ),

            Div(
                H2("Feature Boxes (with Hover)", cls="text-red font-semibold text-center m-3"),
                Div(
                    Div(
                        H3("🚀 Fast", cls="font-bold text-blue"),
                        P("Lightning-fast performance", cls="text-gray"),
                        cls="feature-box"
                    ),
                    Div(
                        H3("🎨 Beautiful", cls="font-bold text-purple"),
                        P("Gorgeous designs", cls="text-gray"),
                        cls="feature-box"
                    ),
                    Div(
                        H3("⚡ Simple", cls="font-bold text-green"),
                        P("Easy to use", cls="text-gray"),
                        cls="feature-box"
                    ),
                    cls="grid grid-cols-3 gap-4"
                ),
                style="max-width: 1000px; margin: 0 auto; padding: 20px;"
            ),

            Div(
                H2("Generated CSS Info", cls="text-gray font-semibold text-center m-3"),
                Div(
                    P(f"Total CSS classes generated: {len(css_gen.classes)}", cls="font-medium text-center"),
                    P("All classes are defined in Python and converted to CSS automatically!", cls="text-center text-gray"),
                    cls="card bg-yellow rounded-xl p-4 m-3"
                ),
                style="max-width: 1000px; margin: 0 auto; padding: 20px;"
            ),
        )
    )

if __name__ == '__main__':
    serve()
