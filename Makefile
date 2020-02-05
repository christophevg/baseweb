VENV=. venv/bin/activate;
GUNICORN=${VENV} gunicorn
PYTHON=${VENV} python
PIP=${VENV} pip
TWINE=${VENV} twine

all: run

run: requirements
	@echo "*** starting the web container"
	@${GUNICORN} -k eventlet -w 1 demo:server

requirements: venv requirements.txt
	@echo "*** setting up requirements"
	@${PIP} install --upgrade -r requirements.txt > /dev/null

venv:
	@echo "*** building a virtual environment"
	@virtualenv -p python3 $@


upgrade: requirements
	@echo "*** upgrading requirements"
	@${PIP} list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

dist: requirements
	@echo "*** building distribution"
	@${PYTHON} setup.py sdist bdist_wheel


tag:
	@echo "*** tagging as ${TAG}"
	@git tag ${TAG} -m "${MSG}"
	@git push --tags


publish-test: dist
	${TWINE} upload --repository-url https://test.pypi.org/legacy/ dist/*

publish: dist
	${TWINE} upload dist/*

test: requirements
	${VENV} tox

coverage: test
	${VENV} coverage report

docs: requirements
	${VENV} cd docs; make html
	open docs/_build/html/index.html

clean:
	find . | grep '\.backup' | xargs rm

.PHONY: dist docs
