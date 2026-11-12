---
title: Orbitra CLI
sidebarTitle: Overview
---

Orbitra CLI `orbitra` is a command-line interface for the Orbitra platform. This interface allows developers to execute different platform functionalities without writing a full Python script. The base version of the Orbitra CLI wraps commands from the Orbitra Commons SDK, such as authentication, account, email and secrets commands. If a developer needs functionalities from the Orbitra Lake or Orbitra Flows SDKs, those contexts can be plugged into the base version once the modules are installed in the environment.

## Command groups

| Group | Commands | Provided by |
| --- | --- | --- |
| Session | [login](/orbitra-cli-commons#orbitra-login), [logout](/orbitra-cli-commons#orbitra-logout) | [`orbitra-commons`](/orbitra-cli-commons) |
| `account` | [show](/orbitra-cli-commons#orbitra-account-show), [get-token](/orbitra-cli-commons#orbitra-account-get-token) | [`orbitra-commons`](/orbitra-cli-commons) |
| `email` | [send](/orbitra-cli-commons#orbitra-email-send) | [`orbitra-commons`](/orbitra-cli-commons) |
| `secrets` | [set](/orbitra-cli-commons#orbitra-secrets-set), [list](/orbitra-cli-commons#orbitra-secrets-list), [delete](/orbitra-cli-commons#orbitra-secrets-delete) | [`orbitra-commons`](/orbitra-cli-commons) |
| `flows` | [run](/orbitra-cli-flows#orbitra-flows-run), [status](/orbitra-cli-flows#orbitra-flows-status) | [`orbitra-flows`](/orbitra-cli-flows) |
| `lake` | [list-namespaces](/orbitra-cli-lake#orbitra-lake-list-namespaces), [list-tables](/orbitra-cli-lake#orbitra-lake-list-tables), [get-table-metadata](/orbitra-cli-lake#orbitra-lake-get-table-metadata), [get-data](/orbitra-cli-lake#orbitra-lake-get-data), [run-query](/orbitra-cli-lake#orbitra-lake-run-query), [create-or-update-table](/orbitra-cli-lake#orbitra-lake-create-or-update-table), [overwrite-data](/orbitra-cli-lake#orbitra-lake-overwrite-data), [upload-bytes-to-raw](/orbitra-cli-lake#orbitra-lake-upload-bytes-to-raw), [download-bytes-from-raw](/orbitra-cli-lake#orbitra-lake-download-bytes-from-raw) | [`orbitra-lake`](/orbitra-cli-lake) |

Every command and group supports `--help`:

```bash
orbitra --help
orbitra flows --help
orbitra lake get-data --help
```

## Examples

Lets say you need to run a deployment that creates tables and then check the result. You can chain a few commands:

```bash
orbitra login
orbitra flows run --deployment "my_flow/my_deployment" --parameters '{"param1": "my_value", "param2": "my_value"}' --wait
orbitra lake list-namespaces
orbitra lake list-tables --namespace "my_namespace"
```

Or, for an agent verifying data across multiple tables to confirm information for a user:

```bash
orbitra login --start-device-code
orbitra login --complete-device-code
orbitra lake get-data --namespace "my_namespace" --table "my_table" --limit 100
orbitra lake run-query --namespace "my_namespace" --query "SELECT COUNT(*) FROM my_other_table"
```