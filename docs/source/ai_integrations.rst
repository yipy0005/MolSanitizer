AI skills and MCP integration
=============================

This page contains detailed integration and security notes. Start with the
:doc:`ai_guide` for the shortest setup and usage path.

Install Pixi environments
-------------------------

Install the Pixi environment from the repository root:

.. code-block:: bash

   pixi install

The default environment contains MolSanitizer's runtime and native build
dependencies. The ``mcp`` environment adds the optional MCP SDK. Run all
Python commands through Pixi, for example ``pixi run python ...`` or the
named tasks below.

Kiro uses the MCP environment directly, so no global Python installation is
needed.

Kiro configuration
------------------

The repository includes ``.kiro/mcp.json.example`` because Kiro settings are
local workspace state. Copy it to ``.kiro/settings/mcp.json`` (or use Kiro's
MCP configuration command), then open the workspace in a trusted Kiro session
and check the Kiro MCP output log for a connected ``molsanitizer`` server. The
configuration uses stdio, keeps all tools behind approval prompts, and
restricts the server root to the workspace's current directory. The matching
``.kiro/sandbox.json.example`` can be copied to ``.kiro/settings/sandbox.json``
on Kiro versions that support local MCP sandboxing.

The repository also includes the ``molsanitizer-engineer`` custom agent at
``.kiro/agents/molsanitizer-engineer.json``. Select it from Kiro's agent picker
or invoke it as ``/molsanitizer-engineer``. It explicitly loads all workspace
skills, starts the repository MCP server through Pixi, keeps MCP calls behind
approval, and asks before high-impact shell operations. The agent does not
pin a model, so it inherits the model selected in Kiro.

The server exposes bounded tools:

* ``project_info`` reports versions, optional modules, capabilities, and limits.
* ``validate_smiles`` parses up to 100 SMILES and returns canonical forms and
  validity details.
* ``prepare_smiles`` runs the public ``Msani`` API in memory for up to 100
  records. It does not write output files.
* ``inspect_input_file`` uses MolSanitizer's real reader and accepts only files
  below ``MSANI_MCP_ROOT``.
* ``run_tests`` runs only named unittest suites. It does not accept arbitrary
  shell commands and never submits SLURM jobs.

Use ``/mcp`` to inspect server status and ``/tools`` to inspect tool schemas.
Review parameters before allowing a call. Keep ``autoApprove`` empty unless a
team has reviewed a narrower policy.

Evaluate the integration
------------------------

Run the static, agent, and core smoke evaluator from the repository root:

.. code-block:: bash

   pixi run evaluate-ai

For an MCP SDK and agent-server startup check, install the MCP environment first:

.. code-block:: bash

   pixi run -e mcp evaluate-ai-required
   pixi run -e mcp test-mcp

Then verify in Kiro with a trusted workspace: select ``molsanitizer-engineer``
from the agent picker, confirm it appears as ``/molsanitizer-engineer``, ask it
for a read-only project status, and verify it reports Pixi commands and uses
explicit skill resources. Test a representative chemistry request, a CLI/data
contract request, and a nearby request that should not trigger unrelated
skills. Inspect the MCP approval prompt and confirm that destructive SLURM,
Git, and deletion commands are denied or require approval. Use ``pixi run
msani_batch --test`` for batch work; the MCP layer intentionally does not expose
job submission or arbitrary command execution.

Security and scientific limits
------------------------------

The MCP server is intended for a trusted local workspace. It validates paths,
limits input sizes, uses an allow-list for test suites, avoids file writes for
chemistry tools, and sends diagnostics to stderr so stdio protocol traffic is
not corrupted. It does not sandbox RDKit itself or replace scientific review.
Report MolSanitizer, Python, RDKit, rule-library, options, and optional-tool
versions with any result used as scientific evidence.
