.PHONY: test

test:
	python -m coverage run -m unittest discover -s tests
	python -m coverage report -m