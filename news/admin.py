# Регистрируем наши модели, чтобы их было видно в админке
# По идее пофиг на это, но пусть будет, на всякий случай

from django.contrib import admin

from news.models import Article, Favorite

admin.site.register(Article)
admin.site.register(Favorite)
