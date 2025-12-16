#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Synchronize project version/name across code, pyproject, package dir, and .env."""

from __future__ import annotations

import io
import re
import shutil
import tokenize
from pathlib import Path

try:  # Python 3.11+
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for older Python
    import tomli as tomllib  # type: ignore


PYPROJECT_PATH = Path("pyproject.toml")
SRC_DIR = Path("src")
OUTER_ENV = Path(".env")


def load_pyproject() -> tuple[str, str, str]:
    data = tomllib.loads(PYPROJECT_PATH.read_text())
    project = data.get("project", {})
    poetry = data.get("tool", {}).get("poetry", {})
    packages = poetry.get("packages") or []

    project_name = project.get("name")
    project_version = project.get("version")
    include_name = None
    for pkg in packages:
        if isinstance(pkg, dict) and "include" in pkg:
            include_name = pkg["include"]
            break
    include_name = include_name or project_name

    if not project_name or not project_version:
        raise ValueError("pyproject.toml must define [project].name and [project].version")

    return project_name, project_version, include_name


def update_pyproject_names(project_name: str) -> None:
    content = PYPROJECT_PATH.read_text()
    content = re.sub(r'(?m)^(name\s*=\s*)"(.*?)"', rf'\1"{project_name}"', content)
    content = re.sub(r'include\s*=\s*"(.*?)"', f'include = "{project_name}"', content)
    PYPROJECT_PATH.write_text(content)


def update_versions_in_code(project_version: str) -> None:
    pattern = re.compile(r'(^\s*__version__\s*=\s*)([\'"])(.*?)(\2)', re.MULTILINE)
    for path in Path(".").rglob("*.py"):
        text = path.read_text()
        new_text, count = pattern.subn(lambda m: f"{m.group(1)}{m.group(2)}{project_version}{m.group(2)}", text)
        if count:
            path.write_text(new_text)


def ensure_package_dir(project_name: str, current_include: str) -> Path:
    target = SRC_DIR / project_name
    if target.exists():
        return target

    source = SRC_DIR / current_include
    if source.exists() and source != target:
        shutil.move(str(source), str(target))
    return target


def update_env_file(pkg_dir: Path, project_name: str, project_version: str) -> None:
    env_path = pkg_dir / ".env"
    if not env_path.exists():
        return

    service_name = project_name if project_name.endswith("-service") else f"{project_name}-service"
    app_module = project_name
    gunicorn_app = f"{project_name}.wsgi:app"
    worker_target = f"{project_name}.app"

    lines = env_path.read_text().splitlines()
    new_lines = []
    seen_name = False
    seen_version = False
    seen_app_module = False
    seen_gunicorn_app = False
    seen_worker_target = False

    for line in lines:
        if line.startswith("SERVICE_NAME="):
            new_lines.append(f"SERVICE_NAME={service_name}")
            seen_name = True
        elif line.startswith("SERVICE_VERSION="):
            new_lines.append(f"SERVICE_VERSION={project_version}")
            seen_version = True
        elif line.startswith("APP_MODULE="):
            new_lines.append(f"APP_MODULE={app_module}")
            seen_app_module = True
        elif line.startswith("GUNICORN_APP="):
            new_lines.append(f"GUNICORN_APP={gunicorn_app}")
            seen_gunicorn_app = True
        elif line.startswith("WORKER_TARGET="):
            new_lines.append(f"WORKER_TARGET={worker_target}")
            seen_worker_target = True
        else:
            new_lines.append(line)

    if not seen_name:
        new_lines.append(f"SERVICE_NAME={service_name}")
    if not seen_version:
        new_lines.append(f"SERVICE_VERSION={project_version}")
    if not seen_app_module:
        new_lines.append(f"APP_MODULE={app_module}")
    if not seen_gunicorn_app:
        new_lines.append(f"GUNICORN_APP={gunicorn_app}")
    if not seen_worker_target:
        new_lines.append(f"WORKER_TARGET={worker_target}")

    env_path.write_text("\n".join(new_lines) + "\n")


def update_outer_env_pythonpath(project_name: str) -> None:
    if not OUTER_ENV.exists():
        return

    target = f'PYTHONPATH="src/{project_name}"'
    lines = OUTER_ENV.read_text().splitlines()
    new_lines = []
    seen = False
    for line in lines:
        if line.startswith("PYTHONPATH="):
            new_lines.append(target)
            seen = True
        else:
            new_lines.append(line)
    if not seen:
        new_lines.append(target)
    OUTER_ENV.write_text("\n".join(new_lines) + "\n")


def rewrite_imports(text: str, old_name: str, new_name: str) -> str:
    buffer = io.StringIO(text)
    tokens = list(tokenize.generate_tokens(buffer.readline))
    new_tokens: list[tokenize.TokenInfo] = []
    state = "default"
    skip_alias = False

    for tok in tokens:
        tok_type, tok_str, start, end, line = tok

        if state == "from_module":
            if tok_type == tokenize.NAME and tok_str == "import":
                state = "default"
                new_tokens.append(tok)
                continue
            if tok_type == tokenize.NAME and tok_str == old_name:
                tok = tokenize.TokenInfo(tok_type, new_name, start, end, line)
            new_tokens.append(tok)
            continue

        if state == "import_module":
            if tok_type == tokenize.NEWLINE:
                state = "default"
                skip_alias = False
                new_tokens.append(tok)
                continue
            if tok_type == tokenize.OP and tok_str == ";":
                state = "default"
                skip_alias = False
                new_tokens.append(tok)
                continue
            if tok_type == tokenize.OP and tok_str == ",":
                skip_alias = False
                new_tokens.append(tok)
                continue
            if tok_type == tokenize.NAME and tok_str == "as":
                skip_alias = True
                new_tokens.append(tok)
                continue
            if tok_type == tokenize.NAME and skip_alias:
                skip_alias = False
                new_tokens.append(tok)
                continue
            if tok_type == tokenize.NAME and tok_str == old_name:
                tok = tokenize.TokenInfo(tok_type, new_name, start, end, line)
            new_tokens.append(tok)
            continue

        if tok_type == tokenize.NAME and tok_str == "from":
            state = "from_module"
            new_tokens.append(tok)
            continue

        if tok_type == tokenize.NAME and tok_str == "import":
            state = "import_module"
            skip_alias = False
            new_tokens.append(tok)
            continue

        new_tokens.append(tok)

    return tokenize.untokenize(new_tokens)


def update_imports(project_name: str, include_name: str) -> None:
    if project_name == include_name:
        return

    targets = [SRC_DIR, Path("tests")]
    for target in targets:
        if not target.exists():
            continue
        for path in target.rglob("*.py"):
            text = path.read_text()
            new_text = rewrite_imports(text, include_name, project_name)
            if new_text != text:
                path.write_text(new_text)


def main() -> None:
    project_name, project_version, include_name = load_pyproject()
    update_pyproject_names(project_name)
    update_versions_in_code(project_version)
    pkg_dir = ensure_package_dir(project_name, include_name)
    update_imports(project_name, include_name)
    update_env_file(pkg_dir, project_name, project_version)
    update_outer_env_pythonpath(project_name)


if __name__ == "__main__":
    main()
