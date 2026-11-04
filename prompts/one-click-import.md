# One-click import prompt

Copy this whole block into Claude Code or Codex with local file and terminal access.

```text
Install https://github.com/miolamio/code-animation-prompts as a skill available to the current coding assistant.

1. Download the repository to a suitable local directory. If a directory with the same name already exists, inspect its contents first and do not overwrite existing changes.
2. Read README.md, docs/INSTALL.md and skills/code-animation-prompts/SKILL.md.
3. Choose the install target for the current assistant: Codex uses ~/.agents/skills/code-animation-prompts,
   Claude Code uses ~/.claude/skills/code-animation-prompts.
   From the repository root, run python scripts/install_skill.py --target codex or --target claude.
   If you cannot determine the current assistant, ask me about the target only; do not install to both locations on your own.
4. Keep the complete skill folder when installing, including every prompt, still, HTML file, example video and license file in assets/library.
   If the target already exists, keep the existing directory and report it; do not delete or overwrite it automatically.
5. Run scripts/styles.py search ink from the installed directory to confirm styles can be found;
   then run scripts/styles.py show B3 to confirm a full prompt can be read.
6. Tell me the actual install path, how to invoke the skill, and whether I need to start a new session.
   Finally, give me one ready-to-use request for a "12-second particle-formation animation".

This task only installs the style skill. Do not automatically install video rendering dependencies, and do not change the configuration of other assistants.
```

[Back to README](../README.md)
