import datetime
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.conf import settings
from conektango.base import ConektaBase
from conektango.errors import ConektangoError


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
        else:
            self.conektango.customer.update(self)
        super(Customer, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Cliente")
        verbose_name_plural = _("Clientes")


class Card(ConektaBase):

    BRAND_CHOICES = (
        ('AMERICAN_EXPRESS', 'American Express'),
        ('VISA', 'Visa'),
        ('MC', 'Master Card')
    )

    conekta_token_id = ""  # valor temporal.

    id = models.CharField(max_length=30, verbose_name=_("ID Conekta"), unique=True, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name=_("Cliente"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de creación"))
    # Card extras
    name = models.CharField(max_length=500, verbose_name=_("Nombre visible en la tarjeta"))
    bin = models.CharField(max_length=10)
    brand = models.CharField(max_length=10, choices=BRAND_CHOICES, verbose_name=_("Tipo de tarjeta"))
    exp_month = models.CharField(max_length=2, verbose_name=_("Mes de expiración"))
    exp_year = models.CharField(max_length=2, verbose_name=_("Año de expiración"))
    last4 = models.CharField(max_length=4, verbose_name=_("Últimos 4 dígitos de la tarjeta"))
    default = models.BooleanField(verbose_name=_("Tarjeta default"), help_text=_(
        "Todos los cargos se hacen automáticamente a la tarjeta default del cliente"))

    def save(self, *args, **kwargs):
        if not self.id:  # new
            is_the_only = Card.objects.filter(customer=self.customer).count() == 0
            if is_the_only:
                self.default = True
            else:
                self.default = False
            response = self.conektango.card.save(self)
            self.id = response.message['id']
            self.brand = response.message['brand']
            self.exp_month = response.message['exp_month']
            self.exp_year = response.message['exp_year']
            self.last4 = response.message['last4']
            self.name = response.message['name']
            self.bin = response.message['bin']
        else:
            response = self.conektango.card.update(self)
        if response.success:
            super(Card, self).save(*args, **kwargs)
        else:
            raise ConektangoError(response.message)

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

    id = models.SlugField(max_length=80, verbose_name=_("Id de referencia"),
                          help_text=_("Una vez creado no puede ser editado"),
                          primary_key=True, unique=True)
    name = models.CharField(max_length=600, verbose_name=_('Nombre del paquete'))
    currency = models.CharField(max_length=3, choices=CURRENCY_OPTIONS,
                                help_text=_("Una vez creado no puede ser editado"),
                                verbose_name=_("Moneda"))
    amount = models.IntegerField(verbose_name=_("Precio"))
    frequency = models.IntegerField(choices=FREQ_OPTIONS, default=1,
                                    help_text=_("Una vez creado no puede ser editado"),
                                    verbose_name=_("Frecuencia"))
    interval = models.CharField(choices=INTER_OPTIONS, default='month',
                                help_text=_("Una vez creado no puede ser editado"),
                                max_length=50,
                                verbose_name='Intervalo de pago')
    trial_period_days = models.IntegerField(default=30,
                                            help_text=_("Una vez creado no puede ser editado"),
                                            verbose_name=_("Días de prueba"))
    expiry_count_mode = models.CharField(max_length=10, choices=COUNT_MODE_OPTIONS, default="forever",
                                         help_text=_("Una vez creado no puede ser editado"),
                                         verbose_name=_("Duración"))
    expiry_count = models.IntegerField(null=True, blank=True, verbose_name=_("Número de repeticiones"),
                                       help_text=_(
                                           "Solo aplica con el modo de cobro 'Fijo'. "
                                           "Una vez creado no puede ser editado"))
    # Extras
    is_visible = models.BooleanField(default=False, verbose_name=_('¿Visible?'))
    is_recommended = models.BooleanField(default=False, verbose_name='¿Recomendado?')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Fecha de creación"))

    def save(self, *args, **kwargs):
        if not self.timestamp:
            response = self.conektango.plan.save(self)
        else:
            response = self.conektango.plan.update(self)
        if response.success:
            super(Plan, self).save(*args, **kwargs)
        else:
            raise ConektangoError(response.message)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Plan")
        verbose_name_plural = _("Planes")


class Subscription(ConektaBase):

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
    # Extras
    canceled_at = models.DateTimeField(verbose_name='Fecha de cancelación', null=True, blank=True)
    paused_at = models.DateTimeField(verbose_name='Fecha de pausado', null=True, blank=True)
    trial_start = models.DateTimeField(verbose_name=_("Fecha de inicio del periodo de prueba"), null=True, blank=True)
    trial_end = models.DateTimeField(verbose_name=_("Fecha de fin del periodo de prueba"), null=True, blank=True)
    subscription_start = models.DateTimeField(verbose_name=_("Fecha de inicio de suscripción"), null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name=_("Estatus"), null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if not self.id:
            response = self.conektango.subscription.save(self)
            self.status = response.message['status']
            self.id = response.message['id']
            self.trial_end = datetime.datetime.fromtimestamp(response.message['trial_end']/1000.0)
            self.subscription_start = datetime.datetime.fromtimestamp(response.message['subscription_start']/1000.0)
        else:
            response = self.conektango.subscription.update(self)
        if response.success:
            super(Subscription, self).save(*args, **kwargs)
        else:
            raise ConektangoError(response.message)

    class Meta:
        verbose_name = _("Suscriptor")
        verbose_name_plural = _("Suscriptores")
