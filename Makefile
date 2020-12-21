.PHONY: help install tests report

help:
	@echo "Possible options:"
	@echo "  install - Install dependencies"
	@echo "  tests   - Execute tests and coverage"
	@echo "  report  - Generate coverage report"

install:
	python -m pip install pip setuptools --upgrade
	python -m pip install pytest coverage
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

tests:
	coverage run --source=myapp -m pytest tests -v

report:
	coverage report
