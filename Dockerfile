# Use the official Python image as a base image
FROM python:3.11

# Set the working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.2

# Copy the poetry.lock and pyproject.toml files
COPY poetry.lock pyproject.toml /app/

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-root --no-dev

# Copy the rest of the application code
COPY . /app

# Expose the port the app runs on
EXPOSE 3001

# Set PYTHONPATH to include /app directory
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Command to run the application
CMD ["poetry", "run", "python", "src/serve/serve.py"]
