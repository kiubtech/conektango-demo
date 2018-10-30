from django.contrib.auth.models import User
from conektango.models import Customer


def global_ctx(request):
    """
    CTX gobal
    :param request: User request
    :return: ctx global
    """
    try:
        customer = Customer.objects.filter(user=request.user).first()
    except:
        customer = None
    ctx = {
        'conekta_user': customer,
    }
    return ctx



