# Project Structure Analysis

This document provides an overview of the folder and file structure for the `CSV-Sorter` project.

## Root Directory (`CSV-Sorter/`)

The root directory contains the main project folders and top-level configuration files.

- **`.venv/`**: A directory containing the Python virtual environment for this project. (See details below).
- **`Docs/`**: A directory for project documentation. (See details below).
- **`.gitignore`**: A configuration file for the Git version control system. It specifies which files and directories should be ignored by Git. Currently, it is correctly configured to ignore `__pycache__/` directories, which prevents temporary Python files from being added to version control.
- **`core.md`**: A markdown file containing a detailed analysis of key files from the project's dependencies (like TensorFlow, SciPy, etc.). This file provides deep insight into the underlying libraries being used.

---

### `.venv/` Directory

This folder represents the project's **Python virtual environment**.

- **Purpose**: A virtual environment is a self-contained directory that houses a specific Python interpreter and all the libraries and dependencies required for a particular project. Using one is a critical best practice in modern Python development.
- **Benefits**:
  - **Isolation**: It keeps the dependencies for this project separate from other projects on your system, preventing version conflicts.
  - **Reproducibility**: It makes it easy to recreate the exact development environment on another machine by listing the installed packages in a `requirements.txt` file.
- **Contents**: This directory contains all the installed packages for your project, such as:
  - `tensorflow`
  - `scipy`
  - `sklearn`
  - `pip`
  - `setuptools`
  - `torch`
  - And many others.

You should almost always add the `.venv/` directory to your `.gitignore` file to avoid committing thousands of library files to your repository.

---

### `Docs/` Directory

This folder is intended to hold all project-related documentation.

- **Purpose**: It serves as a central place for manuals, analysis documents, and any other explanatory materials that help developers (including your future self) understand the project.
- **Contents**: This is where files like this `project_structure.md` and the `core.md` analysis should be stored to keep the project organized.
