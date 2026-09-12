from django.db import models

DEFAULT_HERO_SLIDES = [
    {
        'id': 'le-hong-phong',
        'image': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/%C4%90%C6%B0%E1%BB%9Dng%20L%C3%AA%20H%E1%BB%93ng%20Phong%2C%20Ph%C6%B0%E1%BB%9Dng%20B%C3%ACnh%20%C4%90%E1%BB%8Bnh%2C%20th%E1%BB%8B%20x%C3%A3%20An%20Nh%C6%A1n%2C%20t%E1%BB%89nh%20B%C3%ACnh%20%C4%90%E1%BB%8Bnh.JPG?width=1920',
        'title': 'Nhịp sống Phường Bình Định',
        'caption': 'Không gian đô thị trên trục Lê Hồng Phong.',
    },
    {
        'id': 'cua-dong',
        'image': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/C%E1%BB%95ng%20ch%C3%A0o%20th%E1%BB%8B%20x%C3%A3%20An%20Nh%C6%A1n.jpg?width=1920',
        'title': 'Dấu ấn Thành Bình Định',
        'caption': 'Không gian lịch sử gắn với vùng An Nhơn - Bình Định.',
    },
    {
        'id': 'thanh-hoang-de',
        'image': 'https://commons.wikimedia.org/wiki/Special:Redirect/file/C%E1%BB%95ng%20ch%C3%ADnh%20t%E1%BB%AD%20c%E1%BA%A5m%20th%C3%A0nh%2C%20th%C3%A0nh%20Ho%C3%A0ng%20%C4%90%E1%BA%BF.JPG?width=1920',
        'title': 'Không gian di sản An Nhơn',
        'caption': 'Hình ảnh thực tế khu vực An Nhơn dùng làm ảnh minh họa.',
    },
]


class SiteSettings(models.Model):
    """Singleton — always use get_or_create(pk=1)."""
    hero_slides = models.JSONField(default=list)
    hero_interval_ms = models.IntegerField(default=5200)

    class Meta:
        db_table = 'site_config_settings'

    def __str__(self):
        return 'Site Settings'

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                'hero_slides': DEFAULT_HERO_SLIDES,
                'hero_interval_ms': 5200,
            },
        )
        return obj
