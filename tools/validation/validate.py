"""Static checks for community contribution packages; no contribution execution."""

import argparse
import json
import re
from pathlib import Path, PureWindowsPath


CATEGORIES = ("workflows", "scripts", "connectors")
INPUT_TYPES = ("string", "integer", "number", "boolean")


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def nonempty_string(value):
    return isinstance(value, str) and bool(value.strip())


def validate_package(package, category=None):
    errors = []
    readme = package / "README.md"
    try:
        if not readme.read_text(encoding="utf-8").strip():
            errors.append("README.md must not be empty")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read README.md: {exc}")

    try:
        data = json.loads(
            (package / "manifest.json").read_text(encoding="utf-8"),
            object_pairs_hook=unique_keys,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        return errors + [f"cannot read manifest.json: {exc}"]
    if not isinstance(data, dict):
        return errors + ["manifest.json must contain an object"]

    for field in ("name", "displayName", "description", "category", "entryPoint"):
        if not nonempty_string(data.get(field)):
            errors.append(f"{field} must be a nonempty string")

    name = data.get("name")
    if nonempty_string(name):
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            errors.append("name must be lowercase and hyphen-separated")
        if category is not None and name != package.name:
            errors.append("name must match the contribution folder")
    if data.get("category") not in CATEGORIES:
        errors.append(f"category must be one of {', '.join(CATEGORIES)}")
    elif category is not None and data["category"] != category:
        errors.append("category must match the parent directory")

    entry = data.get("entryPoint")
    if nonempty_string(entry):
        try:
            path = Path(entry.replace("\\", "/"))
            target = (package / path).resolve()
            if (
                path.is_absolute()
                or PureWindowsPath(entry).drive
                or not target.is_relative_to(package.resolve())
            ):
                errors.append("entryPoint must stay inside the contribution folder")
            elif not target.is_file():
                errors.append("entryPoint must reference an existing file")
        except (OSError, ValueError) as exc:
            errors.append(f"invalid entryPoint: {exc}")

    inputs = data.get("inputs")
    if not isinstance(inputs, list):
        return errors + ["inputs must be an array"]
    names = set()
    for index, item in enumerate(inputs):
        prefix = f"inputs[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        input_name = item.get("name")
        if not nonempty_string(input_name):
            errors.append(f"{prefix}.name must be a nonempty string")
        elif input_name in names:
            errors.append(f"{prefix}.name must be unique")
        else:
            names.add(input_name)
        if not nonempty_string(item.get("description")):
            errors.append(f"{prefix}.description must be a nonempty string")
        if item.get("type") not in INPUT_TYPES:
            errors.append(f"{prefix}.type must be one of {', '.join(INPUT_TYPES)}")
        if not isinstance(item.get("required"), bool):
            errors.append(f"{prefix}.required must be a boolean")
    return errors


def validate_repository(root):
    errors = []
    packages = [(root / "templates" / "contribution", None)]
    for category in CATEGORIES:
        directory = root / category
        if not directory.is_dir():
            errors.append(f"{category}: category directory is missing")
            continue
        packages.extend(
            (item, category) for item in sorted(directory.iterdir()) if item.is_dir()
        )
    for package, category in packages:
        label = package.relative_to(root)
        if not package.resolve().is_relative_to(root.resolve()):
            errors.append(f"{label}: package must stay inside the repository")
            continue
        errors.extend(f"{label}: {error}" for error in validate_package(package, category))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    args = parser.parse_args()
    errors = validate_repository(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Contribution structure and metadata checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
