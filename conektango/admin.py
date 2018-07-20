from django.contrib import admin
from .models import *


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'timestamp')
    readonly_fields = ('id', )
    search_fields = ['id']
    list_filter = ('timestamp', )

