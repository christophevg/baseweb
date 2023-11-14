requirements.local.txt:
	pip freeze > req.local.txt
	cat requirements.txt | cut -d"=" -f1 > req.txt
	grep -f req.txt -v req.local.txt > $@
	rm req.local.txt req.txt

.PHONY: requirements.local.txt

clean-requirements:
	pip freeze | cut -d'=' -f1 | xargs pip uninstall -y
	pip install -r requirements.txt
	pip install -r requirements.base.txt

run:
	gunicorn -k eventlet -w 1 baseweb-demo:server
