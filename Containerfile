FROM docker.io/library/python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# The environment lives outside /app, so mounting the code for development doesn't hide it.
ENV UV_PROJECT_ENVIRONMENT=/venv PATH=/venv/bin:$PATH PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project
COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
