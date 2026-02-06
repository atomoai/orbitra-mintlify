# Generate API documentation for orbitra-lake
generate-lake-docs:
    rm -rf orbitra-lake*
    cd ..; uv run mdxify orbitra.lake --root-module orbitra.lake --output-dir docs --anchor-name "Lake SDK" --no-update-nav

# Generate API documentation for orbitra-flows 
generate-flows-docs:
    rm -rf orbitra-flows*
    cd ..; uv run mdxify orbitra.flows --root-module orbitra.flows --output-dir docs --anchor-name "Flows SDK" --no-update-nav

# Generate API documentation for orbitra-commons
generate-commons-docs:
    rm -rf orbitra-commons*
    cd ..; uv run mdxify orbitra.commons --root-module orbitra.commons --output-dir docs --anchor-name "Commons SDK" --no-update-nav
    cd ..; uv run mdxify orbitra.commons.auth --root-module orbitra.commons.auth --output-dir docs --anchor-name "Commons SDK" --no-update-nav 

# Post-process generated docs (e.g., alphabetical function ordering)
organize-docs:
    cd ..; uv run python organizer.py docs

render-docs-json:
    cd ..; uv run python update_version.py docs/docs.json

# Serve the documentation locally
serve-docs: render-docs-json generate-lake-docs generate-flows-docs generate-commons-docs organize-docs
    npx mint@latest dev

# Clean and rebuild docs
clean-docs:
    just generate-lake-docs
    just generate-flows-docs
    just generate-commons-docs