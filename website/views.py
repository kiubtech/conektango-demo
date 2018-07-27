from django.shortcuts import render
from django.views.generic import View
from django.conf import settings
from conektango.models import Card, Customer


class CreateCard(View):
    template_name = "create_card.html"

    def get(self, request):
        customers = Customer.objects.all()
        ctx = {'public_key': settings.CONEKTA_PUBLIC_KEY, 'customers': customers}
        return render(request, self.template_name, ctx)

    def post(self, request):
        customer = Customer.objects.get(id=request.POST['customer'])
        card = Card()
        card.customer = customer
        card.conekta_token_id = request.POST.get('conektaTokenId', None)
        card.save()
        return self.get(request)
