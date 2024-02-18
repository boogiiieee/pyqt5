run:
	poetry run python app.py

lint:
	ruff check

format:
	ruff format

fix:
	ruff --fix

memray:
	poetry run memray run app.py

report:
	poetry run python -m memray flamegraph $(FILE)
