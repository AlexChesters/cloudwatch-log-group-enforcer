set -e

export PATH="${HOME}/.poetry/bin:${PATH}"
export VENV_PATH=$(poetry env info -p)

poetry install --only main
mkdir build
cp -R ${VENV_PATH}/lib/python3.*/site-packages/* build/
cp -R cloudwatch_log_group_enforcer/ build/
