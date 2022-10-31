.PHONY: clean install_poetry package

install_poetry:
	( \
		echo 'Installing poetry...' && \
		curl -sSL https://install.python-poetry.org | POETRY_HOME=${HOME}/.poetry python3 - \
	)

package:
	sh package.sh

build: clean install_poetry package
