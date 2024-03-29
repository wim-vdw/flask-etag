.PHONY: help install install-dev uninstall tests report html

help:
	@echo "Possible options:"
	@echo "  install     - Install dependencies"
	@echo "  install-dev - Install development dependencies (Pytest and Coverage)"
	@echo "  uninstall   - Uninstall dependencies"
	@echo "  tests       - Execute tests and coverage"
	@echo "  report      - Generate coverage report"
	@echo "  html        - Generate HTML report with coverage data"

install:
	python -m pip install pip setuptools --upgrade
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

install-dev:
	pip install pytest coverage

uninstall:
	pip freeze | xargs pip uninstall -y

tests:
	coverage run --source=myapp -m pytest tests --verbose --exitfirst

report:
	coverage report

html:
	coverage html
