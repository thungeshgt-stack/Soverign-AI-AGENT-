"""
Thin helper for reading a Task's audit trail for display.
"""


def format_audit_log(task) -> list:
    return [f"{ts}  {msg}" for ts, msg in task.audit_log]
