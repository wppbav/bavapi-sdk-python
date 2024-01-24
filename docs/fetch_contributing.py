"""Sync top-level `CONTRIBUTING.md` file with `contributing.md` in documentation."""

import hashlib
import re

# Replace absolute documentation URLs with relative URIs
# <rel> capture group finds relative path
# <section> capture group finds section index (including "#")
DOCS_URL_PAT = (
    r"\(https://wppbav\.github\.io/bavapi-sdk-python/latest/"
    r"(?P<rel>[^#\)]+)(?P<section>[^\)]*)\)"
)
URL_REPLACE_PAT = r"(\g<rel>.md\g<section>)"

with open("./CONTRIBUTING.md", encoding="utf-8") as file:
    contributing = file.read()

with open("./docs/contributing.md", encoding="utf-8") as file:
    docs_contributing = file.read()

hashed = hashlib.md5(contributing.encode())
hashed_hex = hashed.hexdigest()

MKDOCS_HEADER = f"""---
hide:
    - navigation
---

<!--hash: {hashed_hex}-->
<!--Autogenerated. Edit ./CONTRIBUTING.md top-level file instead.-->
"""

md5_found = found[0] if (found := re.findall(r"<!--hash: (\S+)-->", docs_contributing)) else "none"

if hashed_hex != md5_found:
    # Substitute found docs links with relative docs path
    # Add ".md" to final relative URL before section index
    contributing = re.sub(DOCS_URL_PAT, URL_REPLACE_PAT, contributing)

    with open("./docs/contributing.md", "w", encoding="utf-8") as file:
        file.write("\n".join((MKDOCS_HEADER, contributing)))

    print("updated contributing...")
