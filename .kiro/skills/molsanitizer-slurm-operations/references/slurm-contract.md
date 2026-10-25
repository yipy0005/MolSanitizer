# SLURM contract

Batch mode stages each input into a folder containing shared data, byte offsets, lock files, generated defaults, and `submit_msani.sh`. Plain input can be symlinked. Compressed input is decompressed into a controlled local file when native decompressor tools are unavailable or used as a stream when available.

Array sizing is constrained by configured maximum array size and project capacity. Whole-node mode groups jobs by core count. A job must preserve nonzero status on failed chunks and must not remove evidence needed for recovery.

Review generated shell as a program. Check quoting, paths with spaces, exit status propagation, lock cleanup, scratch cleanup, task indexing, and shard merge ordering. Never infer safety from a successful script-generation call alone.
