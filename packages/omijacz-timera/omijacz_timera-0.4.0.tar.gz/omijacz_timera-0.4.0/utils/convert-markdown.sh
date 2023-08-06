#!/bin/bash
# This script converts README.md (markdown) to README.rst for PyPI deployment
pandoc --from=markdown --to=rst --output=README.rst README.md