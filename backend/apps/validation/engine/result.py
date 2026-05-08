from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class ValidationResultData:
    email: str
    original_email: str = ''

    # Structure
    local_part: str = ''
    domain: str = ''
    syntax_valid: bool = False

    # DNS
    dns_valid: bool = False
    mx_found: bool = False
    mx_records: List[str] = field(default_factory=list)

    # SMTP
    smtp_check: bool = False
    smtp_connectable: bool = False
    smtp_response_code: Optional[int] = None

    # Characteristics
    is_disposable: bool = False
    is_catch_all: bool = False
    is_role_account: bool = False
    is_free_provider: bool = False
    is_spam_trap: bool = False
    is_greylisted: bool = False
    is_blacklisted: bool = False

    # Scoring
    score: int = 0
    score_breakdown: Dict[str, Any] = field(default_factory=dict)

    # Final verdict
    status: str = 'unknown'
    is_valid: bool = False
    domain_reputation: str = 'unknown'
    risk_level: str = 'low'
    suggested_action: str = 'unknown'

    # Processing
    processing_time_ms: int = 0
    errors: List[str] = field(default_factory=list)
