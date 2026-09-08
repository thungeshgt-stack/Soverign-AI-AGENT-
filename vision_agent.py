from agents.base_agent import BaseAgent
from tools.analysis_tools import analyze_image


class VisionAgent(BaseAgent):
    name = "vision_agent"
    display_name = "Vision Agent"

    def run(self, task) -> dict:
        images = task.files.get("images", [])
        if not images:
            return {"agent": self.name, "images_processed": 0, "results": []}
        results = [analyze_image(img) for img in images]
        return {
            "agent": self.name,
            "images_processed": len(images),
            "results": results,
        }
