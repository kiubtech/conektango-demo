from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import View
from django.conf import settings
from conektango.models import Card, Customer, Order
from django.contrib.auth.mixins import LoginRequiredMixin
import conekta


class Index(View):
    template_name = "index.html"

    def get(self, request):
        return render(request, self.template_name)


class UserProfile(View):
    template_name = "userprofile.html"

    def get(self, request):
        return render(request, self.template_name)


class CreateOrDeleteConektaCustomer(View):

    def get(self, request):
        """
        Recibimos un parámetro en el get:
            - action = 0 -> Eliminar
            - action = 1 -> Agregar customer
        :param request:
        :return: HttpResponseRedirect.
        """
        conekta_action = request.GET.get('action', '0')
        if conekta_action == "1":  # Creamos el customer
            customer = Customer()
            customer.user = request.user
            customer.save()
        else:
            Customer.objects.filter(user=request.user).delete()
        return HttpResponseRedirect("/my-profile/")


class CreateCard(LoginRequiredMixin, View):
    template_name = "card_add.html"

    def get(self, request):
        customer = Customer.objects.filter(user=request.user).first()
        ctx = {'public_key': settings.CONEKTA_PUBLIC_KEY, 'customer': customer}
        return render(request, self.template_name, ctx)

    def post(self, request):
        customer = Customer.objects.get(id=request.POST['customer'])
        card = Card()
        card.customer = customer
        card.conekta_token_id = request.POST.get('conektaTokenId', None)
        card.save()
        return HttpResponseRedirect("/card/list/")


class CardList(LoginRequiredMixin, View):
    """
    Enlistamos las tarjetas.
    """
    template_name = "card_list.html"

    def get(self, request):
        cards = Card.objects.filter(customer__user=request.user)
        ctx = {'cards': cards}
        return render(request, self.template_name, ctx)


class CardDelete(LoginRequiredMixin, View):
    """
    Eliminamos una tarjeta.
    """

    def get(self, request, card_id):
        Card.objects.get(id=card_id).delete()
        return HttpResponseRedirect("/card/list/")


class PaymentsAdd(LoginRequiredMixin, View):
    """
    Generar un nuevo pago.
    """
    template_name = "payments_add.html"
    conekta = None

    def get(self, request):
        try:
            default_card = Card.objects.get(default=True)
        except:
            default_card = None
        ctx = {'default_card': default_card}
        return render(request, self.template_name, ctx)

    def post(self, request):
        customer = Customer.objects.get(user=request.user)
        self.conekta = conekta
        self.conekta.api_key = settings.CONEKTA_PRIVATE_KEY
        self.conekta.locale = settings.CONEKTA_LOCALE
        self.conekta.api_version = settings.CONEKTA_API_VERSION
        order = Order()
        order.customer = customer
        order.payment_method = "card"
        order.payment_source = Card.objects.get(user=request.user, default=True)
        order.currency = "MXN"
        json_items = [{
            'name': request.POST.get('product_name'),
            'product_description': request.POST.get('product_description'),
            'product_price': request.POST.get('product_price'),
            'quantity': request.POST.get('quantity', 1)
        }]  # List of line items
        order.line_items = json_items
        order.metadata = {'confirmation_id': "wit22121", "item_ids": [1, 2, 3, 4], "otro_mas": "++++++"}
        order.save()

        json_data = {
            "currency": "MXN",
            "customer_info": {
                "customer_id": customer.id
            }, "line_items": [
                {
                    "name": request.POST.get("product_name"),
                    "unit_price": request.POST.get("product_price"),
                    "quantity": request.POST.get("quantity", 1)
                }
            ],
            "metadata": {'confirmation_id': "wit22121", "item_ids": [1, 2, 3, 4], "otro_mas": "++++++"},
            "charges": [{
                "payment_method": {
                    "type": "card",
                    "payment_source_id": Card.objects.get(customer=customer, default=True).id  # Tarjeta default
                }
            }]
        }
        order = self.conekta.Order.create(json_data)
        print("ID: " + order.id)
        print("Status: " + order.payment_status)
        return self.get(request)
