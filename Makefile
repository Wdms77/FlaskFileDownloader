.PHONY: build run test lint

build:
	docker build -t flask-file-downloader .

run:
	docker run -it --rm -p 5000:5000 \
	  -v $(PWD)/logs:/logs \
	  -v $(PWD)/files:/data \
	  flask-file-downloader

format:
	docker run --rm -v $(PWD):/app -w /app python:3.11-slim \
	  bash -c "pip install black  --disable-pip-version-check --no-warn-script-location  && black ."

lint:
	docker run --rm -v $(PWD):/app -w /app python:3.11-slim bash -c "pip install flake8 --disable-pip-version-check --no-warn-script-location && flake8"

test:
	docker run --rm -v $(PWD):/app -w /app flask-file-downloader pytest