# FastHTML Styling Quick Start Guide

## Installation

```bash
# Clone or navigate to the project directory
cd fasthtml-styling-experiments

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Experiments

Each experiment file is a standalone application. Simply run:

```bash
# Example 1: Inline Styles
python 01_inline_styles.py

# Example 2: Global Styles
python 02_global_styles.py

# Example 3: Dynamic Styles
python 03_dynamic_styles.py

# Example 4: Style Dictionaries
python 04_style_dictionaries.py

# Example 5: Component-Based Styling
python 05_component_styling.py

# Example 6: CSS Class Generator
python 06_css_class_generator.py
```

The server will start on `http://localhost:5001` (or the next available port).

Press `Ctrl+C` to stop the server.

## What Each Example Demonstrates

| File | Key Concept | Difficulty |
|------|------------|------------|
| `01_inline_styles.py` | Direct inline styling with `style` parameter | Beginner |
| `02_global_styles.py` | Global CSS rules using `Style` component | Beginner |
| `03_dynamic_styles.py` | Dynamic style generation with Python functions | Intermediate |
| `04_style_dictionaries.py` | Using Python dicts for structured styles | Intermediate |
| `05_component_styling.py` | Building reusable styled components | Advanced |
| `06_css_class_generator.py` | Generating utility classes programmatically | Advanced |

## Quick Code Snippets

### Inline Styling
```python
from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get():
    return Div(
        H1("Hello", style="color: blue; font-size: 32px;"),
        P("World", style="color: gray;")
    )

serve()
```

### Global Styles
```python
from fasthtml.common import *

css = Style("""
    .heading { color: blue; font-size: 32px; }
    .text { color: gray; }
""")

app, rt = fast_app(hdrs=[css])

@rt('/')
def get():
    return Div(
        H1("Hello", cls="heading"),
        P("World", cls="text")
    )

serve()
```

### Dynamic Styles
```python
from fasthtml.common import *

def button_style(color='blue'):
    return f"background-color: {color}; color: white; padding: 10px 20px;"

app, rt = fast_app()

@rt('/')
def get():
    return Div(
        Button("Blue", style=button_style('blue')),
        Button("Green", style=button_style('green'))
    )

serve()
```

## Tips for Learning

1. **Start Simple**: Begin with `01_inline_styles.py` to understand the basics
2. **Read the Code**: Each file is heavily commented
3. **Experiment**: Modify the examples and see what happens
4. **Mix Approaches**: Try combining techniques from different examples
5. **Check the README**: Full documentation available in `README.md`

## Common Issues

### Port Already in Use

If you see an error about port 5001 being in use:

```python
# Change the port in the file
serve(port=5002)  # or any other available port
```

### Module Not Found

Make sure you've activated the virtual environment:

```bash
source venv/bin/activate  # On Linux/Mac
venv\Scripts\activate     # On Windows
```

### Import Errors

Reinstall dependencies:

```bash
pip install --force-reinstall -r requirements.txt
```

## Next Steps

After exploring the examples:

1. Read the comprehensive `README.md` for detailed explanations
2. Try building your own page combining techniques
3. Explore the [FastHTML documentation](https://www.fastht.ml/)
4. Build a real project using your preferred styling approach

## Questions or Issues?

- Check `README.md` for detailed documentation
- Visit [FastHTML documentation](https://www.fastht.ml/)
- Review the code comments in each example file

Happy coding! 🚀
