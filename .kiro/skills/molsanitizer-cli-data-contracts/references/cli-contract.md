# CLI contract

## Inputs

Local file mode accepts one or more files or an input-list file. The reader detects gzip, bzip2, and xz from content signatures. The first nonblank record determines the separator unless `--extended` forces tabs. Synthon mode reads `smiles`, `ids`, and `longname`.

Direct `--smiles` input uses generated IDs unless RDKit provides a name property. File and direct-SMILES modes are mutually exclusive.

## Configuration

`pixi run msani config init|use|path|show|reset-path` manages persistent defaults. Explicit command-line values override config values. `MSANI_CONFIG` can select a one-off config. Batch jobs snapshot defaults into `msani_defaults.yaml`.

## Outputs

Default file mode writes `<stem>_clean<suffix>` and `<stem>_rejected<suffix>`. Metal preparation failures use `<prefix>_metal_error.smi` or the explicit `--metal_error_file`. 3D output uses `sdf/`, `mol2/`, `pdbqt/`, `db2/`, or `oeb/` directories. Variant IDs use documented `_N` and stereoisomer suffix conventions.

A rerun can leave stale molecule files in 3D output directories. Use a fresh directory or clean only the exact output scope under review.
