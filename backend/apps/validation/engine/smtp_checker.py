import asyncio
import smtplib
import socket
import logging
from typing import Tuple, Optional, List
from django.conf import settings

logger = logging.getLogger(__name__)

SMTP_TIMEOUT = getattr(settings, 'SMTP_TIMEOUT', 10) if hasattr(settings, 'SMTP_TIMEOUT') else 10
PROBE_FROM_EMAIL = 'verify@emailguard.io'

GREYLISTING_CODES = {451, 421}
CATCHALL_PROBE_EMAIL = 'thisisaveryrandomemailthatdoesnotexist_xyzabc@'


def smtp_verify_email(email: str, mx_records: List[str]) -> Tuple[bool, bool, Optional[int], bool, bool]:
    """
    Verify email existence via SMTP.
    Returns (smtp_check, smtp_connectable, response_code, is_catch_all, is_greylisted)
    """
    if not mx_records:
        return False, False, None, False, False

    for mx_host in mx_records[:3]:
        try:
            result = _try_smtp_verify(email, mx_host)
            if result is not None:
                smtp_check, connectable, code, is_catch_all, is_greylisted = result
                return smtp_check, connectable, code, is_catch_all, is_greylisted
        except Exception as e:
            logger.debug(f'SMTP error for {email} via {mx_host}: {e}')
            continue

    return False, False, None, False, False


def _try_smtp_verify(email: str, mx_host: str) -> Optional[Tuple[bool, bool, int, bool, bool]]:
    """
    Attempt SMTP verification against a single MX host.
    """
    domain = email.split('@')[1]
    timeout = SMTP_TIMEOUT

    try:
        with smtplib.SMTP(timeout=timeout) as smtp:
            smtp.connect(mx_host, 25)
            smtp.ehlo_or_helo_if_needed()

            code, msg = smtp.mail(PROBE_FROM_EMAIL)
            if code not in (250, 251):
                return False, True, code, False, False

            code, msg = smtp.rcpt(email)

            if code in GREYLISTING_CODES:
                return False, True, code, False, True

            if code in (250, 251):
                # Now check for catch-all
                probe = f'{CATCHALL_PROBE_EMAIL}{domain}'
                catch_code, _ = smtp.rcpt(probe)
                is_catch_all = catch_code in (250, 251)
                return True, True, code, is_catch_all, False

            if code in (550, 551, 552, 553, 554):
                return False, True, code, False, False

            # Other codes - treat as unknown
            return False, True, code, False, False

    except smtplib.SMTPConnectError:
        return None
    except smtplib.SMTPServerDisconnected:
        return None
    except socket.timeout:
        return None
    except ConnectionRefusedError:
        return None
    except OSError as e:
        if 'timed out' in str(e).lower() or 'connection refused' in str(e).lower():
            return None
        return False, False, None, False, False
    except Exception as e:
        logger.warning(f'SMTP verify error for {email}: {e}')
        return None


async def smtp_verify_email_async(email: str, mx_records: List[str]) -> Tuple[bool, bool, Optional[int], bool, bool]:
    """
    Async wrapper for SMTP verification.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, smtp_verify_email, email, mx_records)
