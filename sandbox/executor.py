# sandbox/executor.py
# Execution securisee des commandes shell

import subprocess
import os
import shlex
from sandbox.permissions import check_permission, ALLOWED_COMMANDS


SANDBOX_DIR = os.getenv("SANDBOX_DIR", "/tmp/agent")
TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "30"))
MAX_OUTPUT_CHARS = int(os.getenv("MAX_OUTPUT_CHARS", "4000"))
NETWORK_COMMAND_HINTS = ("curl", "wget")


def ensure_sandbox_dir():
    """Cree le repertoire sandbox si inexistant."""
    os.makedirs(SANDBOX_DIR, exist_ok=True)


def execute_command_safe(command: str, use_shell: bool = False) -> dict:
    """
    Execute une commande de maniere securisee.
    
    Args:
        command: La commande a executer
        use_shell: Si True, utilise shell=True (moins securise)
                   Si False, parse et execute sans shell (plus securise)
    
    Returns:
        dict: {success, output, error}
    """
    ensure_sandbox_dir()
    
    # Verifier permission
    if not check_permission("execute", command):
        return {
            "success": False,
            "output": "",
            "error": f"BLOQUE : permission refusee pour -> {command}",
        }

    allow_network = os.getenv("ALLOW_NETWORK", "false").lower() == "true"
    if not allow_network:
        lowered = command.lower()
        if any(hint in lowered for hint in NETWORK_COMMAND_HINTS):
            return {
                "success": False,
                "output": "",
                "error": "BLOQUE : commandes reseau interdites (ALLOW_NETWORK=false)",
            }
    
    try:
        if use_shell:
            # Mode shell (moins securise mais plus flexible)
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=TOOL_TIMEOUT,
                cwd=SANDBOX_DIR,
            )
        else:
            # Mode sans shell (plus securise)
            parts = shlex.split(command)
            if not parts:
                return {"success": False, "output": "", "error": "Commande vide"}
            
            cmd = parts[0]
            # Verifier commande dans allowlist
            if cmd not in ALLOWED_COMMANDS:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Commande '{cmd}' non autorisee (allowlist)",
                }
            
            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=TOOL_TIMEOUT,
                cwd=SANDBOX_DIR,
            )
        
        output = result.stdout or result.stderr or "(aucun output)"
        output = output[:MAX_OUTPUT_CHARS]  # Tronquer pour eviter overflow
        
        return {
            "success": True,
            "output": output,
            "error": None,
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": f"Timeout ({TOOL_TIMEOUT}s depasse)",
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e)[:500],
        }


# Alias pour compatibilite
def execute_command(command: str) -> str:
    """Execution simple (retourne string pour compatibilite)."""
    result = execute_command_safe(command, use_shell=False)
    if result["success"]:
        return result["output"]
    return f"ERREUR : {result['error']}"
