# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Run Commands
- Install deps: `pip install -e .`
- Run tests: `pytest`
- Run lint: `ruff check .`
- Run single test: `pytest path/to/test_file.py::test_function`
- Process data: `python databehandling/behandling_main.py input_file [--metadata path] [--output-dir path]`
- Run Streamlit app: `streamlit run Oversikt.py`

## Code Style Guidelines
- **Imports**: Group imports (standard lib, third-party, local) with standard lib first
- **Formatting**: Use clean indentation (4 spaces), descriptive variable names
- **Types**: Use type hints for function parameters and return values
- **Documentation**: Use docstrings for modules and functions
- **Error handling**: Use explicit error checks with conditional returns
- **Path handling**: Use `pathlib.Path` for file operations
- **Naming**: snake_case for variables/functions, CamelCase for classes
- **Comments**: Keep comments minimal but explain complex logic
- **Data processing**: Chain operations clearly, validate intermediate results