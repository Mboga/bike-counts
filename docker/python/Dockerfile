FROM python:3.9-slim-buster
WORKDIR /app

# Copy the requirements file from the build context (which is ./docker/python/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The actual script 'preprocessing.py' is NOT copied here.
# It will be volume-mounted from ./scripts/ by docker-compose.yml.
# This makes it easier to edit the script locally and have changes reflected instantly.
# If you wanted to bake the script into the image for a production-like immutable setup,
# you would uncomment the line below and adjust path:
# COPY ../../scripts/preprocessing.py /app/scripts/preprocessing.py