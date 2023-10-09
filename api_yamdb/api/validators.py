import re
from rest_framework.validators import ValidationError


def check_username(value):
    if value.lower() == 'me':
        raise ValidationError(
            'Нельзя использовать имя "me"'
        )
    if not re.match(r'^[\w.@+-]', value):
        raise ValidationError(
            'Не соответствует паттерну'
        )
    return value
