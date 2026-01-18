# HSK

HSK application built with Python and Poetry.

## Installation

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Usage

```bash
# Run the application
poetry run python -m hsk
```

## Development

```bash
# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Add a new dependency
poetry add <package-name>

# Add a development dependency
poetry add --group dev <package-name>
```

## Project Structure

```
HSK/
├── hsk/              # Main application package
│   ├── __init__.py   # Package initialization and main entry point
│   └── __main__.py   # Module execution entry point
├── tests/            # Test files
│   └── test_hsk.py   # Basic tests
├── pyproject.toml    # Poetry configuration and dependencies
└── README.md         # This file
```

## License

TBD
