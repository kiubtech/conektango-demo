from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import View
from django.conf import settings
from conektango.models import Card, Customer
from django.contrib.auth.mixins import LoginRequiredMixin


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
    template_name = "card_list.html"

    def get(self, request):
        cards = Card.objects.filter(customer__user=request.user)
        ctx = {'cards': cards}
        return render(request, self.template_name, ctx)
