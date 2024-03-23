from typing import Any
from typing import Optional

from django.core.exceptions import ImproperlyConfigured


def required(conf: object, key: str) -> Any:
    value = getattr(conf, key, None)
    if value is None:
        raise ImproperlyConfigured(f"Required settings value is not set {key}")
    return value


def default(conf: object, key: str, default_value: Optional[Any] = None) -> Any:
    value = getattr(conf, key, None)
    if value is None:
        value = default_value
    return value
