import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if not re.match(r'[\w.@+-]+\Z', value):
        raise ValidationError(
            "Имя пользователя содержит запрещённые символы"
        )
    if value == "me":
        raise ValidationError(
            "Имя пользователя не может быть 'me'"
        )
    return value
