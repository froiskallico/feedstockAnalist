from django.db import models
from django.conf import settings

from jsonfield import JSONField


# Create your models here.
class Analysis(models.Model):
    created_at = models.DateTimeField()
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete='', default="0")
    report = JSONField()
