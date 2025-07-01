FROM jupyter/datascience-notebook:latest 

# Still a good base for data science tools

USER root
# Install any specific system dependencies your preprocessing might need (e.g., if Polars needs a special C lib)
# RUN apt-get update && apt-get install -y some-lib && rm -rf /var/lib/apt/lists/*
USER jovyan

# Copy your requirements for Jupyter (ensure polars, your db connector, and any plotting libs are here)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# The `work` directory is the default working directory for notebooks in Jupyter Docker Stacks
WORKDIR /home/jovyan/work