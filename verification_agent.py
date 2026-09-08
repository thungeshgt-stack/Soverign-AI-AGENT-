"""
Verification Agent: checks whether claims in the reasoning output are
supported by evidence. Flags unsupported/over-confident claims (e.g. precise
failure-time predictions) and softens them.
"""
import re
from agents.base_agent import BaseAgent

UNSUPPORTED_PATTERNS = [
    r"\bwill fail\b", r"\bguaranteed\b", r"\bwithin \d+\s*(hour|minute|day)s?\b",
    r"\bcertainly\b", r"\b100%\b", r"\bdefinitely\b",
]


class VerificationAgent(BaseAgent):
    name = "verification_agent"
    display_name = "Verification Agent"

    def run(self, task) -> dict:
        reasoning = task.agent_results.get("reasoning_agent", {})
        all_claims = (
            reasoning.get("possible_issues", [])
            + [reasoning.get("recommendation", "")]
            + [reasoning.get("overall_assessment", "")]
        )
        evidence_count = (
            len(reasoning.get("document_evidence", []))
            + len(reasoning.get("knowledge_evidence", []))
            + len(reasoning.get("vision_evidence", []))
            + len(reasoning.get("data_evidence", []))
        )
        sources_available = len(reasoning.get("sources", []))

        supported = 0
        flagged = 0
        notes = []
        revised_claims = []

        for claim in all_claims:
            if not claim:
                continue
            is_unsupported = any(re.search(p, claim, re.IGNORECASE) for p in UNSUPPORTED_PATTERNS)
            if is_unsupported and evidence_count == 0:
                flagged += 1
                revised = ("Available evidence indicates conditions that may require attention, "
                           "but the provided data does not support a precise or guaranteed outcome.")
                notes.append(f"⚠ UNSUPPORTED CLAIM softened: \"{claim[:80]}...\" → \"{revised}\"")
                revised_claims.append(revised)
            elif is_unsupported and evidence_count > 0:
                flagged += 1
                revised = claim.replace("will fail", "may be at elevated risk of failure") \
                               .replace("guaranteed", "likely") \
                               .replace("definitely", "likely") \
                               .replace("certainly", "likely")
                notes.append(f"⚠ Overconfident phrasing softened in: \"{claim[:80]}...\"")
                revised_claims.append(revised)
            else:
                supported += 1
                revised_claims.append(claim)

        if evidence_count == 0:
            notes.append("⚠ No supporting evidence sources were available for this task.")

        return {
            "agent": self.name,
            "supported": supported,
            "flagged": flagged,
            "sources_available": sources_available,
            "evidence_count": evidence_count,
            "notes": notes or ["✓ All claims consistent with available evidence."],
            "revised_claims": revised_claims,
        }
