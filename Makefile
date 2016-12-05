init:
	virtualenv -p python3 venv
	pip install -r requirements.txt

test:
	./run_tests_within_venv

.PHONY: init test

