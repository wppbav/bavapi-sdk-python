"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

SOURCE_PATH = Path("./bavapi")
REFERENCE_PATH = Path("reference")

nav = mkdocs_gen_files.nav.Nav()

for path in sorted(SOURCE_PATH.rglob("*.py")):
    module_path = path.relative_to(SOURCE_PATH).with_suffix("")
    doc_path = path.relative_to(SOURCE_PATH).with_suffix(".md")
    full_doc_path = REFERENCE_PATH / doc_path

    parts = module_path.parts
    end_part = parts[-1]
    if (
        end_part in {"__main__", "typing"}
        or (end_part != "__init__" and end_part.startswith("_"))
        or any(part.startswith("_") for part in parts[:-1])
    ):
        continue

    if parts[-1] == "__init__":
        # Create an index page for the package
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")

    try:
        nav[parts] = doc_path.as_posix()
    except ValueError as exc:
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        # Write reference for `mkdocstrings`
        fd.write(f"::: {'.'.join(parts)}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

nav_lines = list(nav.build_literate_nav())
nav_lines.insert(0, nav_lines.pop())  # move `sync` to the top

with mkdocs_gen_files.open(REFERENCE_PATH / "SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav_lines)
