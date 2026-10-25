---
name: molsanitizer-cli-data-contracts
description: Work on MolSanitizer CLI behavior, SMILES/CXSMILES/synthon input, compressed files, configuration precedence, output naming, error files, IDs, and user-facing documentation.
compatibility: MolSanitizer CLI and Python API
---

# MolSanitizer CLI and data contracts

Use this skill when changing parsers, CLI flags, config behavior, file formats, output paths, logs, or command documentation.

## Procedure

1. Read `msani/io/parsers.py`, `msani/io/readers.py`, and the relevant `msani/cli.py` path before editing.
2. Preserve the input contract: headerless SMILES plus ID, automatic gzip/bzip2/xz detection, consistent separators, tab-separated CXSMILES, quoted CXSMILES for whitespace-separated input, and three-column synthon mode.
3. Preserve precedence: bundled defaults, selected/user config, `MSANI_CONFIG`, YAML file values, then explicit CLI flags. Check `Sanitycheck` for derived defaults.
4. Keep output behavior compatible: clean files are headerless, rejected records contain filter reasons where supported, metal failures use the metal-error file, and 3D writers use format-specific directories.
5. Treat IDs as data. Preserve input order, apply documented variant suffixes, and avoid silent collisions. Document rerun and stale-output behavior when relevant.
6. Validate malformed delimiters before molecular processing and keep errors tied to input record offsets.

## Verification

- Run `pixi run python -m unittest test.test_input_readers` and `pixi run python -m unittest test.test_config`.
- Exercise `pixi run msani --help`, `pixi run msani --version`, a two-row plain file, tab/CXSMILES input, and one compressed input in a temporary directory.
- Check generated files and contents, not only stdout or exit code.
- Never add an arbitrary shell escape or silently submit batch jobs from a local CLI path.

## References

- Read `references/cli-contract.md` for file, config, and output details.
