run:
	env\Scripts\activate && uvicorn main:app --reload

# Docker commands
IMAGE_NAME=backend-app
IMAGE_TAG=latest
TAR_FILE=backend-app.tar

# Build Docker image
docker-build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

# Build and save Docker image as tar file
docker-build-tar: docker-build
	docker save $(IMAGE_NAME):$(IMAGE_TAG) -o $(TAR_FILE)
	@echo "Docker image saved to $(TAR_FILE)"
	@echo "To load on server: docker load -i $(TAR_FILE)"

# Build, save as tar, and compress with gzip (requires gzip - available on Linux/Mac/Git Bash)
docker-build-tar-gz: docker-build-tar
	@if command -v gzip >/dev/null 2>&1; then \
		gzip -f $(TAR_FILE); \
		echo "Compressed image saved to $(TAR_FILE).gz"; \
		echo "To load on server: gunzip -c $(TAR_FILE).gz | docker load"; \
	else \
		echo "gzip not found. Using uncompressed tar file: $(TAR_FILE)"; \
		echo "On Windows, you can use 7-Zip or PowerShell to compress the tar file."; \
	fi

# Clean Docker artifacts
docker-clean:
	docker rmi $(IMAGE_NAME):$(IMAGE_TAG) 2>/dev/null || true
	rm -f $(TAR_FILE) $(TAR_FILE).gz
	@echo "Cleaned Docker artifacts"