---
name: molsanitizer-regression-validation
description: Plan and evaluate MolSanitizer changes with focused unittest coverage, golden chemistry outputs, CLI smoke tests, optional-dependency matrices, package inspection, and reproducibility evidence.
compatibility: unittest-based project with RDKit and native extensions
---

# Regression and release validation

Use this skill when evaluating a code change, writing regression tests, investigating a failed build, or deciding whether a chemistry/output change is acceptable.

## Evaluation order

1. Read the changed code and identify the user-visible contract.
2. Run the smallest focused test that exercises the contract.
3. Run CLI/API smoke checks in a temporary directory with tiny inputs.
4. Run the relevant golden-data test, then the full suite when the environment supports it.
5. Inspect outputs structurally: counts, IDs, ordering, canonical SMILES, rejection/error files, and package contents.
6. Report environment gaps separately from product failures. Optional OpenEye, Meeko, Open Babel, CORINA, SLURM, and native ABI checks need explicit environments.

## Evidence standard

A result is reproducible only when it records MolSanitizer, Python, RDKit, rule-library, platform, random-seed, and option values. A process exit code is necessary but not sufficient. Do not rewrite golden outputs to make a test pass without a documented scientific or contract decision.

## Commands

- Focused readers: `pixi run python -m unittest test.test_input_readers`
- Config: `pixi run python -m unittest test.test_config`
- Main behavior: `pixi run python -m unittest test.test_msani`
- Full suite: `pixi run test`
- Integration evaluator: `pixi run evaluate-ai`

## References

- Read `references/validation-matrix.md` for the repository test map.
