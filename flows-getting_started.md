---
title: ' '
sidebarTitle: Flows Tutorial
---

# Getting started with Orbitra Flows

Orbitra Flows is your workflow orchestration framework built on top of Prefect and integrated with Orbitra's environment. It provides a streamlined way to build, deploy, and monitor data pipelines and automated workflows in your organization's infrastructure.

## What is Prefect?

Prefect is a modern workflow orchestration platform that allows you to build, observe, and react to data pipelines. Think of it as a way to define Python functions as tasks, chain them together into workflows (called "flows"), and execute them reliably with features like retries, scheduling, and observability.

### Flows and Tasks

In Prefect terminology:
- **Task**: A Python function decorated with `@task` that represents a discrete unit of work
- **Flow**: A Python function decorated with `@flow` that orchestrates multiple tasks into a complete workflow

Tasks can be retried, cached, and monitored independently. Flows provide the overall structure and can be scheduled, triggered, or executed on-demand.

**Important**: When using Orbitra Flows, the `@orbitra_deployment` decorator **replaces** the Prefect `@flow` decorator. You don't need both - `@orbitra_deployment` handles flow registration and deployment configuration in one step.

## Orbitra Flows vs Plain Prefect

While you can use Prefect directly, Orbitra Flows provides:
- **Declarative Deployments**: Use the `@orbitra_deployment` decorator to register and manage flow deployments consistently:
    - Multiple schedules with cron expressions, intervals, and RRULE support
    - Custom container sizing and concurrency limits for your deployments
    - Pre-configured connections to Orbitra Lake, authentication, and compute resources
    - Managed execution identity integrated with the Orbitra ecosystem (Lake, Flows, Email, and related services)
    - Monitoring and alerting integrations, including notifications via Microsoft Teams and Slack
    - Self-hosted infrastructure alerting for operational visibility
    - Multiple pre-configured self-hosted worker profiles (Container Instances Spot, dedicated Container Instances, and VMs)
    - Repository templates with pre-configured CI/CD pipelines for flow deployment
    - Cloud storage for retry logic to reuse results if task/flow fails

## Orbitra Flows SDK in 2 minutes

### 1) Define a simple flow

```python
from prefect import task
from orbitra.flows.orbitra_deploy import orbitra_deployment

@task
def extract_data():
    # Simulate data extraction
    return {"records": [1, 2, 3, 4, 5]}

@task
def transform_data(data):
    # Simulate transformation
    return {"records": [x * 2 for x in data["records"]]}

@task
def load_data(data):
    # Simulate loading
    print(f"Loading {len(data['records'])} records")
    return data

@orbitra_deployment(name="simple-etl")
def simple_etl_flow():
    raw_data = extract_data()
    transformed_data = transform_data(raw_data)
    result = load_data(transformed_data)
    return result

# Run locally
if __name__ == "__main__":
    simple_etl_flow()
```

### 2) Add retry logic and result persistence

Orbitra Flows works seamlessly with Orbitra Lake for data persistence. The `persist_result=True` parameter enables cloud storage of task results, allowing subsequent runs to reuse successful task outputs if the flow fails:

```python
from prefect import task
from orbitra.flows.orbitra_deploy import orbitra_deployment
from orbitra.lake import get_lake_client
import pandas as pd

@task(retries=3, retry_delay_seconds=15, persist_result=True)
def fetch_and_store_data():
    # Your data fetching logic
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "value": [100, 200, 300],
        "date": ["2026-01-10", "2026-01-11", "2026-01-12"]
    })
    
    # Store in Orbitra Lake
    client = get_lake_client()
    client.overwrite_data(
        namespace="analytics",
        table_name="daily_metrics",
        df=df
    )
    return len(df)

@orbitra_deployment(name="data-ingestion")
def data_ingestion_flow():
    records_processed = fetch_and_store_data()
    print(f"Successfully processed {records_processed} records")

if __name__ == "__main__":
    data_ingestion_flow()
```

### 3) Add production configuration

Now let's add schedules, resource limits, and other production settings:

```python
from prefect import task
from orbitra.flows.orbitra_deploy import orbitra_deployment
from orbitra.lake import get_lake_client
import pandas as pd

@task
def fetch_and_store_data():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "value": [100, 200, 300],
        "date": ["2026-01-10", "2026-01-11", "2026-01-12"]
    })
    client = get_lake_client()
    client.overwrite_data(
        namespace="analytics",
        table_name="daily_metrics",
        df=df
    )
    return len(df)

@orbitra_deployment(
    name="daily-data-ingestion",
    description="Ingests daily metrics into the analytics namespace",
    schedules=["cron=0 2 * * *"],  # Run daily at 2 AM
    tags=["analytics", "daily"],
    concurrency=1,  # Only allow 1 concurrent run
    container_size="S",  # 2 GB memory / 1 CPU
    enable_schedules_on_creation=True
)
def data_ingestion_flow():
    records_processed = fetch_and_store_data()
    print(f"Successfully processed {records_processed} records")

if __name__ == "__main__":
    data_ingestion_flow()
```

The `@orbitra_deployment` decorator handles flow definition and deployment configuration. Here we've added:
- A cron schedule to run daily at 2 AM
- Concurrency limit to prevent overlapping runs
- Tags for organization
- Container size configuration
- Enabled schedules on creation


## Advanced Configuration

The `@orbitra_deployment` decorator supports advanced options for container sizes if you must run heavy computation. You can use predefined sizes ("XS", "S", "M", "L") or specify custom resources:

```python
from orbitra.flows.orbitra_deploy import orbitra_deployment, ContainerSize

@orbitra_deployment(
    name="advanced-etl",
    description="Production ETL with custom resources",
    container_size=ContainerSize(memory_gb=4, cpu_cores=2),  # Custom resources
)
def advanced_flow():
    pass
```
## Monitoring and Observability

Orbitra Flows automatically tracks:
- Flow run status (success, failure, running);
- Task execution times and states;
- Logs from all tasks and flows;
- Retry attempts and failures.

Access the Prefect UI to monitor your workflows in real-time. All flows deployed via Orbitra Flows are automatically connected to your organization's Prefect server workspace.

## Need more details?

For complete deployment and configuration options, see:
- [Orbitra Deploy Reference](orbitra-flows-orbitra_deploy)
- [Prefect Documentation](https://docs.prefect.io/v3/get-started)