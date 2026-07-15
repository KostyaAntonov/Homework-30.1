from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_youtube_url(value):
    """Проверяет, что ссылка ведет на youtube.com или youtu.be"""
    if 'youtube.com' not in value and 'youtu.be' not in value:
        raise ValidationError(
            _('Ссылка на видео должна вести только на youtube.com или youtu.be'),
            code='invalid_youtube_url'
        )
