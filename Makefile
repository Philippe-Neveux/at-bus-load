GCP_REGION=australia-southeast1
GCP_PROJECT_ID = glossy-apex-462002-i3
GCP_ARTIFACT_REPOSITORY = python-projects
DOCKER_IMAGE_NAME = at-bus-load

ruff_check:
	uv run ruff check .

mypy:
	uv run mypy .

get_api_data:
	uv run get_api_data.py

build_docker_image:
	docker image build --no-cache . --tag $(DOCKER_IMAGE_NAME):latest

tag_docker_image_for_gcp:
	docker tag $(DOCKER_IMAGE_NAME):latest $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(GCP_ARTIFACT_REPOSITORY)/$(DOCKER_IMAGE_NAME):latest

push_docker_image_to_gcp:
	docker push $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(GCP_ARTIFACT_REPOSITORY)/$(DOCKER_IMAGE_NAME):latest