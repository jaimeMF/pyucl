.PHONY: doc

all:

clean:
	rm -r VENV_DOCS build

VENV_DOCS: ./*.py docs/requirements.txt
	if test ! -d VENV_DOCS; then virtualenv VENV_DOCS; fi
	. VENV_DOCS/bin/activate && pip install -r docs/requirements.txt .
doc: VENV_DOCS
	. VENV_DOCS/bin/activate && cd docs && env make
