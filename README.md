# FastAPI Web App

This repository contains a FastAPI web application with various endpoints for health checks, CPU/memory load generation, crash simulation, slow response simulation, random failures, and Prometheus metrics.

## Setup Instructions

Follow these steps to set up the application from scratch after cloning the repository from GitHub.

### Prerequisites

- Python 3.9 or higher
- `uvicorn` for running the FastAPI application
- Git for cloning the repository

### Installation Steps

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd webapp-python
   ```

2. **Install Python**:
   Ensure Python 3.9 or higher is installed on your system. Verify the installation:

   ```bash
   python3 --version
   ```

3. **Create a Virtual Environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. **Install Required Modules**:
   Install the dependencies listed in `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**:
   Create a `.env` file in the project root and add the following variables:

   ```env
   DATABASE_URL=sqlite:///./test.db
   SECRET_KEY=your-secret-key
   ```

6. **Run the Application**:
   Start the FastAPI application using `uvicorn`:

   ```bash
   uvicorn app.main:app --reload
   ```

7. **Access the Application**:
   Open your browser and navigate to:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## API Endpoints

### Health Check Endpoints

- **`GET /healthz`**: Liveness probe to check if the app is running.
- **`GET /readyz`**: Readiness probe to check if the app is ready to serve traffic.

### CPU & Memory Load Generator

- **`GET /load`**: Simulates CPU and memory stress.

### Crash Simulation

- **`GET /crash`**: Simulates an application crash.

### Slow Response Simulation

- **`GET /slow?delay=<seconds>`**: Simulates a slow response with a configurable delay (default: 5 seconds).

### Random Failures

- **`GET /random-failure`**: Simulates random failures with a 50% chance of success.

### Metrics Endpoint

- **`GET /metrics`**: Exposes Prometheus metrics for monitoring.

---

## Testing

1. **Run Unit Tests**:
   Use `pytest` to run the unit tests:

   ```bash
   PYTHONPATH=. pytest app/test_main.py
   ```

2. **Test Coverage**:
   Ensure all endpoints are covered by the tests.

---

## Notes

- Ensure the `.env` file is properly configured before running the application.
- Use the `/metrics` endpoint to monitor the application with Prometheus.

---

## License

This project is licensed under the MIT License.
