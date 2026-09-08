"""
Reasoning Agent: combines document, knowledge (RAG), vision, and data
evidence into a structured assessment. Distinguishes FACT / OBSERVATION /
INFERENCE / RECOMMENDATION so downstream verification can check support.
"""
from agents.base_agent import BaseAgent
from core.model_router import route


class ReasoningAgent(BaseAgent):
    name = "reasoning_agent"
    display_name = "Reasoning Engine"

    def run(self, task) -> dict:
        doc_result = task.agent_results.get("document_agent", {})
        rag_result = task.agent_results.get("rag_agent", {})
        vision_result = task.agent_results.get("vision_agent", {})
        data_result = task.agent_results.get("data_agent", {})

        document_evidence = [f"[FACT] {e}" for e in doc_result.get("excerpts", [])]
        knowledge_evidence = [
            f"[FACT] {c['document']} (p.{c['page']}), similarity {c.get('similarity')}: "
            f"{c['text'][:180].strip()}..."
            for c in rag_result.get("chunks", [])
        ]

        vision_evidence = []
        for r in vision_result.get("results", []):
            tag = "[OBSERVATION]" if r.get("mode") == "local" else "[OBSERVATION — DEMO MODE]"
            for obs in r.get("observations", []):
                vision_evidence.append(f"{tag} {obs}")

        data_evidence = []
        possible_issues = []
        exceedance_found = False
        for path, analysis in data_result.get("analysis", {}).items():
            for field, stats in analysis.get("fields", {}).items():
                if stats.get("status") == "ABOVE_THRESHOLD":
                    exceedance_found = True
                    data_evidence.append(
                        f"[FACT] {field.title()} max={stats['max']}{stats.get('unit','')} "
                        f"exceeded configured threshold ({stats['threshold']}{stats.get('unit','')}), "
                        f"{stats['exceedance_count']} reading(s) above limit."
                    )
                    possible_issues.append(
                        f"[INFERENCE] Possible {field} anomaly — threshold exceedance suggests "
                        f"abnormal operating conditions requiring inspection."
                    )
                else:
                    data_evidence.append(
                        f"[FACT] {field.title()} mean={stats['mean']}{stats.get('unit','')}, "
                        f"within configured operating range."
                    )

        POSITIVE_VISION_TRIGGERS = ["elevated edge", "localized dark", "corrosion", "crack",
                                    "possible surface damage", "leakage-like"]
        NEGATION_MARKERS = ["no significant", "appears relatively uniform", "not detected",
                             "no visible"]

        def _is_positive_finding(evidence_line: str) -> bool:
            low = evidence_line.lower()
            if any(neg in low for neg in NEGATION_MARKERS):
                return False
            return any(trig in low for trig in POSITIVE_VISION_TRIGGERS)

        if any("OBSERVATION" in e and _is_positive_finding(e) for e in vision_evidence):
            possible_issues.append("[INFERENCE] Visual evidence suggests possible surface "
                                    "abnormality warranting closer inspection.")

        risk_level = "MEDIUM" if (exceedance_found or possible_issues) else "LOW"

        overall_assessment = (
            "Evidence gathered from documents, knowledge base, sensor data and imagery "
            "indicates " + ("abnormal operating conditions that require attention."
                             if risk_level != "LOW" else
                             "operating conditions broadly consistent with expected ranges.")
        )

        recommendation = (
            "[RECOMMENDATION] Schedule a maintenance inspection to confirm and address the "
            "flagged conditions before continued operation."
            if risk_level != "LOW" else
            "[RECOMMENDATION] No immediate maintenance action indicated by current evidence; "
            "continue standard monitoring."
        )

        model, reason = route("reasoning")
        model_note = model.generate(
            prompt=f"Task: {task.user_query}\nEvidence summary compiled from {len(document_evidence)} "
                   f"document facts, {len(knowledge_evidence)} knowledge facts, "
                   f"{len(vision_evidence)} vision observations, {len(data_evidence)} data facts.",
            system="You are an industrial reasoning assistant. Be conservative and evidence-based.",
        )

        sources = []
        for c in rag_result.get("chunks", []):
            sources.append(f"{c['document']} — page {c['page']}")
        for path in data_result.get("analysis", {}):
            sources.append(path.split("/")[-1])
        for img in [r for r in vision_result.get("results", [])]:
            pass  # image sources tracked via task.files

        return {
            "agent": self.name,
            "model_used": model.name,
            "model_mode": model.mode,
            "document_evidence": document_evidence,
            "knowledge_evidence": knowledge_evidence,
            "vision_evidence": vision_evidence,
            "data_evidence": data_evidence,
            "possible_issues": possible_issues or ["No significant issues identified from available evidence."],
            "overall_assessment": overall_assessment,
            "recommendation": recommendation,
            "risk_level": risk_level,
            "confidence": "Evidence-dependent (demo model)" if model.mode == "mock" else "Evidence-dependent",
            "sources": sources,
            "limitations": [
                "This assessment is AI-assisted and does not replace certified human inspection.",
                "Vision analysis runs in demo/heuristic mode unless a local vision model is configured."
                if any("DEMO MODE" in e for e in vision_evidence) else
                "Vision analysis used a configured local model.",
            ],
            "next_actions": [
                "Route this note to a certified engineer for review and approval.",
                "Schedule physical inspection of flagged components." if risk_level != "LOW" else
                "Continue routine monitoring per maintenance schedule.",
            ],
            "model_commentary": model_note,
        }
