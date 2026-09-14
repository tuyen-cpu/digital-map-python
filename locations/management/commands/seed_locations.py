"""
Management command: seed locations from the React frontend's locations.json

Usage:
    python manage.py seed_locations
    python manage.py seed_locations --clear      # delete all first
    python manage.py seed_locations --path /custom/path/locations.json
"""
import json
import re
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from locations.models import Location


def _make_id(name='dia-diem'):
    slug = re.sub(r'[^a-z0-9\s-]', '', name.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug).strip('-')
    suffix = hex(int(time.time() * 1000))[-6:]
    return f"{slug or 'dia-diem'}-{suffix}"


def _normalize_media(value):
    """Normalize gallery/panoramas/videos to [{url, alt, name}]."""
    if not isinstance(value, list):
        return []
    result = []
    for item in value:
        if isinstance(item, str) and item.strip():
            result.append({'url': item.strip(), 'alt': '', 'name': ''})
        elif isinstance(item, dict) and item.get('url'):
            result.append({
                'url': str(item.get('url', '')).strip(),
                'alt': str(item.get('alt', '')).strip(),
                'name': str(item.get('name', '')).strip(),
            })
    return result


def _to_float(value):
    try:
        v = float(value)
        return v if v != 0 else None
    except (TypeError, ValueError):
        return None


def _map_item(item):
    """Map JSON fields → Location model fields, handling FE naming differences."""
    # Handle websiteEmail: may contain website or email
    website_email = str(item.get('websiteEmail') or '').strip()
    website = str(item.get('website') or '').strip() or None
    email = str(item.get('email') or '').strip() or None

    # If websiteEmail looks like email, put in email; otherwise website
    if website_email and not website and not email:
        if '@' in website_email:
            email = website_email
        else:
            website = website_email

    # Normalize legacy categories to new list
    CATEGORY_MAP = {
        'accommodation': 'lodging',
        'heritage': 'tourism',
        'education': 'utility',
        'religion': 'tourism',
        'shopping': 'utility',
        'sport': 'entertainment',
        'other': 'utility',
    }
    raw_category = str(item.get('category') or 'utility').strip()
    category = CATEGORY_MAP.get(raw_category, raw_category)
    valid = {'tourism', 'lodging', 'food', 'entertainment', 'health', 'administration', 'utility'}
    if category not in valid:
        category = 'utility'

    return {
        'id': str(item.get('id') or '').strip() or _make_id(item.get('name', '')),
        'name': str(item.get('name') or '').strip(),
        'category': category,   # normalized
        'group': str(item.get('group') or '').strip(),
        'subgroup': str(item.get('subgroup') or '').strip(),
        'address': str(item.get('address') or '').strip(),
        'lat': _to_float(item.get('lat')),
        'lng': _to_float(item.get('lng')),
        'phone': str(item.get('phone') or '').strip() or None,
        'zalo_url': str(item.get('zaloUrl') or '').strip() or None,
        'website': website,
        'email': email,
        'facebook': str(item.get('facebook') or '').strip() or None,
        'hours': str(item.get('hours') or '').strip() or None,
        'keywords': str(item.get('keywords') or '').strip() or None,
        'heritage_status': str(item.get('heritageStatus') or '').strip() or None,
        'description': str(item.get('description') or '').strip(),
        'notes': str(item.get('notes') or '').strip(),
        'image': str(item.get('image') or '').strip() or None,
        'image_alt': str(item.get('imageAlt') or '').strip() or None,
        'image_source_url': str(item.get('imageSourceUrl') or '').strip() or None,
        'image_source_name': str(item.get('imageSourceName') or '').strip() or None,
        'gallery': _normalize_media(item.get('gallery')),
        'panoramas': _normalize_media(item.get('panoramas')),
        'videos': _normalize_media(item.get('videos')),
        'is_active': True,
    }


class Command(BaseCommand):
    help = 'Seed Location data from binh-dinh-tourism-react/src/data/locations.json'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete all locations before seeding')
        parser.add_argument('--path', type=str, default=None, help='Custom path to locations.json')

    def handle(self, *args, **options):
        # Resolve path
        if options['path']:
            json_path = Path(options['path'])
        else:
            json_path = Path(settings.BASE_DIR).parent / 'digital-map-react' / 'src' / 'data' / 'locations.json'

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {json_path}'))
            return

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            self.stderr.write(self.style.ERROR('Expected a JSON array.'))
            return

        if options['clear']:
            count, _ = Location.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing locations.'))

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for item in data:
            if not item.get('name'):
                skipped_count += 1
                continue

            mapped = _map_item(item)
            location_id = mapped.pop('id')

            if not location_id:
                skipped_count += 1
                continue

            _, was_created = Location.objects.update_or_create(
                id=location_id,
                defaults=mapped,
            )
            if was_created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Created: {created_count} | Updated: {updated_count} | Skipped: {skipped_count}'
        ))
