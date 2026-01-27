---
title: Getting started with Orbitra Lake
sidebarTitle: Lake Tutorial
---
Orbitra Lake SDK is your primary interface for interacting with the organization's data lake. It abstracts the underlying cloud infrastructure - provisioned via Orbitra Lake Terraform - to provide a consistent, Pythonic way to manage high-performance tables and raw storage. 

## Key Concepts

### The Orbitra Lake Environment
The SDK operates within a pre-configured ecosystem of Azure Storage Accounts and Databricks Workspaces. By using the SDK, you don't need to worry about JDBC strings or storage keys; the library handles authentication and protocol translation automatically.

### Data lake basics

A data lake is a centralized storage layer for data in many formats (raw files, semi-structured, and fully curated datasets).
Unlike traditional warehouses, data lakes don’t require every dataset to fit a rigid, pre-defined schema, so teams can iterate while still enforcing governance where it matters.

**Important:** Data lakes are designed for immutability. This means you cannot update individual rows or cells in a table as you would in a traditional database. Instead, data is always overwritten at the file or partition level. When you need to change data, you overwrite the relevant partition or the entire table. This approach ensures consistency, supports large-scale analytics, and aligns with how modern data lake formats (like Iceberg) manage data.

### Iceberg Tables

Apache Iceberg is an open table format designed for large-scale analytics on data lakes. It brings many of the reliability and performance guarantees of data warehouses to object storage, without locking you into a specific engine or vendor.

One of Iceberg’s most powerful features is table partitioning. Partitioning allows you to split large tables into smaller, logical segments—such as by date, region, or data source—while still presenting them as a single table to your applications. This makes queries much faster and enables efficient overwrites: instead of rewriting an entire table, you can overwrite just the affected partitions. Iceberg manages all the metadata, tracking schemas, partitions, and snapshots, so you can evolve your data model and scale analytics with confidence.

To learn more about Iceberg tables, visit: https://iceberg.apache.org

#### Cases of use of table partition
- Partitioning by date: For time-series data such as logs, transactions, or daily reports, partitioning tables by date (e.g., year, month, day) allows for efficient querying and overwriting of specific time periods without scanning the entire dataset.
- Partitioning by region or business unit: When data is naturally segmented by geography (e.g., country, state) or organizational unit, partitioning by these fields enables teams to manage, update, or analyze data for specific segments independently.
- Partitioning by data source or type: In scenarios where data comes from multiple sources or represents different categories (e.g., device type, product line), partitioning by source or type helps isolate and efficiently process relevant subsets of data.

#### Example of Table partition by date

In Orbitra Lake, you mark partition columns by setting `kind="partition"` in `ColumnSchema`.

```python
from orbitra.lake import get_lake_client
from orbitra.lake.models.table_schema import TableSchema, ColumnSchema
import pandas as pd

client = get_lake_client()

# Create a table partitioned by report_date
table = TableSchema(
	name="daily_report",
	columns=[
		ColumnSchema(name="report_date", type="string", kind="partition"),
		ColumnSchema(name="client_id", type="string", kind="regular"),
		ColumnSchema(name="value", type="double", kind="regular"),
	],
)
client.create_table(namespace="playground", table=table)
```


## Orbitra Lake SDK in 2 minutes

The SDK handles the “plumbing” (configuration + authentication) so you can start from a client and focus on data.

### 1) Create a client

```python
from orbitra.lake import get_lake_client

client = get_lake_client()  # defaults to environment="prod"
```

Tip: if you need to target a different environment, pass `environment="dev"`.

### 2) Create a table

```python
from orbitra.lake import get_lake_client
from orbitra.lake.models.table_schema import TableSchema, ColumnSchema

client = get_lake_client()

table = TableSchema(
	name="my_table",
	columns=[
		ColumnSchema(name="id", type="int", kind="regular"),
		ColumnSchema(name="name", type="string", kind="regular"),
	],
)

client.create_table(namespace="playground", table=table)
```

### 3) Overwrite data

```python
import pandas as pd
from orbitra.lake import get_lake_client

client = get_lake_client()
df = pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})

client.overwrite_data(namespace="playground", table_name="my_table", df=df)
```
* Note: This method will automatically identify partition columns in the dataframe and will overwrite them. If there are no partition columns, the entire table is overwritten.

### 4) Read data

```python
from orbitra.lake import get_lake_client
from orbitra.lake.models.filter import Filter

client = get_lake_client()

# PyIceberg style
df = client.get_table_data(
	namespace="playground",
	table_name="rendimento_dos_fundos",
	scan_filters=[Filter(column="PATRIMONIO_LIQUIDO", value="1000000000", op=">=")],
)

# SQL style
query = """SELECT * FROM rendimento_dos_fundos WHERE PATRIMONIO_LIQUIDO >= 1000000000"""
df_sql = client.run_query(namespace="playground",
query=query,
engine="local")
```
* Note: In most cases, you'll use `engine="local"` for the SQL method, as it runs queries on your local machine at no extra cost. If you need more powerful hardware, you can choose `engine="remote"` to use databricks's hardware, but this may incur additional usage costs. 
The `local` engine is only available on Linux systems or within Dev Container environments.

## Working with raw files (blobs)

Orbitra Lake SDK also supports saving and reading raw data blobs (for example, landing-zone files before they’re curated into tables).
Some of the methods available are `save_raw_df_to_blob`, `save_raw_bytes_to_blob`,  `read_raw_df_from_blob`, and `read_raw_bytes_from_blob`.

### Example: saving and reading raw df
```python
    from orbitra.lake import get_lake_client
    import pandas as pd

    df = pd.DataFrame({"id": [1, 2], "value": ["A", "B"]})
    client = get_lake_client()
    
	client.save_raw_df_to_blob(df, "test.parquet", namespace="playground")
	df = client.read_raw_df_from_blob("test.parquet", namespace="playground")
```
### Example: saving and reading raw files
```python
from orbitra.lake import get_lake_client
import io

bytes_io = io.BytesIO(b"Hello, world!")
client = get_lake_client()

result = client.save_raw_bytes_to_blob(bytes_io, "test.txt", namespace="playground")
bytes_io = client.read_raw_bytes_from_blob("test.txt", namespace="playground")
```

## Need more details? Use the client reference

For the complete list of methods and examples, see [Orbitra Lake Client](orbitra-lake-client).

