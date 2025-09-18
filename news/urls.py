from django.urls import path
from .views import ArticleUpdateView, ArticleListView

urlpatterns = [
    path("update/", ArticleUpdateView.as_view(), name="articles-update"),
    path("list/", ArticleListView.as_view(), name="articles-list"),
]