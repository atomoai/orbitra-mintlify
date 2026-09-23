---
title: Pre-built templates
sidebarTitle: Environment Setup
---
Atomo provides a set of pre-built templates designed to accelerate your data projects:

- **Orbitra API Template**: Kickstart API development with a FastAPI-based project structure, including example endpoints, authentication scaffolding, and integration with Orbitra data models. This template helps you rapidly build, test, and deploy robust APIs within the Orbitra ecosystem.
- **Orbitra Flow Template**: Jumpstart orchestration with ready-to-use Prefect flow examples, making it easy to automate and schedule your data pipelines.
- **Orbitra Data Apps Template**: Quickly build and deploy data-driven applications with a pre-configured project structure. This template provides essential configuration files, a sample Python entry point, and Docker support, enabling rapid prototyping and scalable deployment of Orbitra-based data apps.

Each template comes with CI/CD pipeline integration and a git repository, ensuring your team can collaborate and deploy with confidence. With all the groundwork handled, your data science team can focus on what matters most: building, analyzing, and delivering value from your data.

After opening a template project provided by Atomo, follow these steps:
1. (Optional, but recommended) Open the project in a Dev Container. Atomo will have already configured the container for you, so you can start working immediately.
2. In your terminal, run `uv sync` to automatically install all required dependencies and set up your Python environment. This ensures your project is ready to use.

# How to activate the MCP
At the top of each documentation page, you'll find a "Copy page" button and an arrow next to it. Click the arrow, choose your preferred AI agent, and you'll be redirected to the extension installation page. Install the MCP extension, and you can immediately start asking questions about the documentation.

# Manual Setup
### 1) Get access to Orbitra packages

To install Orbitra SDKs, you’ll need access to your organization’s internal proxy/registry. Contact us (or your internal platform team) to get the registry URL and credentials.

### 2) Install your organization settings package

#### 2.1) Managing dependencies with pyproject.toml
Follow the example `pyproject.toml` file to continue the setup.

```toml
[project]
name = "your-project's-name"
version = "x"
description = "Your project's description"
readme = "README.md"
requires-python = ">=version_wanted"
dependencies = [
    "orbitra-settings-your_company_name",
    "orbitra-lake[azure]",
    "orbitra-flows",
    "orbitra-commons"
]

[tool.uv.sources]
orbitra-settings-your_company_name = { index = "orbitra-private-registry" }
orbitra-lake = { index="orbitra-private-registry"}
orbitra-flows = { index="orbitra-private-registry" }  
orbitra-commons = { index="orbitra-private-registry" }  

[[tool.uv.index]]
name = "orbitra-private-registry"
url = "<url_provided_by_Atomo>"
explicit = true
```
To finish the setup, run:
```bash
uv sync
```

This creates the `.venv` and locks dependencies.

#### 2.2) Managing dependencies with requirements.txt
With the right access, follow the example `requirements.txt` file to continue the setup:
```txt
--index-url https://pypi.org/simple
--extra-index-url <url_provided_by_Atomo>

orbitra-settings-your_company_name
orbitra-lake[azure]
orbitra-flows
orbitra-commons
```
To finish the setup, run:
```bash
pip install -r requirements.txt
```

#### Note
 If you don't need one of Orbitra's package to your project, remove the corresponding dependencies lines on the templates above.

