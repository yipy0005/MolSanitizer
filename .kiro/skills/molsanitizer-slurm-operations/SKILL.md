---
name: molsanitizer-slurm-operations
description: Review or operate MolSanitizer SLURM batch preparation, byte-offset indexing, array scripts, compressed inputs, scratch handling, locks, shard merging, and recovery safely.
compatibility: SLURM environments only; local dry-run first
---

# MolSanitizer SLURM operations

Use this skill for `msani_batch`, generated submission scripts, job sizing, recovery, or cluster failures.

## Safety boundary

Do not submit jobs, remove an existing result directory, or approve destructive cleanup without explicit user authorization. Prefer `pixi run msani_batch --test` and inspect generated files first. The MCP server never submits SLURM jobs.

## Procedure

1. Read `msani/batchmode.py` and the batch options in `msani/io/parsers.py`.
2. Confirm input path, line count, compression, `lines_per_job`, array limits, project capacity, partition, account, time, memory, and whole-node mode.
3. For plain inputs, verify the symlink and byte-offset index. For compressed inputs, verify one controlled decompression pass and the resulting `input.data` and `input.offsets`.
4. Inspect `submit_msani.sh`, `msani_defaults.yaml`, flags, scratch paths, locks, trap/exit handling, shard names, and merge ordering before submission.
5. Test one tiny staging directory locally. Only then run an authorized staging submission and retain logs and shard status.

## Verification

Use `pixi run msani_batch --test` for script/index generation. Check empty files, malformed input, compressed input, a failed task, resumption, cleanup disabled/enabled, whole-node grouping, and ordered merge behavior. Treat SLURM commands and `shutil.rmtree` as privileged operations.

## References

- Read `references/slurm-contract.md` for invariants and review points.
