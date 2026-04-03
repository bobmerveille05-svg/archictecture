# sandbox/permissions.py
# Permission checks with allowlist approach.

import os
from pathlib import Path


ALLOWED_COMMANDS = {
    "ls",
    "dir",
    "pwd",
    "cd",
    "echo",
    "cat",
    "head",
    "tail",
    "grep",
    "find",
    "which",
    "whoami",
    "date",
    "time",
    "mkdir",
    "cp",
    "mv",
    "touch",
    "chmod",
    "stat",
    "python",
    "python3",
    "pip",
    "git",
    "curl",
    "wget",
    "sort",
    "uniq",
    "wc",
    "tr",
    "sed",
    "awk",
}

ALLOWED_PATHS = [
    "/tmp",
    "/tmp/agent",
    "/workspace",
    "/workspace/project",
]

BLOCKED_EXTENSIONS = {".exe", ".bat", ".sh", ".cmd", ".ps1"}
NETWORK_COMMANDS = {"curl", "wget"}


def normalize_path(path: str, base_dir: str | None = None) -> Path:
    """Normalize relative/absolute paths."""
    if base_dir is None:
        base_dir = os.getenv("SANDBOX_DIR", "/tmp/agent")

    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    return (Path(base_dir) / p).resolve()


def check_permission(action: str, target: str) -> bool:
    if action == "execute":
        return check_command_allowed(target)
    if action == "write":
        return check_write_allowed(target)
    if action == "read":
        return check_read_allowed(target)
    return False


def check_command_allowed(command: str) -> bool:
    dangerous_patterns = [
        "rm -rf /",
        "dd if=",
        "mkfs",
        ":(){ :|:& };:",
        "curl | bash",
        "wget | sh",
        "eval ",
        "exec ",
        "chmod 777",
        "chown",
        "> /dev/",
        "2>&1",
    ]

    lower_cmd = command.lower()
    for pattern in dangerous_patterns:
        if pattern in lower_cmd:
            return False

    import shlex

    try:
        parts = shlex.split(command)
        if not parts:
            return True
        main_cmd = parts[0]

        allow_network = os.getenv("ALLOW_NETWORK", "false").lower() == "true"
        if not allow_network and main_cmd in NETWORK_COMMANDS:
            return False

        if main_cmd in ALLOWED_COMMANDS:
            return True

        if main_cmd in ("python", "python3", "git"):
            return True

        return False
    except Exception:
        return False


def check_write_allowed(path: str) -> bool:
    try:
        full_path = normalize_path(path)
        if not any(str(full_path).startswith(allowed_dir) for allowed_dir in ALLOWED_PATHS):
            return False
        return full_path.suffix.lower() not in BLOCKED_EXTENSIONS
    except Exception:
        return False


def check_read_allowed(path: str) -> bool:
    try:
        if not path:
            return True

        full_path = normalize_path(path)
        if not any(str(full_path).startswith(allowed_dir) for allowed_dir in ALLOWED_PATHS):
            return False

        sensitive_patterns = ["/etc/passwd", "/etc/shadow", "~/.ssh", "/root", ".env"]
        return not any(pattern in str(full_path) for pattern in sensitive_patterns)
    except Exception:
        return False
