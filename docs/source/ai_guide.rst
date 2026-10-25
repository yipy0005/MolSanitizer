AI setup and usage guide
=========================

This guide shows how to set up MolSanitizer's Kiro skills, custom agent, and
local MCP server. Follow the setup once, then use the agent or individual
skills from Kiro chat.

What you get
------------

The repository provides:

* **Skills**: focused instructions for chemistry, CLI/data contracts, native
  builds, SLURM operations, and regression validation.
* **Agent**: ``molsanitizer-engineer`` coordinates the skills and follows the
  repository's Pixi, testing, chemistry, packaging, and safety rules.
* **MCP server**: bounded tools for project information, SMILES validation and
  preparation, input-file inspection, and allow-listed tests.

The MCP server does not submit SLURM jobs, run arbitrary shell commands, or
write chemistry output files.

Before you start
----------------

You need:

* Kiro IDE installed.
* Pixi installed and available as ``pixi`` in a terminal.
* This repository cloned locally.
* A trusted Kiro workspace. Kiro does not load workspace skills, agents, or MCP
  configuration from an untrusted workspace.

Set up the repository
---------------------

Open a terminal at the repository root and install the Pixi environments:

.. code-block:: bash

   pixi install

This creates the default environment for MolSanitizer and the ``mcp``
environment for the MCP SDK. Pixi owns the Python dependencies and all Python
commands in this repository should run through Pixi.

Run the built-in integration check:

.. code-block:: bash

   pixi run evaluate-ai

A successful check reports five skills, one agent, valid MCP configuration,
and successful core smoke checks.

Configure MCP in Kiro
---------------------

Kiro workspace settings are local configuration. Copy the included MCP
configuration template into the Kiro settings directory:

.. code-block:: bash

   mkdir -p .kiro/settings
   cp .kiro/mcp.json.example .kiro/settings/mcp.json

For Kiro versions that support local MCP sandboxing, also copy:

.. code-block:: bash

   cp .kiro/sandbox.json.example .kiro/settings/sandbox.json

The MCP template starts the server through Pixi:

.. code-block:: text

   pixi run -e mcp python -m msani.mcp.server

In Kiro:

#. Trust the workspace if Kiro asks for permission.
#. Reload the MCP configuration or restart the Kiro session.
#. Open the MCP panel and confirm that ``molsanitizer`` is connected.
#. Open the MCP output log if the server does not connect.
#. Use ``/tools`` to inspect the available MCP tools.

Run the required MCP check from the repository root if the server does not
connect:

.. code-block:: bash

   pixi run -e mcp evaluate-ai-required
   pixi run -e mcp test-mcp

Set up the custom agent
-----------------------

The agent is already in:

.. code-block:: text

   .kiro/agents/molsanitizer-engineer.json

In Kiro, select **molsanitizer-engineer** from the agent picker. You can also
start it from chat with:

.. code-block:: text

   /molsanitizer-engineer

The agent loads the repository skills, starts the Pixi-backed MCP server, and
uses approval gates for MCP and high-impact operations. It does not pin a model,
so it uses the model selected in Kiro.

Use the skills
--------------

Skills activate in two ways.

Use the slash menu
~~~~~~~~~~~~~~~~~~

Type ``/`` in Kiro chat and select the skill you want. The available skills are:

.. list-table::
   :header-rows: 1

   * - Skill
     - Use it for
   * - ``molsanitizer-chemistry``
     - Sanitization, salts, metals, filters, tautomers, protonation,
       stereoisomers, and 3D preparation.
   * - ``molsanitizer-cli-data-contracts``
     - SMILES/CXSMILES/synthon input, compression, config precedence, IDs,
       outputs, and CLI documentation.
   * - ``molsanitizer-native-build-release``
     - CMake, pybind11, RDKit ABI, wheels, sdists, and optional dependencies.
   * - ``molsanitizer-slurm-operations``
     - Byte-offset indexing, generated SLURM scripts, scratch, locks, shards,
       recovery, and dry runs.
   * - ``molsanitizer-regression-validation``
     - Focused tests, golden data, CLI smoke tests, optional-dependency checks,
       and reproducibility evidence.

Examples:

.. code-block:: text

   /molsanitizer-chemistry Explain what --removesalts and --neutralize do in this workflow.
   /molsanitizer-cli-data-contracts Review this parser change for compatibility with CXSMILES input.
   /molsanitizer-regression-validation Plan the smallest Pixi test for this change.

Use natural language
~~~~~~~~~~~~~~~~~~~~

Kiro can activate a matching skill automatically. Be specific about the work:

.. code-block:: text

   Review the ID suffix behavior when tautomerization creates duplicate records.
   Check whether this change preserves compressed CXSMILES input behavior.
   Diagnose a wheel that cannot find the RDKit native extension.
   Review this generated SLURM script without submitting it.

Use the agent
-------------

Ask the agent for a concrete task and include the relevant path or behavior.
It will inspect the repository, select the appropriate skill, use Pixi commands,
and report evidence.

Safe examples:

.. code-block:: text

   Review the current git diff for chemistry and CLI regressions. Do not edit files.
   Use the MCP tools to validate these three SMILES and explain the active options.
   Add a focused regression test for the CXSMILES delimiter behavior, then run it with Pixi.
   Inspect the native packaging configuration and check whether Data files enter the wheel.
   Prepare a dry-run review of this SLURM change. Do not submit jobs or delete outputs.

The agent asks before MCP calls unless Kiro's permission policy already covers
the action. It must not perform destructive operations without explicit
authorization.

Use the MCP tools
-----------------

The agent can call the MCP server when a bounded repository or chemistry check
is useful. The tools are:

* ``project_info``: reports Python, RDKit, MolSanitizer, optional-module, and
  request-limit information.
* ``validate_smiles``: validates up to 100 SMILES and returns canonical forms,
  validity, and heavy-atom counts.
* ``prepare_smiles``: prepares up to 100 in-memory SMILES through the public
  ``Msani`` API without writing files.
* ``inspect_input_file``: inspects a repository-local input file with the real
  MolSanitizer reader. Paths outside the configured MCP root are rejected.
* ``run_tests``: runs only named unittest suites; it does not accept arbitrary
  commands.

Example request:

.. code-block:: text

   Use validate_smiles on CCO, c1ccccc1, and an invalid example. Return the
   canonical SMILES and explain which records were rejected.

The MCP server is intentionally small. Use the normal Pixi CLI when you need
large files, 3D output, SLURM submission, or a persistent output directory.

Verify your setup
-----------------

Run these checks from the repository root:

.. code-block:: bash

   pixi run evaluate-ai
   pixi run -e mcp evaluate-ai-required
   pixi run -e mcp test-mcp
   pixi run test

Then verify the Kiro side:

* The skills appear in the ``/`` slash menu.
* ``molsanitizer-engineer`` appears in the agent picker.
* ``/tools`` lists the MolSanitizer MCP tools.
* A safe MCP call shows an approval prompt.
* A request to submit SLURM work or delete outputs is blocked or asks for
  approval.

Troubleshooting
---------------

**Skills or agent do not appear**

Trust the workspace, start a new Kiro session, and confirm that the files exist
under ``.kiro/skills/`` and ``.kiro/agents/``. The skill folder name must match
the ``name`` in ``SKILL.md``.

**MCP is disconnected**

Run ``pixi install`` and then ``pixi run -e mcp test-mcp``. Confirm that
``.kiro/settings/mcp.json`` was copied from the current template. Check Kiro's
MCP output log for startup errors.

**The MCP server starts but a chemistry call fails**

Run ``pixi run -e mcp evaluate-ai-required``. Check the reported Python, RDKit,
and MolSanitizer versions. Optional OpenEye, Meeko, Open Babel, CORINA, and
SLURM capabilities require their own explicitly provisioned environments.

**A test is skipped**

Treat the skip as an environment report. The full suite can skip optional
features when their external dependency or licence is unavailable. Do not
rewrite golden output to remove a skip without a documented behavior decision.

More detail
-----------

For the detailed integration and security notes, read :doc:`ai_integrations`.
For chemistry and validation behavior, use the repository skills and the
references inside each skill directory.
