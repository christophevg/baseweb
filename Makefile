#MODEL=qwen3.5:397b-cloud
#ARGS += --plugin-dir ./
ARGS += --plugin-dir ../c3
ARGS += --agent c3:project-manager
ARGS += "manage the project!"

-include ~/.claude/Makefile

# colors

GREEN=\033[0;32m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

# test envs

PYTHON_VERSIONS ?= 3.9.18 3.10.13 3.11.12 3.12.10
RUFF_PYTHON_VERSION ?= py311

PROJECT=$(shell basename $(CURDIR))
PACKAGE_NAME=baseweb

LOG_LEVEL?=ERROR
SILENT?=yes

RUN_CMD?=LOG_LEVEL=$(LOG_LEVEL) python -m $(PACKAGE_NAME)
RUN_ARGS?=

TEST_ENVS=$(addprefix $(PROJECT)-test-,$(PYTHON_VERSIONS))

# Virtual environment name
VENV_NAME=baseweb

install:
	@echo "👷‍♂️ $(BLUE)installing package in development mode$(NC)"
	pip install -e ".[dev]"

install-env-run:
	@echo "👷‍♂️ $(BLUE)creating virtual environment $(PROJECT)-run$(NC)"
	pyenv local --unset
	-pyenv virtualenv $(PROJECT)-run > /dev/null
	pyenv local $(PROJECT)-run
	pip install -U pip > /dev/null
	pip install -e ".[dev]" > /dev/null

install-env-docs:
	@echo "👷‍♂️ $(BLUE)creating virtual environment $(PROJECT)-docs$(NC)"
	pyenv local --unset
	-pyenv virtualenv $(PROJECT)-docs > /dev/null
	pyenv local $(PROJECT)-docs
	pip install -U pip > /dev/null
	pip install -e ".[dev]" > /dev/null

install-env-test: $(TEST_ENVS)

$(PROJECT)-test-%:
	@echo "👷‍♂️ $(BLUE)creating virtual test environment $@$(NC)"
	pyenv local --unset
	-pyenv virtualenv $* $@ > /dev/null
	pyenv local $@
	pip install -U pip > /dev/null
	pip install -e ".[dev]" > /dev/null

uninstall: uninstall-envs

uninstall-envs: uninstall-env-test uninstall-env-docs uninstall-env-run env clean-env

uninstall-env-test: $(addprefix uninstall-env-test-,$(PYTHON_VERSIONS))

$(addprefix uninstall-env-test-,$(PYTHON_VERSIONS)) uninstall-env-docs uninstall-env-run: uninstall-env-%:
	@echo "👷‍♂️ $(RED)deleting virtual environment $(PROJECT)-$*$(NC)"
	-pyenv virtualenv-delete $(PROJECT)-$*

clean-env:
	@echo "👷‍♂️ $(RED)deleting all packages from current environment$(NC)"
	pip freeze | cut -d"@" -f1 | cut -d'=' -f1 | xargs pip uninstall -y > /dev/null

upgrade:
	@pip list --outdated | tail +3 | cut -d " " -f 1 | xargs -n1 pip install -U

# env switching

env-%:
	@echo "👷‍♂️ $(BLUE)activating $* environment$(NC)"
	@pyenv local $(PROJECT)-$*

env:
	@echo "👷‍♂️ $(BLUE)activating project environment$(NC)"
	@pyenv local $(PROJECT)

env-test:
	@echo "👷‍♂️ $(BLUE)activating test environments$(NC)"
	@pyenv local $(TEST_ENVS)

# functional targets

run: env-run
	@echo "👷‍♂️ $(BLUE)running$(GREEN) $(RUN_CMD) $(RUN_ARGS)$(NC)"
	@$(RUN_CMD) $(RUN_ARGS)

test: lint
	pytest --cov=baseweb --cov-report=term-missing

coverage: test
	coverage report
	coverage lcov

lint:
	ruff check src tests

docs: env-docs
	cd docs; make html
	open docs/_build/html/index.html

# packaging targets

publish-test: dist
	twine upload --repository testpypi dist/*

publish: dist
	twine upload dist/*

dist: dist-clean
	python -m build

dist-clean: clean
	rm -rf dist build *.egg-info

clean:
	find . -type f -name "*.backup" | xargs rm

.PHONY: dist docs test

# include optional a personal/local touch

-include Makefile.mak
