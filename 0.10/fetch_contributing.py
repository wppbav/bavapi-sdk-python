import re

# Replace absolute documentation URLs with relative URIs
# <rel> capture group finds relative path
# <section> capture group finds section index (including "#")
DOCS_URL_PAT = (
    r"\(https://wppbav\.github\.io/bavapi-sdk-python/latest/"
    r"(?P<rel>[^#\)]+)(?P<section>[^\)]*)\)"
)

MKDOCS_HEADER = """---
hide:
    - navigation
---
"""

with open("./CONTRIBUTING.md", encoding="utf-8") as file:
    contributing = file.read()

# Substitute found docs links with relative docs path
# Add ".md" to final relative URL before section index
contributing = re.sub(DOCS_URL_PAT, r"(\g<rel>.md\g<section>)", contributing)

with open("./docs/contributing.md", "w", encoding="utf-8") as file:
    file.write("\n".join((MKDOCS_HEADER, contributing)))
