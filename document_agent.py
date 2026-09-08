from agents.base_agent import BaseAgent
from tools.pdf_tools import read_pdf


class DocumentAgent(BaseAgent):
    name = "document_agent"
    display_name = "Document Agent"

    def run(self, task) -> dict:
        pdfs = task.files.get("pdfs", [])
        all_pages = []
        for path in pdfs:
            pages = read_pdf(path)
            all_pages.extend(pages)
        summary_lines = [f"{p['document']} (p.{p['page']}): {p['text'][:160].strip()}..."
                          for p in all_pages[:6]]
        return {
            "agent": self.name,
            "documents_processed": len(pdfs),
            "pages_extracted": len(all_pages),
            "excerpts": summary_lines,
            "raw_pages": all_pages,
        }
