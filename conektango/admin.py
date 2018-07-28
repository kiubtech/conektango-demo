from django.contrib import admin
from .models import *
from django.utils.translation import ugettext_lazy as _


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'timestamp')
    readonly_fields = ('id', )
    search_fields = ['id']
    list_filter = ('timestamp', )


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    fields = ('id', 'name', ('amount', 'currency'), 'frequency', 'interval',
              'trial_period_days', 'expiry_count_mode', 'expiry_count', 'timestamp')
    list_display = ('id', 'name', 'amount', 'currency', 'frequency', 'interval', 'timestamp')
    search_fields = ['name']
    list_filter = ('currency', 'interval')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["timestamp", "id", "frequency", "interval", "trial_period_days",
                    "expiry_count_mode", "expiry_count", "currency"]
        else:
            return ["timestamp"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'status', 'timestamp', 'canceled_at', 'paused_at',
                       'trial_start', 'trial_end', 'subscription_start')
    list_display = ('id', 'customer', 'plan', 'status')
    list_filter = ('status', )
    fieldsets = [
        (_('Suscripción'), {'fields': ['customer', 'plan', 'status']}),
        (_('Información adicional'), {'fields': ['id', 'timestamp', 'canceled_at',
                                                 'paused_at', 'trial_start', 'trial_end', 'subscription_start']}),
    ]


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'customer', 'brand', 'default')
    list_filter = ('default', 'brand')
    readonly_fields = ('id', 'customer', 'name', 'bin', 'brand', 'last4')
