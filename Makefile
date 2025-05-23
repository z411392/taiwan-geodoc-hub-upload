export UV_PROJECT_ENVIRONMENT=src/venv
export IMAGE_REPOSITORY=asia-east1-docker.pkg.dev/taiwan-geodoc-hub/upload/worker

.PHONY: \
	dev \
	format \
	lint \
	test \
	deploy \
	install \
	tree \
	freeze \
	login \
	keygen \
	build \
	push \
	init



format:
	@uvx ruff format .

dev:
	@firebase emulators:start --only functions

lint:
	@uvx ruff check .

test:
	@uv run pytest -k "test_upload_pdf"

deploy:
	@firebase deploy --only functions

install:
	@uv pip install -e ".[firebase,cli,dev]"
	@uvx playwright install chromium

tree:
	@tree -I 'build|__pycache__|*.egg-info|venv|.venv|*.log'

freeze:
	@uv pip compile pyproject.toml --extra firebase > src/requirements.txt

login:
	@uv run python ./src/main.py auth login

keygen:
	@openssl rand -hex 32

push:
	@docker push $(IMAGE_REPOSITORY)

build:
	@docker build --platform=linux/amd64 . -t $(IMAGE_REPOSITORY)

init:
	@uv run python ./src/main.py topics init