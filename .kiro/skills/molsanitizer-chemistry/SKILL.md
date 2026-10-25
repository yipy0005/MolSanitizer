---
name: molsanitizer-chemistry
description: Design, review, or explain MolSanitizer molecule preparation with RDKit, including sanitization, salts, metal complexes, standardization, filters, tautomerization, protonation, stereoisomers, and 3D preparation.
compatibility: Python 3.10-3.14, RDKit, pandas, packaged MolSanitizer data files
---

# MolSanitizer chemistry workflow

Use this skill for chemistry behavior, rule changes, molecule-preparation questions, or interpretation of clean/rejected output.

## Workflow

1. Inspect the requested transformation and identify whether it runs in `msani.api.Msani`, a lower-level transformer, or conformer generation.
2. Preserve the pipeline order in `msani/api.py`: parse/remove invalid SMILES, reconnect metal complexes when enabled, standardize or strip salts, apply descriptor and substructure filters, neutralize, enumerate tautomers, filter PAINS/unwanted patterns, protonate, and enumerate stereoisomers.
3. Check interactions before changing behavior. `standardize` intentionally returns after standardization. CLI sanity checks can enable neutralization, protonation, tautomerization, or stereoisomer enumeration implicitly.
4. Treat files under `msani/Data/` as versioned scientific inputs. Do not edit a rule library or expected chemistry without explaining the scientific change and updating focused regression evidence.
5. Keep outputs deterministic where the existing API promises determinism. Preserve IDs, ordering, duplicate handling, random seeds, and variant suffix rules.
6. Separate chemical validity from policy choices. Report the active RDKit version, rule-library choice, pH, enumeration limits, and optional dependencies.

## Safe verification

- Start with `validate_smiles` through the MolSanitizer MCP or a small `Msani` DataFrame.
- Use focused tests before the full suite: `pixi run python -m unittest test.test_input_readers` and the relevant cases in `test.test_msani`.
- Compare canonical structures, IDs, counts, rejection reasons, and ordering. Do not accept a green process exit as proof that chemistry is correct.
- For 3D work, explicitly check the embedding method and whether Meeko, Open Babel, CORINA, or OpenEye are installed. Never imply OEB support without a valid OpenEye environment.

## References

- Read `references/chemistry-contract.md` for the pipeline contract and edge cases.
