from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import datetime
import conekta


class _ConektaResponse:

    def __init__(self):
        self.success = True
        self.message = ""


class _ConektaInit:
    """Conekta settings"""
    def __init__(self):
        self.conekta = conekta
        self.conekta.api_key = settings.CONEKTA_PRIVATE_KEY
        self.conekta.locale = settings.CONEKTA_LOCALE
        self.conekta.api_version = settings.CONEKTA_API_VERSION
        self.response = _ConektaResponse()  # Aquí se almacena el conekta response


class Conektango:

    def __init__(self):
        self.customer = CustomerInterface()
        self.plan = PlanInterface()
        self.subscription = SubscriptionInterface()
        self.card = CardInterface()


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


class PlanInterface(_ConektaInit):

    def save(self, plan):
        """Save plan"""
        json_data = {
            'id': plan.id,
            'name': plan.name,
            'amount': plan.amount * 100,  # Convertimos de centavos a pesos
            'currency': plan.currency,
            'interval': plan.interval,
            'frecuency': plan.frequency,
            'trial_period_days': plan.trial_period_days,
            'expiry_count': plan.expiry_count
        }
        try:
            response = self.conekta.Plan.create(json_data)
            self.response.success = True
            self.response.message = _("Creado correctamente")
        except conekta.ParameterValidationError as error:
            self.response.success = False
            for detail in error.error_json['details']:
                self.response.message += detail['message']
        return self.response

    def update(self, plan):
        """Update plan"""
        json_data = {
            'name': plan.name,
            'amount': plan.amount * 100,  # Convertimos de centavos a pesos
        }
        try:
            plan_obj = conekta.Plan.find(plan.id)
            response = plan_obj.update(json_data)
            self.response.success = True
            self.response.message = _("Actualizado correctamente")
        except conekta.ParameterValidationError as error:
            self.response.success = False
            for detail in error.error_json['details']:
                self.response.message += detail['message']
        return self.response

    def delete(self, plan):
        """Delete plan"""
        plan_obj = self.conekta.Plan.find(plan.id)
        plan_obj.delete()
        return True


class SubscriptionInterface(_ConektaInit):

    def save(self, subscription):
        """Save subscription"""
        json_data = {
            'plan': subscription.plan.id
        }
        try:
            customer_obj = self.conekta.Customer.find(subscription.customer.id)
            subscription = customer_obj.createSubscription(json_data)
            self.response.success = True
            self.response.message = subscription
        except conekta.ParameterValidationError as error:
            self.response.success = False
            for detail in error.error_json['details']:
                self.response.message += detail['message']
        except conekta.ProcessingError as error:
            self.response.success = False
            for detail in error.error_json['details']:
                self.response.message += detail['message']
        return self.response

    def cancel(self, subscription):
        """Delete cancel"""
        customer_obj = self.conekta.Customer.find(subscription.customer.id)
        customer_obj.subscription.cancel()
        return True


class CardInterface(_ConektaInit):

    def save(self, card):
        json_data = {
            'type': 'card'
        }
        try:
            customer = conekta.Customer.find(card.customer.id)
            json_data['token_id'] = card.conekta_token_id
            response = customer.createPaymentSource(json_data)
            self.response.message = response
            self.response.success = True
        except conekta.ParameterValidationError as error:
            self.response.success = False
            for detail in error.error_json['details']:
                self.response.message += detail['message']
            self.response.success = False
        except conekta.ProcessingError as error:
            self.response.success = False
            for detail in error.error_json['details']:
                self.response.message += detail['message']
            self.response.success = False
        return self.response

    def update(self, card):
        json_data = {}
        now = datetime.datetime.now()
        complete_year = str(now.year)[0:2] + card.exp_year
        try:
            customer = conekta.Customer.find(card.customer.id)
            json_data['exp_month'] = card.exp_month
            json_data['exp_year'] = complete_year
            for cus_card in customer.payment_sources:
                if cus_card['id'] == card.id:
                    cus_card.update(json_data)
                    break
            if card.default:
                # setting de default card
                from conektango.models import Card
                customer.update({'default_payment_source_id': card.id})
                Card.objects.filter(default=True, customer=card.customer).exclude(id=card.id).update(default=False)
            response = "OK"
            self.response.message = response
            self.response.success = True
        except conekta.ParameterValidationError as error:
            self.response.success = False
            for detail in error.error_json['details']:
                self.response.message += detail['message']
            self.response.success = False
        except conekta.ProcessingError as error:
            self.response.success = False
            for detail in error.error_json['details']:
                self.response.message += detail['message']
            self.response.success = False
        return self.response

    def delete(self, card):
        customer = conekta.Customer.find(card.customer.id)
        for cus_card in customer.payment_sources:
            if cus_card['id'] == card.id:
                cus_card.delete()
                break
        return True