PYTHON ?= python3
export PYTHONPATH := src

.PHONY: help demo test clean

help:
	@echo "make demo  - regenera el run de demostración y audita"
	@echo "make test  - suite de tests del harness"
	@echo "make clean - borra informes generados"

demo:
	$(PYTHON) scripts/make_demo_run.py
	$(PYTHON) -m audit run --adapter mock --run-dir runs/demo-model --out reports/demo

test:
	$(PYTHON) -m pytest

clean:
	rm -rf reports/demo .pytest_cache
