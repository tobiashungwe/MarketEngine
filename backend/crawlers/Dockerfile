FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the Pipfile and Pipfile.lock for Pipenv setup
COPY Pipfile* /app/

# Install pipenv and project dependencies
RUN pip install pipenv && pipenv install --system --deploy

# Copy the rest of the project files
COPY . /app

# Set environment variable for Scrapy settings
ENV SCRAPY_SETTINGS_MODULE=backend.crawlers.interface_adapters.settings

# Set the command to run the Scrapy spider
CMD ["scrapy", "crawl", "company_spider"]
