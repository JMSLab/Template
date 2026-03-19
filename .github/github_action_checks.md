# GitHub Actions Checks

## Adding a new check

1. Add a step to `checks.yml` with a unique `id` and `display` (e.g. `id: check_newlines`, `display: Newlines`)
2. Add `{"name": "Newlines"}` (i.e. matching `display`) to `checks.json`

The order of entries in `checks.json` controls the row order in the results table.
