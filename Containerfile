# Use a Python base image
FROM python:3.10-slim-buster # Or the appropriate Python version matching pyproject.toml

# Set the working directory inside the container
WORKDIR /app/backend

# Install Poetry
RUN pip install poetry

# Copy the pyproject.toml and poetry.lock (if it exists) to leverage Docker cache
COPY backend/pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root --no-dev # Install only production dependencies in the final image

# Copy the rest of the application code
COPY backend/ ./

# Expose the port the application runs on
EXPOSE 8000

# Command to run the application
# Assumes the app is in app/main.py and the FastAPI instance is named 'app'
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
