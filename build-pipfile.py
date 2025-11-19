import ast
import sys
import textwrap
from pathlib import Path

try:
    stdlib_modules = sys.stdlib_module_names
except AttributeError:
    stdlib_modules = {
        "os",
        "sys",
        "re",
        "math",
        "json",
        "time",
        "itertools",
        "functools",
        "collections",
        "subprocess",
        "logging",
        "random",
        "datetime",
        "pathlib",
        "threading",
        "typing",
        "heapq",
        "shutil",
    }


def get_imported_modules(file_path):
    """Parse a Python file and return a set of top-level imported module names."""
    modules = set()
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".")[0])

    # Filter out standard library modules
    user_modules = {m for m in modules if m not in stdlib_modules}
    return user_modules


def generate_pipfile(modules, output_path="Pipfile"):
    """Create a Pipfile with the given modules."""
    lines = ["[packages]"]
    for module in sorted(modules):
        lines.append(f'{module} = "*"')

    pipfile_content = "\n".join(lines)
    header = """\
        [[source]]
        url = "https://pypi.org/simple"
        verify_ssl = true
        name = "pypi"\n
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(header))
        f.write(pipfile_content)

    print(f"Pipfile generated with {len(modules)} package(s): {modules}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Pipfile from Python imports."
    )
    parser.add_argument("file", type=str, help="Path to the Python file")
    parser.add_argument(
        "--output", type=str, default="Pipfile", help="Output Pipfile path"
    )
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: {file_path} does not exist")
        sys.exit(1)

    modules = get_imported_modules(file_path)
    generate_pipfile(modules, args.output)
