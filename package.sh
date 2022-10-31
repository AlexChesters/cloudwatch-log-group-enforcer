set -e

export PATH="${HOME}/.poetry/bin:${PATH}"
export VENV_PATH=$(poetry env info -p)

poetry install --only main

poetry build --format wheel
pip install ./dist/*.whl -t lambda_dist

cd lambda_dist && zip lambda * -r
