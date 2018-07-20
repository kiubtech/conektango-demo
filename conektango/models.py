from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from conektango.base import ConektaBase


class Customer(ConektaBase):
    id = models.CharField(max_length=30, verbose_name=_("Conekta Id"), unique=True, primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("User"),
                                help_text=_("Once created, it can not be modified"))
    phone = models.CharField(max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Creation date"))

    def __str__(self):
        return "{0} {1}".format(self.id, self.user.username)

    def save(self, *args, **kwargs):
        if not self.id:
            conekta_id = self.conektango.customer.save(self)
            self.id = conekta_id
            super(Customer, self).save(*args, **kwargs)
        else:
            self.conektango.customer.update(self)
            super(Customer, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")


class CreditCard(ConektaBase):
    id = models.CharField(max_length=30, verbose_name=_("ID Conekta"), unique=True, primary_key=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Usuario"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de creación"))

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = _("Tarjeta de crédito")
        verbose_name_plural = _("Tarjetas de crédito")


class Plan(ConektaBase):
    FREQ_OPTIONS = (
        (1, _('1')), (2, _('2')), (3, _('3')),
        (4, _('4')), (5, _('5')), (6, _('6')),
        (7, _('7')), (8, _('8')), (9, _('9')),
        (10, _('10')), (11, _('11')), (12, _('12'))
    )

    INTER_OPTIONS = (
        ('minute', _('Minuto')), ('week', _('Semana')),
        ('half_month', _('Quincena')), ('month', _('Mes')),
        ('year', _('Año')),
    )

    CURRENCY_OPTIONS = (
        ('MXN', _("Peso mexicano: MXN")),
        ('USD', _("Dólar americano: USD"))
    )

    COUNT_MODE_OPTIONS = (
        ('forever', _("Indefinido")),
        ('fixed', _("Fijo"))
    )

    id = models.SlugField(max_length=80, verbose_name=_("Id de referencia"), primary_key=True, unique=True)
    name = models.CharField(max_length=600, verbose_name=_('Nombre del paquete'))
    currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS, verbose_name=_("Moneda"))
    amount = models.IntegerField(verbose_name=_("Precio"))
    frequency = models.IntegerField(choices=FREQ_OPTIONS, default=1, verbose_name=_("Frecuencia"))
    interval = models.CharField(choices=INTER_OPTIONS, default='month', max_length=50,
                                verbose_name='Frecuencia de pago')
    trial_period_days = models.IntegerField(default=30, verbose_name=_("Días de prueba"))
    expiry_count_mode = models.CharField(max_length=10, choices=COUNT_MODE_OPTIONS, default="forever",
                                         verbose_name=_("Duración"))
    expiry_count = models.IntegerField(null=True, blank=True, verbose_name=_("Número de repeticiones"),
                                       help_text=_("Solo aplica con el modo de cobro 'Fijo'"))
    # Extras
    is_visible = models.BooleanField(default=False, verbose_name=_('¿Visible?'))
    is_recommended = models.BooleanField(default=False, verbose_name='¿Recomendado?')

    def save(self, *args, **kwargs):
        super(Plan, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Planes")


class Subscriber(ConektaBase):
    STATUS_CHOICES = (
        ('in_trial', _("En trial")),
        ('active', _("Active")),
        ('past_due', _("Vencido")),
        ('paused', _("Pausado")),
        ('canceled', _("Cancelado")),
    )

    id = models.CharField(max_length=1000, verbose_name=_("ID Conekta"), unique=True, primary_key=True)
    customer = models.ForeignKey(Customer, verbose_name=_("Cliente"), on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, verbose_name=_("Plan"), on_delete=models.CASCADE)
    card = models.ForeignKey(CreditCard, verbose_name=_("Tarjeta de Crédito"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Fecha de creación')
    canceled_at = models.DateTimeField(verbose_name='Fecha de creación')
    paused_at = models.DateTimeField(verbose_name='Fecha de creación')
    trial_start = models.DateTimeField(verbose_name=_("Fecha de inicio del periodo de prueba"))
    trial_end = models.DateTimeField(verbose_name=_("Fecha de fin del periodo de prueba"))
    status = models.CharField(max_length=10, verbose_name=_("Estatus"))

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = _("Suscriptor")
        verbose_name_plural = _("Suscriptores")
