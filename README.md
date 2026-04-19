# The Path (AI-Pi)

Edge AI-powered turn-based combat game running on Raspberry Pi hardware.

![The Path (AI-Pi)](docs/images/cover.png)

📚 [View Documentation](https://primatif.github.io/thepath-ai_pi/)

## Project Origins

This project represents the evolution of turn-based battle mechanics through several research spikes:

1. [Simulat33](https://github.com/MaterDev/Python_Jupyter_Experiments/tree/main/projects/06_simulat33) - The initial prototype built in Python using Jupyter notebooks, which established core concepts for:
   * Character class systems with unique abilities
   * Turn-based combat mechanics
   * Interactive battle UI using ipywidgets
   * Status effects and buff systems

2. [huMon-gen](https://github.com/MaterDev/Python_Jupyter_Experiments/tree/main/projects/08_huMon-gen) - A specialized tool for character stat generation and balancing:
   * Algorithmic generation of character stats using ancestral tree patterns
   * Interactive visualization of stat distributions across character generations
   * Comparative analysis tools for balancing character attributes
   * The base character stats used in this project were generated using this system

3. [golang_turnbased_game_spike](https://github.com/MaterDev/golang_turnbased_game_spike) - A Go-based implementation that refined these concepts and added:
   * RESTful API architecture
   * Modern React TypeScript frontend
   * Improved battle state management
   * Enhanced cooldown mechanics

The current project builds upon these previous implementations, incorporating:
* Core battle mechanics from Simulat33
* Balanced character stats generated through huMon-gen
* Modern architecture and UI patterns from the Go implementation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Format and lint code
make format
make lint

# Build documentation
make docs-build

# Start documentation server
make docs
```

## Development

The project uses several tools to maintain code quality:

* `ruff`: Fast Python linter with auto-fix
* `black`: Code formatting
* `isort`: Import sorting

These are configured in `pyproject.toml` with sensible defaults that prioritize productivity.

## Documentation

Documentation is built using MkDocs with Material theme. Key features:

* Automatic formatting
* Link validation
* Image optimization
* Development tracking
* Code style checks

### Documentation Requirements

* Python 3.9+
* MkDocs Material theme
* Python-Markdown extensions
* Pillow for image processing

### Available Commands

```bash
# Documentation
make docs              # Start documentation server
make docs-build        # Build documentation site
make docs-deploy       # Deploy to GitHub Pages
make docs-validate     # Validate documentation

# Code Quality
make format           # Format code with black and isort
make lint            # Lint code with ruff
make check-style     # Check code style without fixing

# Image Management
make check-images    # Check image optimization
make process-images  # Optimize images for web

# Development Logs
make update-logs     # Update development logs
make check-logs      # Validate log format
```

Run `make help` to see all available commands.

## Project Structure

```
.
├── docs/               # Documentation
│   ├── meta/          # Development logs and social updates
│   ├── overview/      # Project overview and objectives
│   ├── scripts/       # Documentation automation
│   ├── technical/     # Technical specifications
│   └── world_building/ # Game world and mechanics
├── requirements.txt    # Python dependencies
└── mkdocs.yml         # Documentation configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make format` and `make lint`
5. Submit a pull request

## License

This project is licensed under Mater Development Dynamic Version License (MDDVL) found in the [LICENSE](LICENSE) file.
