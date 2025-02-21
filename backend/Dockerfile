FROM python:3.12-slim as requirements-stage

WORKDIR /tmp

# Install poetry using pip
RUN pip install poetry==1.7.1

# Configure poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Copy only pyproject.toml and poetry.lock first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Configure poetry and export dependencies
RUN poetry install --no-root \
    && poetry export --format requirements.txt --output requirements.txt --without-hashes

# Create necessary directories
RUN mkdir -p /home/app /home/data/docs

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code
COPY ./app /home/app
COPY ./data/docs /home/data/docs

WORKDIR /home

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]