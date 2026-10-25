---
name: molsanitizer-native-build-release
description: Build, package, release, or diagnose MolSanitizer's CMake, pybind11, scikit-build-core, RDKit ABI, wheel, sdist, and optional dependency behavior.
compatibility: CMake >=3.20, scikit-build-core, pybind11, Python 3.10-3.14
---

# Native build and release

Use this skill for C++ extensions, CMake, editable installs, wheels, sdists, release CI, package resources, or platform-specific failures.

## Procedure

1. Read `pyproject.toml`, `CMakeLists.txt`, `cmake/MSANINative.cmake`, and the affected native subtree. Follow the existing scikit-build-core component layout.
2. Keep the RDKit C++ SDK, Python RDKit package, compiler, and native extension ABI aligned. Diagnose version/linkage mismatches before changing code.
3. Preserve package resources. Verify every required `msani/Data/` file is present in the sdist and wheel and that native libraries land inside the package.
4. Keep optional capabilities optional. PDBQT, OpenEye, Open Babel, CORINA, and SLURM must fail with clear, scoped diagnostics rather than breaking core import or basic 2D preparation.
5. Avoid changing published metadata, package names, or entry points without checking CI and installation documentation.

## Verification

- Build an editable install and import `msani`, the stereoisomer extension, and conformer modules.
- Run `pixi run python -m unittest discover -s test` in the supported environment.
- Build an sdist and wheel, inspect their contents, and verify `msani/Data/` and console scripts.
- Exercise core features without optional dependencies, then separately test each optional feature in its licensed/tool-enabled environment.
- Record Python, RDKit, compiler, CMake, and package versions in failure reports.

## References

- Read `references/build-contract.md` for packaging boundaries and release checks.
