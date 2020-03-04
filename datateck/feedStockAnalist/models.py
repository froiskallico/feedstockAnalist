from django.db import models
from mongoengine import *
from datateck.settings import DBNAME

from feedStockAnalist.scripts.app import App

connect(DBNAME)

# Create your models here.
class analysis(Document):
    created_at = DateTimeField(required=True)
    # TODO: Here associate a analysis to user
    # created_by = user.foreignkey

    # TODO: Here call App(csv=True, lista_ops=(114562)).analist() on analysis creation
    # may not to call it here,
    # may i need to call it from view and,
    # from there, store it to analysis field
    analysis = DictField(required=True)





