---
title: Getting started with Orbitra API
sidebarTitle: API Tutorial
---
Orbitra API provides a FastAPI-based foundation for building robust, production-grade REST APIs within the Orbitra ecosystem. It offers seamless integration with Orbitra Lake for data access, built-in authentication/authorization support, and a standardized project structure for rapid API development.

## Key Concepts

### What is Orbitra API ?

Orbitra API is a pre-configured FastAPI template that allows you to quickly build and deploy REST endpoints integrated with Orbitra's data platform and built-in examples. It abstracts away infrastructure concerns and provides:

- **Pre-configured authentication**: Automatic token validation and credential management via Orbitra Commons;
- **Orbitra Lake integration**: Direct access to your data lake through the Lake SDK;
- **Development and deployment ready**: Serverless execution on Azure Functions, pre-configured OpenTelemetry/Azure Monitor telemetry, CI/CD pipeline integration, and local dev container setup.

### REST API Fundamentals

A REST API exposes your application's functionality through HTTP endpoints:

- **Endpoints**: URLs that represent resources (e.g., `/api/tables`, `/api/data`)
- **HTTP Methods**: GET (retrieve), POST (create), PUT (update), DELETE (remove)
- **Request/Response**: Structured data exchange using JSON
- **Status Codes**: HTTP codes indicate success (2xx), client errors (4xx), or server errors (5xx)

## Getting Started with the Template

### 1) Set Up Your Development Environment

From your template project root:

<Tabs>
<Tab title="Using Dev Container (Recommended)">
Open the project in VS Code, press `ctrl+shift+P` and select "Reopen in Container". This automatically configures:
- Python 3.11+ with all dependencies
- FastAPI development server
- Debugging support
- All required tools and libraries
</Tab>

<Tab title="Manual Setup">
```bash
# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```
</Tab>
</Tabs>

### 2) Understand the Main Components

#### API Initialization (`main.py`)

The template includes a minimal `api/main.py` file:

```python
from fastapi import FastAPI

app = FastAPI(
    title="Orbitra API",
    description="REST API for accessing Orbitra data",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orbitra-api"}
```

-> This is your starting point. You'll add endpoints and routers to this file.

### 3) Create Your First Endpoint

Add an endpoint directly to your `api/main.py`:

```python
from fastapi import FastAPI, HTTPException
from orbitra.lake import get_lake_client  # For Orbitra Lake integration

app = FastAPI(
    title="Orbitra API",
    description="REST API for accessing Orbitra data",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orbitra-api"}

@app.get("/api/tables/{namespace}")
async def list_tables(namespace: str):
    """
    List all tables in a specified namespace.
    Args:
      - `namespace`: The namespace containing the tables
    
    Returns:
      - List of table names in the namespace
    """
    try:
        client = get_lake_client()
        tables = client.list_tables(namespace=namespace)
        return {
            "namespace": namespace,
            "tables": tables,
            "count": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4) Run Your API Locally

<Tabs>
<Tab title="VS Code/Cursor UI">

1. Open the Run and Debug panel in VS Code
2. Select "Python: API" configuration
3. Press F5 to launch

</Tab>
<Tab title="Terminal">

```bash
# From your project root, run the app directly
python api/main.py
```

</Tab>
</Tabs>

The template already includes `if __name__ == "__main__":` with `uvicorn.run(...)`, so either option works.

### 5) Test Your Endpoints

<Tabs>
<Tab title="Using curl">
```bash
# List tables in a namespace
curl -X GET "http://localhost:8000/api/tables/playground"

# Get table metadata
curl -X GET "http://localhost:8000/api/tables/playground/my_table"
```
</Tab>

<Tab title="Using Python">
```python
import requests

BASE_URL = "http://localhost:8000"
NAMESPACE = "playground"
TABLE_NAME = "my_table"

# List tables
response = requests.get(f"{BASE_URL}/api/tables/{NAMESPACE}")
print(response.json())

# Get table metadata
response = requests.get(f"{BASE_URL}/api/tables/{NAMESPACE}/{TABLE_NAME}")
print(response.json())
```
</Tab>

<Tab title="Using Swagger UI">
1. Open `http://localhost:8000/docs`
2. Find the endpoint you want to test
3. Click "Try it out"
4. Enter parameters and click "Execute"
5. View the response
</Tab>
</Tabs>

## Deployment

### Serverless runtime and telemetry (pre-configured)

The API template is packaged and deployed as an Azure Function App with telemetry enabled by default:

- `.pipelines/function_app.py` wraps your FastAPI app using `func.AsgiFunctionApp(...)` for serverless execution;
- `.pipelines/host.json` sets `telemetrymode` to OpenTelemetry and keeps HTTP routes at root (`"routePrefix": ""`);
- `configure_azure_monitor()` is enabled to export traces/metrics/logs to Azure Monitor.

No extra telemetry bootstrap is required for the default template flow.

When you've finished developing the main.py file, add the pipeline to your DevOps and hit the run pipeline button in your project. Everything else is already set up for you:

1. **Run the pipeline** in `.pipelines/pipeline.yaml` (builds `functionapp.zip` with `api/`, `.pipelines/function_app.py`, and `.pipelines/host.json`);
2. **Monitor** via your platform observability stack and function app logs.

## Next Steps

- Review the [Orbitra Lake documentation](orbitra-lake-client) for data access patterns.
- Explore the [Flows SDK](orbitra-flows-orbitra_deploy) if you need to orchestrate backend processes.
- Check the [Commons SDK](orbitra-commons-auth-azure) to understand the authentication scenarios.