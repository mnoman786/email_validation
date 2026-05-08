import time
import logging
from typing import Optional
from django.conf import settings
from django.core.cache import cache

from .result import ValidationResultData
from .syntax import validate_syntax, is_role_account, is_free_provider
from .dns_checker import get_mx_records, check_domain_exists
from .smtp_checker import smtp_verify_email
from .disposable_checker import is_disposable_domain
from .scorer import calculate_score

logger = logging.getLogger(__name__)

RESULT_CACHE_TTL = 3600 * 6  # 6 hours


class EmailValidator:
    """
    Full pipeline email validator.
    Stages:
      1. Syntax check
      2. Domain extraction
      3. DNS lookup + MX verification
      4. Disposable check
      5. Spam trap check
      6. SMTP verification (with catch-all detection)
      7. Score calculation + final verdict
    """

    def __init__(
        self,
        check_smtp: bool = True,
        use_cache: bool = True,
        timeout_smtp: int = None,
    ):
        self.check_smtp = check_smtp
        self.use_cache = use_cache
        self.timeout_smtp = timeout_smtp or getattr(settings, 'SMTP_TIMEOUT', 10)

    def validate(self, email: str) -> ValidationResultData:
        start_time = time.time()
        email_clean = email.strip().lower()
        result = ValidationResultData(email=email_clean, original_email=email)

        # Check result cache
        if self.use_cache:
            cached = self._get_cached_result(email_clean)
            if cached:
                cached.processing_time_ms = 1
                return cached

        try:
            self._run_pipeline(result)
        except Exception as e:
            logger.error(f'Validation pipeline error for {email}: {e}', exc_info=True)
            result.errors.append(str(e))
            result.status = 'unknown'

        result.processing_time_ms = int((time.time() - start_time) * 1000)

        if self.use_cache and result.status != 'unknown':
            self._cache_result(email_clean, result)

        return result

    def _run_pipeline(self, result: ValidationResultData):
        # Stage 1: Syntax
        is_valid_syntax, local_part, domain, syntax_error = validate_syntax(result.email)
        result.syntax_valid = is_valid_syntax
        result.local_part = local_part
        result.domain = domain

        if not is_valid_syntax:
            result.errors.append(f'Syntax error: {syntax_error}')
            result.status = 'invalid'
            result.score = 0
            return

        # Stage 2: Email characteristics (no network needed)
        result.is_role_account = is_role_account(local_part)
        result.is_free_provider = is_free_provider(domain)

        # Stage 3: Disposable check
        result.is_disposable = is_disposable_domain(domain)

        # Stage 4: Spam trap check
        result.is_spam_trap = self._check_spam_trap(result.email, domain)

        # Stage 5: DNS + MX records
        mx_found, mx_records = get_mx_records(domain)
        result.mx_found = mx_found
        result.mx_records = mx_records
        result.dns_valid = mx_found or check_domain_exists(domain)

        if not result.dns_valid:
            score, breakdown, status, risk, action = calculate_score(result)
            result.score = score
            result.score_breakdown = breakdown
            result.status = status
            result.risk_level = risk
            result.suggested_action = action
            return

        # Stage 6: Domain reputation
        result.domain_reputation = self._get_domain_reputation(domain)

        # Stage 7: SMTP verification
        if self.check_smtp and mx_found:
            smtp_ok, smtp_connectable, smtp_code, is_catch_all, is_greylisted = smtp_verify_email(
                result.email,
                result.mx_records
            )
            result.smtp_check = smtp_ok
            result.smtp_connectable = smtp_connectable
            result.smtp_response_code = smtp_code
            result.is_catch_all = is_catch_all
            result.is_greylisted = is_greylisted
        else:
            # Without SMTP check, mark as catch-all if domain accepts anything
            result.smtp_check = False
            result.smtp_connectable = False

        # Stage 8: Score + final verdict
        score, breakdown, status, risk, action = calculate_score(result)
        result.score = score
        result.score_breakdown = breakdown
        result.status = status
        result.risk_level = risk
        result.suggested_action = action
        result.is_valid = status in ('valid', 'catch_all')

    def _check_spam_trap(self, email: str, domain: str) -> bool:
        try:
            from apps.validation.models import SpamTrapDomain
            return SpamTrapDomain.objects.filter(
                domain=domain,
                is_active=True
            ).exists()
        except Exception:
            return False

    def _get_domain_reputation(self, domain: str) -> str:
        """Determine domain reputation based on known providers and heuristics."""
        from .syntax import FREE_PROVIDERS
        if domain in FREE_PROVIDERS:
            return 'good'
        # Check domain age/known-good domains heuristic
        known_good_tlds = {'.com', '.org', '.net', '.edu', '.gov'}
        for tld in known_good_tlds:
            if domain.endswith(tld):
                return 'good'
        parts = domain.split('.')
        if len(parts) >= 2:
            return 'fair'
        return 'unknown'

    def _get_cached_result(self, email: str) -> Optional[ValidationResultData]:
        try:
            cache_key = f'validation:{email}'
            return cache.get(cache_key)
        except Exception:
            return None

    def _cache_result(self, email: str, result: ValidationResultData):
        try:
            cache_key = f'validation:{email}'
            cache.set(cache_key, result, RESULT_CACHE_TTL)
        except Exception:
            pass
