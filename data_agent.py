from agents.base_agent import BaseAgent
from tools.csv_tools import read_csv, analyze_sensor_data, detect_anomaly


class DataAgent(BaseAgent):
    name = "data_agent"
    display_name = "Data Agent"

    def run(self, task) -> dict:
        csvs = task.files.get("csv", [])
        if not csvs:
            return {"agent": self.name, "files_processed": 0, "analysis": {}}

        all_analysis = {}
        anomalies = {}
        for path in csvs:
            df = read_csv(path)
            analysis = analyze_sensor_data(df)
            all_analysis[path] = analysis
            for field in analysis["fields"]:
                anomalies[field] = detect_anomaly(df, field)

        return {
            "agent": self.name,
            "files_processed": len(csvs),
            "analysis": all_analysis,
            "anomalies": anomalies,
        }
