# code-research

Research experiments and explorations for various technologies.

## Organization

For each new experiment, create a new folder.

## Python Projects with Pixi

Always use [Pixi](https://pixi.sh) for package management and running code if the language is Python. Pixi automatically creates an isolated virtual environment (`.pixi/envs/default`) for each project.

### Setting up a new Python project

1. Create a new folder for your experiment
2. Create a `pixi.toml` file with your dependencies:
   ```toml
   [project]
   name = "your-project-name"
   version = "0.1.0"
   channels = ["conda-forge"]
   platforms = ["linux-64", "osx-64", "win-64", "osx-arm64"]

   [dependencies]
   python = ">=3.11"
   # Add your dependencies here
   ```
3. Run `pixi install` to create the environment
4. Run your code with `pixi run python your_script.py`

## Experiments

### FastHTML Styling Experiments

Located in `fasthtml-styling-experiments/`, this folder contains comprehensive research on Python-based styling approaches with FastHTML, including:
- Inline styles
- Global styles
- Dynamic styles
- Style dictionaries
- Component-based styling
- CSS class generators

Each experiment includes a screenshot showing the visual output. See the [README](fasthtml-styling-experiments/README.md) for details.
