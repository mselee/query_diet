.PHONY: check
check: 
	@poetry run black --check .
	@poetry run isort --check-only

.PHONY: test
test:
	@rm -f fitness.sqlite3
	@poetry run pytest tests

.PHONY: format
format:
	@poetry run black .
	@poetry run isort -y

.PHONY: ci
ci: check test
