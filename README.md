# Agent Local V2 — Specification Corrigee

## Architecture V2 (6 noeuds reels)

```
inject_memory → plan → choose_action → execute_tool → record_result → decide
                                                                     ↑         │
                                                                     └─────────┘
```

**PRINCIPE: Runtime-centric, pas LLM-centric**

- Le runtime est source de verite, pas le LLM
- ToolResult structure (verite)
- Allowlist security (capacites explicites)

## Structure V2 Complete

```
agent/
├── core/
│   ├── graph.py           # Boucle 6 noeuds
│   ├── state.py           # AgentState V2
│   ├── nodes.py           # 5 noeuds operativos
│   ├── schemas.py         # ToolCallProposal, ToolResult, PlanStep
│   └── prompts.py
│
├── tools/
│   ├── registry.py        # ToolRegistry centralise
│   ├── terminal.py
│   ├── files.py           # Relatif + absolu
│   ├── web.py
│   ├── memory_tool.py
│   └── tasks.py
│
├── memory/
│   ├── session.py         # Contexte actuel (checkpoint)
│   ├── profile.py         # Durable utilisateur
│   ├── journal.py         # Lecons compressees
│   └── db.py
│
├── sandbox/
│   ├── executor.py        # Allowlist + timeout + max output
│   └── permissions.py    # ALLOWLIST commandes et chemins
│
├── observability/
│   ├── logger.py
│   └── tracer.py
│
├── channels/
│   └── cli.py
│
├── config/
│   ├── settings.py
│   └── .env.example
│
└── tests/
    └── test_graph.py      # Tests cibles (pas "validés" encore)
```

## Schemas V2

```python
class ToolCallProposal(TypedDict):
    tool_name: str
    arguments: dict
    reason: str

class ToolResult(TypedDict):
    tool_name: str
    success: bool
    input: dict
    output: str
    error: Optional[str]
    metadata: dict
    recoverable: bool

class AgentState(TypedDict):
    objective: str
    plan: list[str]
    current_step: int
    memory_context: str
    messages: list
    
    last_proposal: ToolCallProposal  # Ce que LLM propose
    last_result: ToolResult           # Ce que runtime execute VRAIMENT
    tool_results: list[ToolResult]    # Historique
    
    status: Literal["running", "finished", "error"]
    decision: Literal["execute", "next_step", "replan", "finish", "error"]
    decision_reason: str
    
    iteration: int
    max_iterations: int
    retry_count: int
    
    session_summary: str
    errors: list[str]
```

## Decidesur Hybride (Runtime-first)

```
SI last_result.success == True → next_step
SI recoverable ET retry < limite → replan
SI erreur bloquante → error
SI fin plan → finish

LLM intervene SEULEMENT pour: replanifier, reformuler, arbitrer flou
```

## Securite V2 (Allowlist)

```python
ALLOWED_COMMANDS = {"ls", "echo", "cat", "python", "git", ...}
ALLOWED_READ_ROOTS = ["/tmp", "/workspace"]
ALLOWED_WRITE_ROOTS = ["/tmp/agent", "/workspace"]

MAX_OUTPUT_CHARS = 4000
MAX_PROCESS_SECONDS = 20
ALLOW_NETWORK = False
```

## Cibles de Tests

Au lieu de "6 criteres valides", vise ces tests precise:

1. plan cree une seule fois
2. choose_action propose un outil autorise
3. execute_tool refuse un outil non autorise
4. record_result stocke un ToolResult propre
5. decide passe a etape suivante apres succes
6. decide stoppe apres max_iterations
7. checkpoint permet reprise via thread_id
8. journal final ecrit un resume de session

## Utilisation

```bash
cd /workspace/project/agent
cp config/.env.example .env
# Ajouter OPENAI_API_KEY

python -m agent.main run "Creer test.txt avec Hello"
python -m agent.main run "Lire test.txt"
```

## Installation

```bash
cd agent
pip install -e .
```

## Configuration

Copier `.env.example` vers `.env` et configurer les variables:

```bash
cp config/.env.example .env
# Éditer .env avec vos clés API
```

Variables obligatoires:
- `OPENAI_API_KEY` - Clé API OpenAI

Variables optionnelles:
- `MODEL_NAME` - Modèle à utiliser (défaut: gpt-4o)
- `MAX_ITERATIONS` - Nombre max d'itérations (défaut: 20)
- `TOOL_TIMEOUT` - Timeout des commandes (défaut: 30s)

## Utilisation

### Mode CLI

```bash
# Lancer une tâche
python -m agent.main run "Créer un fichier test.txt avec Hello World"

# Avec verbeux
python -m agent.main run "..." --verbose

# Reprendre une session
python -m agent.main resume <session_id>

# Voir l'historique
python -m agent.main history
```

### Mode API (Phase 3)

```bash
uvicorn agent.channels.api:app --reload
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      AGENT                             │
│  ┌──────────┐    ┌───────────────────────────────────┐  │
│  │   CLI    │───▶│         LangGraph                 │  │
│  │ Rich     │    │  inject → plan → act → observe    │  │
│  └──────────┘    │                ↑      │           │  │
│                  │           continue ───┘           │  │
│                  │              decide → END         │  │
│                  └───────────────────────────────────┘  │
│                             │                           │
│                  ┌──────────┴──────────┐               │
│                  │    OUTILS           │  MÉMOIRE     │
│                  │ terminal            │  session     │
│                  │ files               │  profile     │
│                  │ web                 │  journal     │
│                  │ memory              │              │
│                  └─────────────────────┘              │
│                  sandbox + logger                     │
└─────────────────────────────────────────────────────────┘
```

## Tests

```bash
pytest agent/tests/ -v
```

Les 6 critères validés:
1. ✅ Reçoit un objectif
2. ✅ Planifie les étapes
3. ✅ Appelle les outils
4. ✅ Checkpoint pour reprise
5. ✅ Observations enregistrées
6. ✅ Pas d'exception non capturée

## Licence

MIT