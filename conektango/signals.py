from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from conektango.models import Customer, Plan, Subscription, Card
from django.dispatch import receiver


@receiver(post_delete, sender=Customer)
def post_delete_customer(sender, instance, **kwargs):
    """Delete Conekta Customer"""
    from conektango.interface import CustomerInterface
    interface = CustomerInterface()
    interface.delete(instance)


@receiver(post_delete, sender=Plan)
def post_delete_plan(sender, instance, **kwargs):
    """Delete Conekta Plan"""
    from conektango.interface import PlanInterface
    interface = PlanInterface()
    interface.delete(instance)


@receiver(post_delete, sender=Card)
def post_delete_card(sender, instance, **kwargs):
    """Delete Conekta Card"""
    from conektango.interface import CardInterface
    interface = CardInterface()
    interface.delete(instance)


@receiver(post_delete, sender=Subscription)
def post_delete_subscription(sender, instance, **kwargs):
    """Cancel Conekta Subscription"""
    from conektango.interface import SubscriptionInterface
    interface = SubscriptionInterface()
    interface.cancel(instance)

