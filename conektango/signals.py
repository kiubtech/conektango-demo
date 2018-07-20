from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from conektango.models import Customer
from django.dispatch import receiver


@receiver(post_delete, sender=Customer)
def post_delete_customer(sender, instance, **kwargs):
    """Delete Conekta"""
    from conektango.interface import CustomerInterface
    interface = CustomerInterface()
    interface.delete(instance)

