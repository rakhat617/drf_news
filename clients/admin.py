from django.contrib import admin

from clients.models import Client, ActivationCode

admin.site.register(Client)
admin.site.register(ActivationCode)
