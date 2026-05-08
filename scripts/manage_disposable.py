#!/usr/bin/env python
"""
Script to bulk import disposable domains from a text file.
Usage: python manage_disposable.py import domains.txt
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.validation.models import DisposableDomain
from apps.validation.engine.disposable_checker import invalidate_disposable_cache


def import_domains(filename: str):
    created = 0
    skipped = 0
    with open(filename) as f:
        for line in f:
            domain = line.strip().lower()
            if not domain or domain.startswith('#'):
                continue
            _, was_created = DisposableDomain.objects.get_or_create(
                domain=domain,
                defaults={'source': 'import', 'is_active': True}
            )
            if was_created:
                created += 1
            else:
                skipped += 1

    invalidate_disposable_cache()
    print(f'Imported {created} new domains. Skipped {skipped} existing.')


def export_domains(filename: str):
    domains = DisposableDomain.objects.filter(is_active=True).values_list('domain', flat=True)
    with open(filename, 'w') as f:
        for domain in domains:
            f.write(domain + '\n')
    print(f'Exported {len(domains)} domains to {filename}')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python manage_disposable.py [import|export] <filename>')
        sys.exit(1)

    action = sys.argv[1]
    filename = sys.argv[2]

    if action == 'import':
        import_domains(filename)
    elif action == 'export':
        export_domains(filename)
    else:
        print(f'Unknown action: {action}')
        sys.exit(1)
