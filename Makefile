GCP_REGION=australia-southeast1
GCP_PROJECT_ID = glossy-apex-462002-i3
GCP_ARTIFACT_REPOSITORY = python-projects
DOCKER_IMAGE_NAME = at-bus-load

ruff_check:
	uv run ruff check src/
	uv run ruff check --select I src/

ruff_isort:
	uv run ruff check --select I --fix src/

mypy:
	uv run mypy src/ 

# Test commands
test:
	uv run pytest tests/ -v --cov=src/at_bus_load --cov-report=term-missing --cov-report=html:htmlcov

test-unit:
	uv run pytest tests/ -m unit -v

test-coverage:
	uv run pytest tests/ --cov=src/at_bus_load --cov-report=html:htmlcov --cov-report=xml:coverage.xml

test-watch:
	uv run pytest tests/ -v --cov=src/at_bus_load --cov-report=term-missing -f

# Quality checks
quality: ruff_check mypy test

get_api_data:
	uv run get_api_data.py

build_docker_image:
	docker image build --no-cache . --tag $(DOCKER_IMAGE_NAME):latest

tag_docker_image_for_gcp:
	docker tag $(DOCKER_IMAGE_NAME):latest $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(GCP_ARTIFACT_REPOSITORY)/$(DOCKER_IMAGE_NAME):latest

push_docker_image_to_gcp:
	docker push $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(GCP_ARTIFACT_REPOSITORY)/$(DOCKER_IMAGE_NAME):latest