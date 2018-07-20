import conekta
from django.conf import settings


class _ConektaInit:
    """Conekta settings"""
    def __init__(self):
        self.conekta = conekta
        self.conekta.api_key = settings.CONEKTA_PRIVATE_KEY
        self.conekta.locale = settings.CONEKTA_LOCALE
        self.conekta.api_version = settings.CONEKTA_API_VERSION


class Conektango:

    def __init__(self):
        self.customer = CustomerInterface()


class CustomerInterface(_ConektaInit):

    def save(self, customer):
        """Save customer"""
        json_data = {
            'name': customer.user.get_full_name() if customer.user.get_full_name() != "" else customer.user.username,
        }
        if customer.user.email:
            json_data['email'] = customer.user.email
        if customer.phone:
            json_data['phone'] = customer.phone
        data = self.conekta.Customer.create(json_data)
        return data.id

    def update(self, customer):
        """Update customer"""
        json_data = {
            'name': customer.user.get_full_name() if customer.user.get_full_name() != "" else customer.user.username,
        }
        if customer.user.email:
            json_data['email'] = customer.user.email
        if customer.phone:
            json_data['phone'] = customer.phone
        customer_obj = self.conekta.Customer.find(customer.id)
        customer_obj.update(json_data)
        return True

    def delete(self, customer):
        """Delete Customer"""
        customer_obj = self.conekta.Customer.find(customer.id)
        customer_obj.delete()
        return True
