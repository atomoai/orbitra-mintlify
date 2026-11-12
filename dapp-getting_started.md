---
title: Getting started with Orbitra Data Apps
sidebarTitle: Data App Tutorial
---

Orbitra Data Apps provide a Streamlit-based template to build interactive data products that run locally and deploy seamlessly to your cloud via Azure Container Apps. The template includes a dev container, CI/CD pipeline, Docker image, and a minimal example wired to Orbitra Lake.

**Key Features:**
- **Streamlit UI**: Build interactive interfaces with Python-only code.
- **Orbitra Environment Integration**: Use `get_lake_client()` to create an `OrbitraLakeClient` with Orbitra Commons-managed authentication, and connect your app to Orbitra Flows scheduled pipelines.
- **Dev Container**: Reproducible environment with `uv` package manager and tooling.
- **CI/CD Pipeline**: Automated builds and deployments to Azure Container Apps pre-configured.

## Getting Started

### Step 1: Set Up Your Development Environment

<Tabs>
<Tab title="Using Dev Container (Recommended)">
1. In VS Code, press `Ctrl+Shift+P` → "Reopen in Container".
2. The container auto-runs `uv sync` to install dependencies.
</Tab>
<Tab title="Manual Setup">

```bash
# From project root
uv sync --all-extras

# (optional) activate venv if you created one
source .venv/bin/activate
```

</Tab>
</Tabs>

### Step 2: Run the App Locally

<Tabs>
<Tab title="VS Code Debug (Recommended)">
1. Open the Run and Debug panel in VS Code
2. Select "Python: Streamlit" configuration
3. Press F5 to launch

The app will be available at http://localhost:8501.
</Tab>
<Tab title="Command Line">

```bash
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
```

</Tab>
</Tabs>

## Understanding the App

### Minimal Example

A minimal example usage of the streamlit framework is shown below:

```python
from orbitra.lake import get_lake_client
from orbitra.lake.client import OrbitraLakeClient
import streamlit as st

@st.cache_data
def load_dash_data() -> list[str]:
    client: OrbitraLakeClient = get_lake_client()
    namespaces = client.list_namespaces()
    return namespaces

with st.sidebar:
    st.title("Orbitra Dapps")
    if st.button("Clear Cache"):
        st.cache_data.clear()

namespaces = load_dash_data()
st.title("Orbitra Namespaces")
st.write(namespaces)
```

**Key operations:**
- `@st.cache_data`: Cache expensive operations like data fetches
- `st.cache_data.clear()`: Invalidate cached results when users need a fresh read from Orbitra Lake
- `get_lake_client()`: Access Orbitra Lake without manual authentication
- Sidebar: Navigation and controls

### Extended Streamlit Patterns

When you are ready to add interactivity beyond the minimal app, you can use the following patterns:

```python
from concurrent.futures import ThreadPoolExecutor
from orbitra.lake import get_lake_client
from orbitra.lake.client import OrbitraLakeClient
import streamlit as st

client: OrbitraLakeClient = get_lake_client()
namespaces = client.list_namespaces()

selected_namespace = st.selectbox("Namespace", namespaces)
search = st.text_input("Search tables")

if st.button("Refresh"):
    st.cache_data.clear()
    st.rerun()

def get_tables(namespace: str) -> list[str]:
    return client.list_tables(namespace=namespace)

def get_table_count(namespace: str) -> int:
    return len(client.list_tables(namespace=namespace))

with st.spinner("Loading tables in parallel..."):
    with ThreadPoolExecutor(max_workers=2) as executor:
        tables_future = executor.submit(get_tables, selected_namespace)
        count_future = executor.submit(get_table_count, selected_namespace)
        tables = tables_future.result()
        total_tables = count_future.result()

filtered_tables = [t for t in tables if search.lower() in t.lower()]
st.caption(f"Total tables in namespace: {total_tables}")
st.metric("Table count", len(filtered_tables))
st.dataframe(filtered_tables)
```

**Extended operations:**

- `st.button("Refresh")`: Trigger manual reloads for user-driven interactions
- `st.cache_data.clear()`: Clear memorized Streamlit data before rerunning so the UI fetches the latest values
- `st.selectbox("Namespace", namespaces)`: Let users choose a value from loaded data
- `st.text_input("Search")`: Capture user text filters before querying or rendering
- `st.metric("Table count", len(filtered_tables))`: Highlight key KPIs at a glance
- `st.dataframe(data)`: Render tabular results with built-in sorting and scrolling
- `st.spinner("Loading data...")`: Show progress feedback during slower operations
- `concurrent.futures.ThreadPoolExecutor`: Execute independent data reads in parallel for better responsiveness

## Development Workflow

### Common Tasks

- Edit `main.py` or create new modules
- Use Orbitra Lake for data access (see [Lake Tutorial](lake-getting_started))
- **Run locally**: Use VS Code "Python: Streamlit" debug config or `streamlit run main.py`
- **Clear cache**: Use the sidebar button or call `st.cache_data.clear()`
- **Format/lint**: Ruff is pre-configured in the dev container. Run `uvx ruff format` to fix formatting issues

## Deployment

### CI/CD Pipeline

The preconfigured pipeline (`.pipelines/pipeline.yaml`) automatically:

1. **Builds** a Docker image from `.pipelines/Dockerfile`
2. **Pushes** the image to your Azure Container Registry (ACR)
3. **Deploys** to Azure Container Apps with the new image tag

**How to deploy:**

- Commit and push to the main branch
- The pipeline triggers automatically
- Monitor progress in Azure DevOps
- View logs and status in Azure Portal

<Info>
Configuration uses Azure DevOps service connections and variable groups managed by your platform team. Never hardcode secrets or resource names in your repository.
</Info>

## Next Steps

- **Build your app**: Add pages and components to `main.py` or organize into modules
- **Connect to data**: Use [Orbitra Lake](lake-getting_started) for data access
- **Deploy**: Commit and push to your default branch to trigger the pipeline
