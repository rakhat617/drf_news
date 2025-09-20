from django.urls import path, include
from rest_framework.routers import DefaultRouter
from news.views import ArticleUpdateView, ArticleListView, FavoriteViewSet

# Роутер для модел вью сета 
# (жоска я конечно сидел тупил, пытаясь сделать для него обычные юрлы)
router = DefaultRouter()
router.register("favorites", FavoriteViewSet, basename="favorite")

urlpatterns = [
    path("update/", ArticleUpdateView.as_view(), name="articles-update"),
    path("list/", ArticleListView.as_view(), name="articles-list"),
    path("", include(router.urls)),
]