import re
from email_validator import validate_email, EmailNotValidError
from typing import Tuple, Optional


ROLE_ACCOUNTS = {
    'admin', 'administrator', 'webmaster', 'postmaster', 'hostmaster',
    'support', 'help', 'helpdesk', 'service', 'contact', 'info', 'information',
    'sales', 'marketing', 'billing', 'accounts', 'accounting', 'finance',
    'hr', 'jobs', 'careers', 'recruitment', 'press', 'media', 'pr',
    'abuse', 'spam', 'noreply', 'no-reply', 'donotreply', 'do-not-reply',
    'bounce', 'bounces', 'mailer', 'mailer-daemon', 'mail', 'email',
    'newsletter', 'news', 'updates', 'notifications', 'alerts', 'notify',
    'security', 'privacy', 'legal', 'compliance', 'dmca',
    'team', 'staff', 'office', 'reception', 'hello', 'hi',
    'root', 'system', 'daemon', 'www', 'ftp', 'smtp', 'imap', 'pop3',
}

FREE_PROVIDERS = {
    'gmail.com', 'googlemail.com',
    'yahoo.com', 'yahoo.co.uk', 'yahoo.fr', 'yahoo.de', 'yahoo.es',
    'hotmail.com', 'hotmail.co.uk', 'hotmail.fr', 'hotmail.de',
    'outlook.com', 'live.com', 'msn.com', 'passport.com',
    'aol.com', 'aim.com',
    'icloud.com', 'me.com', 'mac.com',
    'protonmail.com', 'pm.me', 'proton.me',
    'zoho.com', 'zohomail.com',
    'yandex.com', 'yandex.ru',
    'mail.com', 'email.com',
    'gmx.com', 'gmx.net', 'gmx.de',
    'web.de', 'freenet.de',
    'tutanota.com', 'tuta.io',
    'fastmail.com', 'fastmail.fm',
}


def validate_syntax(email: str) -> Tuple[bool, str, str, str]:
    """
    Returns (is_valid, local_part, domain, error_message)
    """
    email = email.strip().lower()

    if len(email) > 512:
        return False, '', '', 'Email too long'

    if email.count('@') != 1:
        return False, '', '', 'Invalid email format: missing or multiple @ symbols'

    try:
        result = validate_email(email, check_deliverability=False)
        normalized = result.normalized
        local_part, domain = normalized.split('@', 1)
        return True, local_part, domain, ''
    except EmailNotValidError as e:
        parts = email.split('@', 1)
        local_part = parts[0] if len(parts) > 0 else ''
        domain = parts[1] if len(parts) > 1 else ''
        return False, local_part, domain, str(e)


def is_role_account(local_part: str) -> bool:
    return local_part.lower() in ROLE_ACCOUNTS


def is_free_provider(domain: str) -> bool:
    return domain.lower() in FREE_PROVIDERS
