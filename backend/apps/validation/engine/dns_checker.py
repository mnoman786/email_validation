import asyncio
import logging
from typing import List, Tuple, Optional
import dns.resolver
import dns.exception
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

DNS_CACHE_TTL = 3600  # 1 hour


def get_mx_records(domain: str) -> Tuple[bool, List[str]]:
    """
    Synchronous MX record lookup with caching.
    Returns (mx_found, mx_records_list)
    """
    cache_key = f'mx:{domain}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = getattr(settings, 'DNS_TIMEOUT', 5)
        resolver.lifetime = getattr(settings, 'DNS_TIMEOUT', 5)

        answers = resolver.resolve(domain, 'MX')
        mx_records = sorted(
            [str(r.exchange).rstrip('.') for r in answers],
            key=lambda x: answers[0].preference if answers else 0
        )

        result = (True, mx_records)
        cache.set(cache_key, result, DNS_CACHE_TTL)
        return result

    except dns.resolver.NXDOMAIN:
        result = (False, [])
        cache.set(cache_key, result, DNS_CACHE_TTL)
        return result
    except dns.resolver.NoAnswer:
        # Try A record fallback
        result = _check_a_record_fallback(domain)
        cache.set(cache_key, result, DNS_CACHE_TTL // 2)
        return result
    except (dns.exception.Timeout, dns.resolver.NoNameservers):
        return (False, [])
    except Exception as e:
        logger.warning(f'MX lookup error for {domain}: {e}')
        return (False, [])


def _check_a_record_fallback(domain: str) -> Tuple[bool, List[str]]:
    """Check if domain has an A record when no MX record exists."""
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3
        resolver.resolve(domain, 'A')
        return (True, [domain])
    except Exception:
        return (False, [])


def check_domain_exists(domain: str) -> bool:
    """Check if domain has any DNS records."""
    cache_key = f'domain_exists:{domain}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 3
        try:
            resolver.resolve(domain, 'MX')
            result = True
        except dns.resolver.NoAnswer:
            try:
                resolver.resolve(domain, 'A')
                result = True
            except Exception:
                result = False
        except dns.resolver.NXDOMAIN:
            result = False

        cache.set(cache_key, result, DNS_CACHE_TTL)
        return result
    except Exception:
        return False


async def get_mx_records_async(domain: str) -> Tuple[bool, List[str]]:
    """Async version of MX lookup."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_mx_records, domain)
