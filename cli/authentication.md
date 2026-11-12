---
title: Authentication
sidebarTitle: Authentication
---

Authenticate against Azure AD with [`orbitra login`](/orbitra-cli-commons#orbitra-login). Credentials are cached locally and reused by every SDK client and CLI command.
There are two different authentication methods: interactive browser, designed for manual user login through a browser, and device-code authentication, designed for agent-aided development. If you would like to authenticate against a specific environment and relay your credentials there, all auth commands accept `--env` to target a specific environment (default: `prod`).

For browser-based user login and development, you can use either of the following authentication methods:

```bash
orbitra login                       # interactive browser flow (default) [all environments]
orbitra login --env dev             # a single environment

orbitra login --use-device-code                 # blocking device-code flow [all environments]
orbitra login --use-device-code --env dev       # a single environment
```

For automation and agents, use the two-step device-code flow: start it, hand out the URL + code, then complete it separately:

```bash
orbitra login --start-device-code      # prints URL + code, returns immediately
orbitra login --complete-device-code   # polls until the token is issued
```

You may inspect the current session with [`orbitra account show`](/orbitra-cli-commons#orbitra-account-show) or request raw access tokens with [`orbitra account get-token`](/orbitra-cli-commons#orbitra-account-get-token).

To clear cached credentials and logout simply:

```bash
orbitra logout              # all environments
orbitra logout --env dev    # a single environment
```
