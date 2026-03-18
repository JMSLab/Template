# GitHub Actions Checks

## Adding a new check

1. Add a step to `checks.yml` with `id: check_<name>`
2. Add `CHECK_<NAME>_OUTCOME` and `CHECK_<NAME>_TIME` env vars to the `Post results` step in `checks.yml`
3. Add `("Display Name", "check_<name>")` to `CHECKS` in `post_check_results.py`
