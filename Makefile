# Makefile - Monitor de Sistema com Tkinter

run:
	python3 -m View

install:
	pip install -r requirements.txt

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -r {} +

venv:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
