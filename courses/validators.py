import re
from django.core.exceptions import ValidationError

def validate_video_link(value):
    # Регулярное выражение для проверки ссылок
    if not re.match(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+', value):
        raise ValidationError('Можно использовать только ссылки на YouTube.')
