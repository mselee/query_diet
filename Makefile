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

.PHONY: linux_release
linux_release:
	docker pull quay.io/pypa/manylinux2010_x86_64
	docker run --rm -i -v `pwd`:/io quay.io/pypa/manylinux2010_x86_64 /io/make-linux-release.sh