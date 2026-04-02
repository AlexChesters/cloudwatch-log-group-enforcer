set -e

uv sync --no-dev

mkdir -p build
cp -R .venv/lib/python3.*/site-packages/* build
cp -R cloudwatch_log_group_enforcer/ build/
