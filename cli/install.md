---
title: Installation
sidebarTitle: Install
---

The base version of the Orbitra CLI is part of `orbitra-commons` and is available as soon as that package is installed. The Lake and Flows command groups come from their own packages and are added the same way — the CLI is built on Orbitra Commons and acquires extra command groups from the `orbitra-lake` and `orbitra-flows` packages once they are in your project.

To install the packages, follow the setup steps in the [Environment Setup](/quick_setup) guide. The CLI becomes available as soon as the packages are installed.

Once installed, you may verify it:

```bash
orbitra --help
```

CLI support was introduced in `orbitra-commons` 0.8.0, `orbitra-flows` 0.4.0 and `orbitra-lake` 0.8.0 — these are the minimum versions. Prefer the latest release of each, as newer versions expose additional commands.
