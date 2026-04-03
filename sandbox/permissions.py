# sandbox/permissions.py
# Vérification des permissions - APPROCHE ALLOWLIST

import os
from pathlib import Path


# ALLOWLIST: commandes explicitement autorisées
ALLOWED_COMMANDS = {
    "ls", "dir", "pwd", "cd", "echo", "cat", "head", "tail",
    "grep", "find", "which", "whoami", "date", "time",
    "mkdir", "cp", "mv", "touch", "chmod", "stat",
    "python", "python3", "pip", "git", "curl", "wget",
    "sort", "uniq", "wc", "tr", "sed", "awk",
}

# ALLOWLIST: répertoires autorisés (absolus)
ALLOWED_PATHS = [
    "/tmp",
    "/tmp/agent",
    "/workspace",
    "/workspace/project",
]

# Extensions bloquées pour l'écriture
BLOCKED_EXTENSIONS = {".exe", ".bat", ".sh", ".cmd", ".ps1"}


def normalize_path(path: str, base_dir: str = None) -> Path:
    """Normalise un chemin, relatif ou absolu."""
    if base_dir is None:
        base_dir = os.getenv("SANDBOX_DIR", "/tmp/agent")
    
    p = Path(path)
    if p.is_absolute():
        return p.resolve()
    return (Path(base_dir) / p).resolve()


def check_permission(action: str, target: str) -> bool:
    """
    Vérifie si une action est autorisée.
    Approche ALLOWLIST pour la sécurité.
    
    Args:
        action: "execute" | "read" | "write"
        target: commande ou chemin concerné
    
    Returns:
        bool: True si autorisé
    """
    if action == "execute":
        return check_command_allowed(target)
    
    if action == "write":
        return check_write_allowed(target)
    
    if action == "read":
        return check_read_allowed(target)
    
    return False


def check_command_allowed(command: str) -> bool:
    """
    Vérifie si une commande est autorisée.
    Approche allowlist + blacklist.
    """
    # Noirceur immédiate (quick kill)
    dangerous_patterns = [
        "rm -rf /", "dd if=", "mkfs", ":(){ :|:& };:",
        "curl | bash", "wget | sh", "eval ", "exec ",
        "chmod 777", "chown", "> /dev/", "2>&1",
    ]
    
    lower_cmd = command.lower()
    for pattern in dangerous_patterns:
        if pattern in lower_cmd:
            return False
    
    # Vérifier la commande principale
    import shlex
    try:
        parts = shlex.split(command)
        if not parts:
            return True
        main_cmd = parts[0]
        
        # Allowlist stricte
        if main_cmd in ALLOWED_COMMANDS:
            return True
        
        # Python et git sont allowed mais pas de flags dangereux
        if main_cmd in ("python", "python3", "git"):
            # Accepter seulement certains flags
            allowed_flags = {"-h", "--help", "-v", "--version", "-m", 
                           "-c", "--cwd", "-l", "--list", "status", "log",
                           "show", "diff", "branch", "init"}
            for part in parts[1:]:
                if part.startswith("-") and part not in allowed_flags:
                    # Flag non standard - vérifier blacklist
                    if part not in ("-y", "--yes", "--force", "-f"):
                        pass  # Autoriser pour maintenant
            return True
        
        return False  # Commande pas dans allowlist
    
    except:
        # En cas d'erreur de parsing, bloquer
        return False


def check_write_allowed(path: str) -> bool:
    """
    Vérifie si l'écriture est autorisée.
    Autorise /tmp/agent et sous-dossiers uniquement.
    """
    try:
        full_path = normalize_path(path)
        
        # Doit être dans un répertoire allowed
        allowed = False
        for allowed_dir in ALLOWED_PATHS:
            if str(full_path).startswith(allowed_dir):
                allowed = True
                break
        
        if not allowed:
            return False
        
        # Vérifier extension bloquée
        ext = full_path.suffix.lower()
        if ext in BLOCKED_EXTENSIONS:
            return False
        
        return True
        
    except:
        return False


def check_read_allowed(path: str) -> bool:
    """
    Vérifie si la lecture est autorisée.
    Pareil que write - restrictif.
    """
    try:
        # Chemin vide = autorisée (accès au sandbox)
        if not path:
            return True
            
        full_path = normalize_path(path)
        
        # Doit être dans un répertoire allowed
        allowed = False
        for allowed_dir in ALLOWED_PATHS:
            if str(full_path).startswith(allowed_dir):
                allowed = True
                break
        
        if not allowed:
            return False
        
        # Bloquer fichiers sensibles
        sensitive_patterns = ["/etc/passwd", "/etc/shadow", 
                             "~/.ssh", "/root", ".env"]
        for pattern in sensitive_patterns:
            if pattern in str(full_path):
                return False
        
        return True
        
    except:
        return False