# PR Review — Issue #166: SaveData hash inconsistency for identical outputs

Branch diff vs `main` (excluding `issue/`):
- `source/lib/SaveData.py`
- `source/lib/JMSLab/tests/test_savedata.py`

No `drive/`/`datastore` folders updated (per author). No `source/derived`, `analysis`,
`figures`, or `tables` changes — scope is confined to the SaveData library and its tests.

## source/lib/SaveData.py

### Issues
No blocking issues found.

### Notes
- **Core fix is correct.** The MD5 hash is now computed *after* the rows are sorted
  ([SaveData.py:20-23](source/lib/SaveData.py#L20-L23)), so two inputs that differ only
  in row order produce the same hash. Verified empirically: reverting to the pre-fix
  ordering makes the new regression test fail, and the fixed code passes.
- **`index=False` is essential and correct** ([SaveData.py:23](source/lib/SaveData.py#L23)).
  After `sort_values`, the row index is a permutation that still differs between two
  differently-ordered inputs. Hashing with the default `index=True` would *not* fix the
  bug; `index=False` is what makes the hash depend only on the (sorted) values. Good catch.
- **Sorting was hoisted out of `SaveDf` into `SaveData`** and changed from
  `sort_values(..., inplace=True)` to an assignment (`df = df.sort_values(keys)`). This is
  cleaner (no in-place mutation of the passed frame) and keeps sort + hash adjacent so they
  can't drift apart again.
- **`GetSummaryStats` is now computed before the sort** ([SaveData.py:19](source/lib/SaveData.py#L19)).
  This is fine — `describe`/counts are order-independent, so the logged summary is unchanged.
- **Minor cleanup opportunity (non-blocking):** now that sorting moved out of `SaveDf`, its
  `keys` and `sortbykey` parameters are unused ([SaveData.py:110](source/lib/SaveData.py#L110)).
  `SaveDf` is only called once, from inside `SaveData`, so these could be dropped for clarity.
  Harmless to leave as-is.
- **`sortbykey=False` path:** hash is then computed on the column-reordered but unsorted
  frame. Consistent and sensible — if the caller opts out of sorting, the hash reflects the
  given order.
- Consistent with the R implementation referenced in the issue, which already sorts before
  hashing.

## source/lib/JMSLab/tests/test_savedata.py

### Issues
No blocking issues found.

### Notes
- **`test_hash_invariant_to_row_order`** ([test_savedata.py:144-152](source/lib/JMSLab/tests/test_savedata.py#L144-L152))
  directly tests the issue: same data in reversed row order (`df.iloc[::-1]`) must yield the
  same logged MD5 hash. Confirmed it is a genuine regression guard — it fails against the
  pre-fix code and passes against the fix.
- Reuses existing infrastructure well: the `data/data.csv` fixture, direct `SaveData` calls,
  and `temp_save/` + `shutil.rmtree` cleanup mirroring `test_logs_forward_slashes`.
- `get_manifest_hash` helper ([test_savedata.py:19-21](source/lib/JMSLab/tests/test_savedata.py#L19-L21))
  cleanly extracts the hash from the log via regex. Minor: if the pattern ever fails to match
  it raises `AttributeError` rather than a descriptive error, but that is acceptable in a test.
- Full suite passes: `python -m unittest source.lib.JMSLab.tests.test_savedata` → 18 tests OK.

## Checklist items N/A to this PR
- SConscript coverage, figure pipelines, SaveData-usage enforcement, data storage, raw
  Terms-of-Use/citations, economics sanity: not applicable — changes are confined to the
  `SaveData` library and its unit tests; no pipeline scripts, data, figures, or raw
  directories were added or modified.

## Summary

**Outputs match the issue description.** The author stated the bug was that the dataframe
hash was generated before the data were sorted/standardized, and the fix moves hash
generation to after standardization. The diff does exactly that, and the added unit test
confirms identical-output / differently-ordered inputs now hash identically.

**Top issues to address:** none blocking.
1. (Optional) Drop the now-unused `keys`/`sortbykey` parameters from `SaveDf`
   ([SaveData.py:110](source/lib/SaveData.py#L110)) for clarity.

**Economics-sanity flags:** none — library/test code only.
