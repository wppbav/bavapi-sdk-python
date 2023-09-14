with open("./CONTRIBUTING.md", encoding="utf-8") as file:
    contributing = file.read()

mkdocs_header = """---
hide:
    - navigation
---
"""

with open("./docs/contributing.md", "w", encoding="utf-8") as file:
    file.write("\n".join((mkdocs_header, contributing)))
