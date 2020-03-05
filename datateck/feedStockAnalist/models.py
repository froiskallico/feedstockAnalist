from django.db import models
from jsonfield import JSONField

from django.conf import settings

# Create your models here.
class Analysis(models.Model):
    created_at = models.DateTimeField()
    # TODO: Here associate a analysis to user
    # created_by = models.ForeignKey()
    report = JSONField()

