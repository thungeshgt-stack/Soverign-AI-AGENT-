"""
Task object shared across the orchestrator, agents, and UI.
"""
import uuid
import time
from dataclasses import dataclass, field


@dataclass
class Task:
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    user_query: str = ""
    files: dict = field(default_factory=dict)          # {"pdfs": [...], "images": [...], "csv": [...]}
    required_agents: list = field(default_factory=list)
    agent_results: dict = field(default_factory=dict)   # agent_name -> result dict
    agent_status: dict = field(default_factory=dict)    # agent_name -> "PENDING"/"RUNNING"/"COMPLETED"/"FALLBACK"
    audit_log: list = field(default_factory=list)       # list of (timestamp, message)
    status: str = "CREATED"                              # CREATED -> RUNNING -> COMPLETED
    final_result: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def log(self, message: str):
        self.audit_log.append((time.strftime("%H:%M:%S"), message))

    def set_status(self, agent_name: str, status: str):
        self.agent_status[agent_name] = status
