from typing import Dict, Any, Tuple
from .result import ValidationResultData


def calculate_score(result: ValidationResultData) -> Tuple[int, Dict[str, Any], str, str, str]:
    """
    Calculate the email quality score (0-100) and return
    (score, score_breakdown, status, risk_level, suggested_action)
    """
    breakdown = {}
    score = 0

    # 1. Syntax validation (max 10 pts)
    if result.syntax_valid:
        score += 10
        breakdown['syntax'] = {'points': 10, 'max': 10, 'label': 'Valid syntax'}
    else:
        breakdown['syntax'] = {'points': 0, 'max': 10, 'label': 'Invalid syntax'}
        return 0, breakdown, 'invalid', 'critical', 'do_not_send'

    # 2. Domain DNS valid (max 10 pts)
    if result.dns_valid and result.mx_found:
        score += 10
        breakdown['dns'] = {'points': 10, 'max': 10, 'label': 'MX records found'}
    elif result.dns_valid:
        score += 5
        breakdown['dns'] = {'points': 5, 'max': 10, 'label': 'Domain exists (no MX)'}
    else:
        breakdown['dns'] = {'points': 0, 'max': 10, 'label': 'No DNS records'}
        return score, breakdown, 'invalid', 'high', 'do_not_send'

    # 3. SMTP mailbox verification (max 25 pts)
    if result.smtp_check:
        score += 25
        breakdown['smtp'] = {'points': 25, 'max': 25, 'label': 'Mailbox verified'}
    elif result.smtp_connectable:
        score += 10
        breakdown['smtp'] = {'points': 10, 'max': 25, 'label': 'SMTP connected (unverifiable)'}
    else:
        score += 0
        breakdown['smtp'] = {'points': 0, 'max': 25, 'label': 'SMTP unreachable'}

    # 4. Catch-all penalty (max 10 pts, penalize -10)
    if result.is_catch_all:
        score -= 5
        breakdown['catch_all'] = {'points': -5, 'max': 0, 'label': 'Catch-all domain (risky)'}
    else:
        score += 10
        breakdown['catch_all'] = {'points': 10, 'max': 10, 'label': 'Not a catch-all domain'}

    # 5. Disposable domain (penalty up to -30)
    if result.is_disposable:
        score -= 30
        breakdown['disposable'] = {'points': -30, 'max': 0, 'label': 'Disposable email domain'}
    else:
        score += 5
        breakdown['disposable'] = {'points': 5, 'max': 5, 'label': 'Not disposable'}

    # 6. Spam trap (penalty -40)
    if result.is_spam_trap:
        score -= 40
        breakdown['spam_trap'] = {'points': -40, 'max': 0, 'label': 'Known spam trap'}
    else:
        score += 5
        breakdown['spam_trap'] = {'points': 5, 'max': 5, 'label': 'Not a spam trap'}

    # 7. Domain reputation (max 15 pts)
    reputation_points = {
        'excellent': 15,
        'good': 12,
        'fair': 6,
        'poor': 0,
        'unknown': 5,
    }
    rep_pts = reputation_points.get(result.domain_reputation, 5)
    score += rep_pts
    breakdown['reputation'] = {
        'points': rep_pts,
        'max': 15,
        'label': f'Domain reputation: {result.domain_reputation}'
    }

    # 8. Role account (penalty -5)
    if result.is_role_account:
        score -= 5
        breakdown['role_account'] = {'points': -5, 'max': 0, 'label': 'Role/functional account'}
    else:
        score += 5
        breakdown['role_account'] = {'points': 5, 'max': 5, 'label': 'Personal account'}

    # 9. Free provider (minor info, no major penalty)
    if result.is_free_provider:
        score -= 2
        breakdown['free_provider'] = {'points': -2, 'max': 0, 'label': 'Free email provider'}
    else:
        score += 5
        breakdown['free_provider'] = {'points': 5, 'max': 5, 'label': 'Business/custom domain'}

    # 10. Greylisted (small penalty)
    if result.is_greylisted:
        score -= 5
        breakdown['greylisted'] = {'points': -5, 'max': 0, 'label': 'Domain may be greylisted'}

    # 11. Blacklisted (major penalty)
    if result.is_blacklisted:
        score -= 20
        breakdown['blacklisted'] = {'points': -20, 'max': 0, 'label': 'Domain on blacklist'}

    # Clamp score to 0-100
    score = max(0, min(100, score))

    # Determine status
    if result.is_spam_trap:
        final_status = 'spam_trap'
    elif result.is_disposable:
        final_status = 'disposable'
    elif not result.mx_found:
        final_status = 'invalid'
    elif result.is_catch_all and not result.smtp_check:
        final_status = 'catch_all'
    elif score >= 70 and result.smtp_check:
        final_status = 'valid'
    elif score >= 40:
        final_status = 'risky'
    elif result.smtp_check:
        final_status = 'valid'
    else:
        final_status = 'unknown'

    # Determine risk level
    if score >= 80:
        risk_level = 'low'
    elif score >= 60:
        risk_level = 'medium'
    elif score >= 30:
        risk_level = 'high'
    else:
        risk_level = 'critical'

    # Determine action
    if final_status in ('valid',) and score >= 70:
        suggested_action = 'safe_to_send'
    elif final_status in ('risky', 'catch_all') or score >= 40:
        suggested_action = 'send_with_caution'
    else:
        suggested_action = 'do_not_send'

    breakdown['total'] = {'score': score, 'status': final_status}

    return score, breakdown, final_status, risk_level, suggested_action
