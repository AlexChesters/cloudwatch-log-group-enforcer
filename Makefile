.PHONY: clean package

package:
	sh package.sh

run:
	AWS_PROFILE=accounts-janitor uv run run.py

build: clean package
