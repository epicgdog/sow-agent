# main.py
"""Controller script: appends a line to a target file (SOW-compliant, reversible)."""
import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths relative to this script's directory (run from anywhere)
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
LOG_PATH = SCRIPT_DIR / "controller.log"

# Load config
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

TARGET_REPO = Path(config["target_repo_path"])
TARGET_FILE = TARGET_REPO / config["target_file"]


def log(message: str) -> None:
    """Write to log file and console (SOW: log or console output)."""
    line = f"{datetime.now().isoformat()} {message}\n"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
    print(message.strip())


def apply_change() -> None:
    """Append one line to the target file. Backup created for reversibility."""
    if not TARGET_FILE.exists():
        log("Target file does not exist.")
        return

    timestamp = datetime.now().isoformat()
    new_line = f"\n# Updated by agent-controller at {timestamp}\n"

    # Reversible: backup before modify (no destructive operations)
    backup_path = TARGET_FILE.with_suffix(TARGET_FILE.suffix + ".bak")
    shutil.copy2(TARGET_FILE, backup_path)
    log(f"Backup created: {backup_path}")

    with open(TARGET_FILE, "a", encoding="utf-8") as f:
        f.write(new_line)

    log(f"Change applied to {TARGET_FILE} (append only, once per execution)")


if __name__ == "__main__":
    apply_change()