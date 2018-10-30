from django.contrib.auth.models import User
from conektango.models import Customer


def global_ctx(request):
    """
    CTX gobal
    :param request: User request
    :return: ctx global
    """
    ctx = {
        'conekta_user': Customer.objects.filter(user=request.user).first(),
    }
    return ctx



