all:
	cd venv && . bin/activate && cd .. && python -m wsrc.build_all

init:
	virtualenv -p python3 venv
	pip install -r requirements.txt

test:
	./run_tests_within_venv

.PHONY: init test

