# HSK Mock Test Application

An advanced testing engine for the HSK (Hanyu Shuiping Kaoshi) 3.0 standard, featuring a tiered difficulty system and standardized mock tests.

## Features

- **HSK 3.0 Standard Aligned**: Comprehensive coverage of levels 1 through 9.
- **Tiered Difficulty Engine (v17.0)**:
    - **Intra-Level Homogeneity**: Distractors are strictly selected from the same HSK level.
    - **Absolute Parallelism**: Options match in Part-of-Speech and character length.
    - **Adaptive Distraction Logic**:
        - *L1-3*: Semantic categories and visual discrimination.
        - *L4-6*: Near-synonyms and usage scenarios.
        - *L7-9*: Morphological sophistication (Doctorate standard).
- **Universal Dataset**: High-quality JSON and plain text datasets for mock tests.
- **Comprehensive Verification**: Automated scripts for auditing level coverage, duplicates, and linguistic accuracy.

## Getting Started

### Installation

Ensure you have [Poetry](https://python-poetry.org/) installed.

```bash
make install
```

### Usage

Use the provided scripts to generate datasets or run audits:

```bash
python scripts/generate_universal_hsk_dataset.py
python scripts/audit_levels.py
```

## Development

We maintain high SWE standards. Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Common Commands

- `make check`: Run all linting and tests.
- `make test`: Run unit tests.
- `make format`: Auto-format code with Ruff.

## Branching Strategy

- `main`: Stable production branch.
- `dev`: Development integration branch.
- `feature/*`: Working branches.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
