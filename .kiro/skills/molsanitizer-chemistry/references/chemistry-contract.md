# Chemistry contract

## Public orchestration

`msani.api.Msani` accepts a pandas DataFrame with `smiles` and `ids` columns and returns a new processed DataFrame. It owns the main transformation order and supports context-managed worker reuse. Instances are not thread-safe.

## Behavior that must remain explicit

- `metal`: `strict` keeps one plausible coordination structure, `soft` can emit variants, and `off` preserves dissociated records.
- `standardize`: uses the database-oriented standardization path and returns before the later transformations.
- `removesalts`: strips small fragments before later filtering.
- `neutralize`: changes charge state and is often enabled by CLI sanity checks when salt removal, tautomerization, or protonation is requested.
- `tautomers` and `extended_tautomers`: can expand IDs and use packaged rule files.
- `protonation`: uses pH and pH range and can expand IDs.
- `stereoisomers`: can expand records and is enabled by default for some 3D CLI paths unless explicitly disabled.
- `pains` and unwanted SMARTS: filter records and may append reasons to a rejected file in CLI workflows.

## Evidence requirements

For a chemistry change, record input structures, active options, Python/RDKit/MolSanitizer versions, expected record count, canonical SMILES or an accepted structure comparison, ID mapping, and rejection/error behavior. Use fresh output directories when comparing reruns because old 3D files can remain.
