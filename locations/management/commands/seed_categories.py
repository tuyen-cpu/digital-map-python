"""
Management command: seed default categories

Usage:
    python manage.py seed_categories              # thêm nếu chưa có, bỏ qua nếu đã có
    python manage.py seed_categories --clear      # xóa hết rồi seed lại
"""
from django.core.management.base import BaseCommand

from locations.category_models import Category
from locations.category_views import DEFAULT_CATEGORIES


class Command(BaseCommand):
    help = 'Seed default categories from DEFAULT_CATEGORIES in category_views.py'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete all categories before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            count, _ = Category.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing categories.'))

        created_count = 0
        updated_count = 0

        for item in DEFAULT_CATEGORIES:
            key = item['key']
            defaults = {
                'label':               item.get('label', key),
                'short_label':         item.get('short_label', key),
                'emoji':               item.get('emoji', '📍'),
                'description':         item.get('description', ''),
                'marker':              item.get('marker', '#1d4ed8'),
                'order':               item.get('order', 99),
                'is_active':           True,
                'suggested_groups':    item.get('suggested_groups', []),
                'suggested_subgroups': item.get('suggested_subgroups', []),
                'suggested_keywords':  item.get('suggested_keywords', []),
            }
            _, was_created = Category.objects.update_or_create(key=key, defaults=defaults)
            if was_created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Created: {created_count} | Updated: {updated_count} | Total: {Category.objects.count()}'
        ))
