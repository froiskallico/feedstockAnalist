from django.db import models
from jsonfield import JSONField
from feedStockAnalist.scripts.app import App

# Create your models here.
class analysis(models.Model):
    created_at = models.DateTimeField()
    # TODO: Here associate a analysis to user
    # created_by = user.foreignkey

    # TODO: Here call App(csv=True, lista_ops=(114562)).analist() on analysis creation
    # may not to call it here,
    # may i need to call it from view and,
    # from there, store it to analysis field
    analysis = JSONField()


