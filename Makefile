# Makefile

# Install dependencies from requirements.txt
install:
	cd todo_api-main && pip install -r requirements.txt

# Reminder to install Docker Desktop manually
install-docker:
	@echo "Please ensure Docker Desktop is installed manually."

# Define variables
HOST_PORT := 8080
CNTR_PORT := 8000
NAME := oppcontainer

# Build Docker image
build: Dockerfile
	docker build -t opp-api .

# Run Docker container
run-app-local: build
	# Stop and remove the container if it already exists
	-docker stop $(NAME)
	-docker rm $(NAME)
	# Run the new container
	docker run --detach --publish $(HOST_PORT):$(CNTR_PORT) --name $(NAME) opp-api

# Check API
check:
	@echo "Check the API at http://127.0.0.1/docs"

# Combine commands to setup and run everything
# all: install install-docker build run check
