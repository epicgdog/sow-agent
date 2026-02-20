# Agent Controller (Proof of Concept)

Standalone controller that applies **one append** to a predefined file in a target repo. SOW-compliant: config-driven, reversible (backup), and logged.

## Run

From this directory (or with `PYTHONPATH` set to it):

```bash
python main.py
```

Config is loaded from `config.json` next to this script. Target paths in config are absolute.

## Config (`config.json`)

| Key                | Description                          |
|--------------------|--------------------------------------|
| `target_repo_path` | Absolute path to the target repo     |
| `target_file`      | Path relative to repo (e.g. `README.md`) |

## Behavior

- **One change per run**: Appends a single timestamped line to the target file.
- **Reversible**: Creates a `.bak` copy of the target file before modifying (restore from `.bak` if needed).
- **Logged**: Writes to `controller.log` and prints the same to console.

## Success Criteria (SOW)

- Script runs without errors (valid config and existing target file).
- Target file is modified exactly once per execution.
- Changes are visible via `git diff` in the target repository.
