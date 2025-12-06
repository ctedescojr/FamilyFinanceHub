# This file can be left empty or used for package-level initializations.
from .celery import app as celery_app

__all__ = ('celery_app',)
