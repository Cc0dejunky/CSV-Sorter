import os
import re


def refactor_imports_in_project(project_root):
    """
    Walks through the project, finds Python files, and updates deprecated
    import paths.
    """
    # Define the refactoring rules: (old_import_pattern, new_import_string)
    # These patterns will find imports of 'config' from the 'optimizer' module.
    refactoring_rules = [
        (
            re.compile(r"from optimizer\.config import"),
            "from core.config import",
        ),
        (
            re.compile(r"import optimizer\.config"),
            "import core.config",
        ),
        # Add other rules here if needed, for example:
        # (
        #     re.compile(r"from data\.processed\.webhook_handler_example import"),
        #     "from integration.webhook_handler_example import",
        # ),
    ]

    print(f"Starting import refactoring in: {project_root}\n")
    files_changed = 0

    # We only want to modify files within the 'src' directory
    source_directory = os.path.join(project_root, "src")

    for root, _, files in os.walk(source_directory):
        for filename in files:
            if filename.endswith(".py"):
                filepath = os.path.join(root, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    original_content = f.read()

                modified_content = original_content
                for old_pattern, new_string in refactoring_rules:
                    modified_content = old_pattern.sub(new_string, modified_content)

                if modified_content != original_content:
                    print(f"Updating imports in: {filepath}")
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(modified_content)
                    files_changed += 1

    print(f"\nRefactoring complete. {files_changed} file(s) were updated.")


if __name__ == "__main__":
    # Assumes the script is in the project root directory
    project_root_path = os.path.dirname(os.path.abspath(__file__))
    refactor_imports_in_project(project_root_path)