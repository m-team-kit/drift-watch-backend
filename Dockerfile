# ================================== BUILDER ===================================
ARG  PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION} as build

# Environments to reduce size of docker image
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONFAULTHANDLER=true
ENV PYTHONUNBUFFERED=true
ENV PYTHONHASHSEED=random
ENV PIP_NO_CACHE_DIR=true
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

# Install system updates and tools
RUN apt-get update 
RUN python -m pip install --upgrade pip

# Add workdir and user non root user
WORKDIR /srv
RUN useradd -m sid

# ================================= PRODUCTION =================================
FROM build AS production
USER root

# Copy and install production requirements
COPY --chown=sid:sid backend /srv/backend
RUN python -m pip install -r backend/requirements.txt

# Change to non root user and expose port
USER sid
EXPOSE 8000

# Define entrypoint and default command
ENTRYPOINT [ "python" ]
CMD [ "-m", "uvicorn", "backend.autoapp:app", "--proxy-headers", "--host", "0.0.0.0" ]

# ================================= TESTING ====================================
FROM production AS testing
USER root

# Copy and install production requirements
COPY --chown=sid:sid requirements-test.txt /srv
RUN python -m pip install -r requirements-test.txt

# Copy the tests and sandbox for the application
COPY --chown=sid:sid sandbox /srv/sandbox
COPY --chown=sid:sid tests /srv/tests
COPY --chown=sid:sid pyproject.toml /srv

# Change to non root user and expose port
RUN chown -R sid:sid /srv
USER sid

# Define entrypoint and default command
ENTRYPOINT [ "python" ]
CMD [ "-m", "pytest", "-n", "auto", "--dist", "loadfile", "tests" ]

# ================================= DEVELOPMENT ================================
FROM testing AS development
USER root

# Copy and install development requirements
COPY --chown=sid:sid requirements-dev.txt /srv
RUN python -m pip install -r requirements-dev.txt

# Copy the rest of the application
COPY --chown=sid:sid .. /srv

# Change to non root user and expose port
USER sid
EXPOSE 5000
EXPOSE 5678

# Define entrypoint and default command
ENTRYPOINT ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client" ]
CMD ["-m", "flask", "run", "--no-debugger", "--no-reload", "--host", "0.0.0.0" ]
