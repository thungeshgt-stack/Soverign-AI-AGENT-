from agents.base_agent import BaseAgent
from tools.report_tools import create_docx_report


class ReportAgent(BaseAgent):
    name = "report_agent"
    display_name = "Report Generator"

    def run(self, task) -> dict:
        reasoning = task.agent_results.get("reasoning_agent", {})
        verification = task.agent_results.get("verification_agent", {})
        path = create_docx_report(task, reasoning, verification)
        return {"agent": self.name, "report_path": path}
