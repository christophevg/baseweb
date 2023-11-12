requirements.local.txt:
	pip freeze > req.local.txt
	cat requirements.txt | cut -d"=" -f1 > req.txt
	grep -f req.txt -v req.local.txt > $@
	rm req.local.txt req.txt

.PHONY: requirements.local.txt
