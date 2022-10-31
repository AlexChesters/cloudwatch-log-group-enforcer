.PHONY: clean install_poetry package

install_poetry:
	( \
		echo 'Installing poetry...' && \
		curl -sSL https://install.python-poetry.org | POETRY_HOME=${HOME}/.poetry python3 - \
	)

package:
	sh package.sh

run:
	poetry run python run.py

build: clean install_poetry package
