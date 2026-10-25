# Validation matrix

| Change area | First check | Follow-up |
| --- | --- | --- |
| Input parsing | `test_input_readers` | compressed, CXSMILES, synthons, malformed delimiters |
| Config/CLI flags | `test_config`, `pixi run msani --help` | precedence, sanity defaults, templates |
| Chemistry orchestration | focused `test_msani` cases | golden outputs, ID expansion, invalid inputs |
| 3D writers | relevant `test_msani` cases | optional-tool matrix and fresh output directories |
| Batch indexing | batch tests or `pixi run msani_batch --test` | compressed inputs, script review, authorized staging |
| Native/build | editable import | wheel/sdist resource and console-script inspection |
| Release docs | CLI smoke tests | docs build and clean install |

Known environment gaps are evidence, not automatic failures. State exactly which check could not run and why.
