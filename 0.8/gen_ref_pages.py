"""Generate the code reference pages and navigation."""

from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.nav.Nav()

for path in sorted(Path("./bavapi").rglob("*.py")):
    if path.name == "__init__.py":
        pass
    module_path = path.relative_to("./bavapi").with_suffix("")
    doc_path = path.relative_to("./bavapi").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] in {"__main__", "typing"}:
        continue
    elif parts[-1].startswith("_"):
        continue

    try:
        nav[parts] = doc_path.as_posix()
    except ValueError as exc:
        continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        fd.write(f"::: {'.'.join(parts)}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
