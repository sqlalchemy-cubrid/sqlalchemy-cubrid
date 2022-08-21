.PHONY: install, clean

VENV = venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip


install:
	$(PIP) install -r requirements.txt 
	$(PIP) install -r requirements-dev.txt

clean:
	rm -rf __pycache__
	rm -rf venv