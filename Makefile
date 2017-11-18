all:
	. venv/bin/activate
	python3 -B -m wsrc.build_all

init:
	virtualenv -p python3 venv
	pip install -r requirements.txt

test:
	. venv/bin/activate
	python3 -B -m run_tests

.PHONY: init test

