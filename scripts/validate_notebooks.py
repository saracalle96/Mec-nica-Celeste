import argparse
import json
import subprocess
import sys
from pathlib import Path


REQUIRED_TOP_LEVEL_KEYS = ("cells", "metadata", "nbformat", "nbformat_minor")


def staged_notebooks() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip().endswith(".ipynb")]


def validate_notebook(path_str: str) -> list[str]:
    errors: list[str] = []
    path = Path(path_str)

    if not path.exists():
        return errors

    if path.stat().st_size == 0:
        return [f"Notebook vacio: {path_str}"]

    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"JSON invalido en {path_str}: linea {exc.lineno}, columna {exc.colno}"]

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in notebook:
            errors.append(f"Falta la clave '{key}' en {path_str}")

    cells = notebook.get("cells")
    if not isinstance(cells, list):
        errors.append(f"La clave 'cells' no es una lista en {path_str}")

    metadata = notebook.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"La clave 'metadata' no es un objeto en {path_str}")

    nbformat = notebook.get("nbformat")
    if not isinstance(nbformat, int):
        errors.append(f"La clave 'nbformat' no es un entero en {path_str}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida notebooks Jupyter antes de hacer commit.")
    parser.add_argument("paths", nargs="*", help="Rutas de notebooks a validar")
    parser.add_argument("--staged", action="store_true", help="Valida solo notebooks staged en git")
    args = parser.parse_args()

    paths = args.paths
    if args.staged:
        paths = staged_notebooks()

    if not paths:
        return 0

    errors: list[str] = []
    for path in paths:
        errors.extend(validate_notebook(path))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print("Se bloqueo el commit porque hay notebooks invalidos.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())