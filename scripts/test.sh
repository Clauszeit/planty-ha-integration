#!/usr/bin/env bash
set -euo pipefail

mkdir -p coverage
python -m coverage run --branch --source=custom_components.planty \
  -m unittest discover -s tests -v
python -m coverage xml -o coverage/sonar-coverage.xml
