# Generate API documentation for orbitra-lake
# (the .cli module is excluded: it is covered by the CLI reference, see generate-cli-docs)
generate-lake-docs:
    rm -rf orbitra-lake*
    cd ..; uv run mdxify orbitra.lake --root-module orbitra.lake --output-dir docs --anchor-name "Lake SDK" --no-update-nav --exclude orbitra.lake.cli

# Generate API documentation for orbitra-flows
generate-flows-docs:
    rm -rf orbitra-flows*
    cd ..; uv run mdxify orbitra.flows --root-module orbitra.flows --output-dir docs --anchor-name "Flows SDK" --no-update-nav --exclude orbitra.flows.cli

# Generate API documentation for orbitra-commons
generate-commons-docs:
    rm -rf orbitra-commons*
    cd ..; uv run mdxify orbitra.commons --root-module orbitra.commons --output-dir docs --anchor-name "Commons SDK" --no-update-nav --exclude orbitra.commons.cli
    cd ..; uv run mdxify orbitra.commons.auth --root-module orbitra.commons.auth --output-dir docs --anchor-name "Commons SDK" --no-update-nav

# Generate CLI command reference by introspecting the cyclopts app (incl. plugins)
generate-cli-docs:
    rm -f orbitra-cli*
    cd ..; uv run python -B docs/cli/gen_cli_docs.py --output-dir docs

# Post-process generated docs (alphabetical ordering + MDX character escaping)
organize-docs:
    cd ..; uv run python organizer.py docs
    cd ..; uv run python sanitize_mdx.py docs

render-docs-json:
    cd ..; uv run python update_version.py docs/docs.json

# Serve the documentation locally
serve-docs: render-docs-json generate-lake-docs generate-flows-docs generate-commons-docs generate-cli-docs organize-docs
    npx -y mint@latest dev

# Clean and rebuild docs
clean-docs:
    just generate-lake-docs
    just generate-flows-docs
    just generate-commons-docs
    just generate-cli-docs