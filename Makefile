ruff_check:
	uv run ruff check .

mypy:
	uv run mypy .

get_api_data:
	uv run get_api_data.py