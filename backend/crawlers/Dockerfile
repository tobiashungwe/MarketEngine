# Use official Python image as base
FROM python:3.9-slim

# Set work directory
WORKDIR /app

# Install Pipenv
RUN pip install pipenv

# Copy Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies with Pipenv
RUN pipenv install --system --deploy

# Copy the rest of the application
COPY . .

# Expose the application port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
