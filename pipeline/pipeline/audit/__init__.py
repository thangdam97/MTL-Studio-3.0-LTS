"""
Audit Module - Translation quality assessment for EN and VN.

Provides:
- TranslationAuditor: Core audit engine
- AuditResult: Audit result container
- audit_translation: Convenience function
"""

from .translation_auditor import (
    TranslationAuditor,
    AuditResult,
    AuditIssue,
    Severity,
    IssueCategory,
    audit_translation,
)

__all__ = [
    "TranslationAuditor",
    "AuditResult",
    "AuditIssue",
    "Severity",
    "IssueCategory",
    "audit_translation",
]
