run: env-demo
	gunicorn -k eventlet -w 1 baseweb-demo:server

env-%: local-env-% clean-env	
	pip install -r requirements.$*.txt

local-env-%:
	pyenv local baseweb-$*

clean-env:
	pip freeze | cut -d"@" -f1 | cut -d'=' -f1 | xargs pip uninstall -y

pypi:
	pyenv local baseweb

test-docs: env-docs docs

test-test: env-test test
