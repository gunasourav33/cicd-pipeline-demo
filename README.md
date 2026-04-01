# CI/CD Pipeline Demo

A straightforward Flask REST API with a complete CI/CD pipeline using GitHub Actions. Good for understanding the basic flow: lint → test → docker build → registry push → deploy.

## What's in here

- **Flask REST API**: minimal health check + items CRUD endpoints
- **Full pipeline**: flake8 linting, pytest coverage, Docker build, push to GHCR
- **Deploy stub**: placeholder for deploying to your target (Kubernetes, EC2, whatever)

## Local setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run tests:
```bash
pytest app/test_app.py -v --cov=app
```

Lint:
```bash
flake8 app/
```

Run the app:
```bash
python -m flask --app app.app run
```

Hits `http://localhost:5000/health` to verify it's up.

## API endpoints

- `GET /health` - health status + version
- `GET /items` - list all items
- `POST /items` - add item (JSON: name, description)
- `DELETE /items/<id>` - remove item

## Pipeline stages

The GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **Lint** - flake8 on the app code
2. **Test** - pytest with coverage reporting
3. **Docker** - multi-stage build, push to ghcr.io on main branch only

Push to main triggers the pipeline. PRs run lint + test (no Docker push).

## Docker

Built as multi-stage: first stage runs tests, second stage creates minimal runtime image. Non-root user (appuser) runs the container. Gunicorn on port 8080.

```bash
docker build -t myapp:latest .
docker run -p 8080:8080 myapp:latest
```

## Known issues / TODO

- [ ] Add request tracing across service boundaries
- [ ] Integrate with ECS/EKS deployment (currently a stub in the workflow)
- [ ] Metrics export (Prometheus format) on /metrics endpoint
- Docker image size could be smaller with Alpine, but we're using slim for compatibility
