# observability/logger.py
# Journalisation de chaque action de l'agent

import json
import logging
from datetime import datetime
from pathlib import Path
import os

LOGS_DIR = Path(os.getenv("LOGS_DIR", "logs"))
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOGS_DIR / "agent.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)


def log_action(node: str, data: dict):
    """
    Enregistre chaque action de l'agent.
    Format lisible + JSON pour parsing futur.
    """
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "node": node,
        "data": data,
    }
    logging.info(json.dumps(entry, ensure_ascii=False))