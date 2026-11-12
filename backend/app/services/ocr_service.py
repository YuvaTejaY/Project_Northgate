from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OCRResult:
    extracted_fields: dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    evidence: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class OCRProvider:
    def extract(self, document_payload: dict[str, Any]) -> OCRResult:
        raise NotImplementedError


class MockOCRProvider(OCRProvider):
    def extract(self, document_payload: dict[str, Any]) -> OCRResult:
        fields = {
            "first_name": document_payload.get("first_name") or "",
            "last_name": document_payload.get("last_name") or "",
            "date_of_birth": document_payload.get("date_of_birth") or "",
            "address": document_payload.get("address") or "",
            "nationality": document_payload.get("nationality") or "",
        }
        evidence = ["Synthetic OCR check completed for local development."]
        errors = []
        if not any(fields.values()):
            errors.append("Unable to read text from the document.")
        return OCRResult(
            extracted_fields=fields,
            confidence_score=0.81,
            evidence=evidence,
            errors=errors,
        )
