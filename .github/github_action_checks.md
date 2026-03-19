# GitHub Actions Checks

## Adding a new check

1. Add a step to `workflows/checks.yml` with a unique `id` and `display` (e.g. `id: check_newlines`, `display: Newlines`), and a `script` pointing to your script in `checks/`
2. Add `{"name": "Newlines", "command": "/run-actions-newlines"}` (i.e. matching `display`) to `checks/checks.json`

The order of entries in `checks.json` controls the row order in the results table.
