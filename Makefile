GUNICORN=. venv/bin/activate; gunicorn

all: run

run: requirements
	@echo "*** starting the web container"
	@${GUNICORN} -k eventlet -w 1 demo:server

requirements: venv requirements.txt
	@echo "*** setting up requirements"
	@. venv/bin/activate; pip install --upgrade -r requirements.txt > /dev/null

venv:
	@echo "*** building a virtual environment"
	@virtualenv -p python3 $@


upgrade: requirements
	@echo "*** upgrading requirements"
	@. venv/bin/activate; pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

dist: requirements
	@echo "*** building distribution"
	@. venv/bin/activate; python setup.py sdist bdist_wheel


tag:
	@echo "*** tagging as ${TAG}"
	@git tag ${TAG} -m "${MSG}"
	@git push --tags
