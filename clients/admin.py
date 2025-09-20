# Регистрируем наши модели, чтобы их было видно в админке
# По идее пофиг на это, но пусть будет, на всякий случай

from django.contrib import admin

from clients.models import Client, ActivationCode

admin.site.register(Client)
admin.site.register(ActivationCode)
