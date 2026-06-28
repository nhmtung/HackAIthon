# Code Style and Python Development Guidelines

This document outlines the coding standards, typing requirements, and formatting rules for the Python codebase in the HackAIthon project.

## 1. Python Version & Run Environments
* **Python Runtime**: Python >= 3.10 is required.
* **Typing Mandatory**:
  * Function signatures MUST utilize Python type hints.
  * Example:
    ```python
    def process_data(inputs: list[dict]) -> pd.DataFrame:
    ```

## 2. UTF-8 Explicit Encoding
* **UTF-8 Requirement**: In all file opens, string encodes, and writes, `encoding="utf-8"` must be passed explicitly.
* **No system-default fallback**: This prevents encoding differences between development machines (Windows/macOS) and execution environments (Docker/Linux).

## 3. Modular Architecture & Clean Abstractions
* **Keep functions single-purpose**: Each function should ideally do one thing (e.g., only data validation, only prompt formatting, or only post-processing).
* **Minimal dependencies**: Avoid introducing complex dependencies unless absolutely necessary.
