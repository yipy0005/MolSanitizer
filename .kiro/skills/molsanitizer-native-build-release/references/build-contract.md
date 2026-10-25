# Build and release contract

`pyproject.toml` uses scikit-build-core and pybind11, requires CMake >=3.20, packages `msani`, and excludes native sources from binary wheels. The package requires Python >=3.10,<3.15 and RDKit >=2025.3.1.

Core runtime dependencies are pandas, numpy, RDKit, pyaml, and platformdirs. Optional extras cover OpenEye and PDBQT/Meeko. Open Babel and CORINA are external tools.

A release check must cover:

- editable import and native extension loading;
- unittest discovery;
- wheel and sdist presence of data resources;
- console scripts `msani`, `msani_batch`, `strain`, `m_ionizer`, `m_tautomerizer`, and `gen3d`;
- optional feature diagnostics;
- license files and platform-specific library placement.
