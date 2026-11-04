# Install for Claude Code / Codex

This repository targets Claude Code and Codex with local file and terminal access. Download the full repository first (the library is about 75 MiB including the sample videos, plus the README images). What gets installed is the entire `skills/code-animation-prompts/` directory.

## Hand it to your assistant in one go

[Copy the one-click import prompt](../prompts/one-click-import.md). The assistant downloads the repository, reads the instructions, chooses the install location for the current tool and verifies style lookup.

## Python install script

Requires Python 3.10+ and no third-party packages. From the repository root, run:

```bash
python scripts/install_skill.py --target codex
python scripts/install_skill.py --target claude
```

Pick one of these. `--target both` installs to both locations. `--dry-run` only shows the paths and writes no files.

| Tool | User-level directory | Project-level directory |
|---|---|---|
| Codex | `~/.agents/skills/code-animation-prompts/` | `<project>/.agents/skills/code-animation-prompts/` |
| Claude Code | `~/.claude/skills/code-animation-prompts/` | `<project>/.claude/skills/code-animation-prompts/` |

`~` means your home directory; on Windows it is usually `C:\Users\<username>`. These paths follow the [official OpenAI skills docs](https://learn.chatgpt.com/docs/build-skills) and the [official Claude Code skills docs](https://code.claude.com/docs/en/skills).

To install into a specific project:

```bash
python scripts/install_skill.py --target codex --scope project --project-dir "your/project/path"
python scripts/install_skill.py --target claude --scope project --project-dir "your/project/path"
```

Do not install the same skill at both the user level and the project level for one assistant, or you may see several entries with the same name.

## Without Python

Manually copy the whole `skills/code-animation-prompts/` directory from the repository to a location in the table. You should end up with:

```text
<install-location>/code-animation-prompts/SKILL.md
<install-location>/code-animation-prompts/assets/library/style-picker.html
<install-location>/code-animation-prompts/references/catalog.json
```

Copying only `SKILL.md` loses the style library. Do not change the relative positions of files inside `assets/library/`.

## Verify the install

Replace `<skill-dir>` with the real install path:

```bash
python "<skill-dir>/scripts/styles.py" search ink
python "<skill-dir>/scripts/styles.py" show B3
```

After starting a new session, type `$code-animation-prompts` in Codex or `/code-animation-prompts` in Claude Code. You can also just say "use code-animation-prompts to make an animation". If the new skill doesn't appear in the current session, restart the session; account or admin settings may affect skill discovery.

## Update

The install script does not overwrite an existing directory. Before updating, save your own changes and back up the old skill directory outside the skill scan directories; then pull the repository and run the install command again. Do not leave a backup containing `SKILL.md` under `.agents/skills/` or `.claude/skills/`, as it may still get scanned.

To update the library index in the repository and check its integrity:

```bash
python scripts/build_catalog.py
python scripts/validate_repo.py
```

## Optional: video export

Installing the skill does not install a browser or FFmpeg. When you actually need to export video, set up the dependencies using the [rendering notes](../skills/code-animation-prompts/references/rendering.md).

[Back to README](../README.md)
