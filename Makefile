.PHONY: help dev lock test cover cover-html fmt type pre-commit

.DEFAULT: help
help:
	@echo "make dev"
	@echo "	prepare development environment"
	@echo "make lock"
	@echo "	lock requirements"
	@echo "make test"
	@echo "	run tests"
	@echo "make cover"
	@echo "	run tests and coverage"
	@echo "make cover-html"
	@echo "	run tests, coverage and open HTML report"
	@echo "make fmt"
	@echo "	run black code formatter"
	@echo "make type"
	@echo "	run mypy static type checker"
	@echo "make pre-commit"
	@echo "	run pre-commit hooks"

dev:
	pipenv install --dev
	pipenv run pre-commit install

lock:
	pipenv lock
	pipenv requirements > requirements.txt
	pipenv requirements --dev > requirements-dev.txt

test:
	pipenv run test

cover:
	pipenv run coverage run -m unittest
	pipenv run coverage report -m

cover-html:
	pipenv run coverage run -m unittest
	pipenv run coverage html
	open htmlcov/index.html

fmt:
	pipenv run black .

type:
	pipenv run mypy .

pre-commit:
	pipenv run pre-commit
