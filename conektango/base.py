import conekta
from django.db import models
from django.conf import settings
from conektango.interface import Conektango


class ConektaBase(models.Model):

    def __init__(self, *args, **kwargs):
        # Conekta Instance
        self.conektango = Conektango()
        super(ConektaBase, self).__init__(*args, **kwargs)

    class Meta:
        abstract = True
