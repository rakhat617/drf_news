import django_filters
from django.utils import timezone
from datetime import timedelta
from news.models import Article

class ArticleFilter(django_filters.FilterSet):
    fresh = django_filters.BooleanFilter(method="filter_fresh") # Указываем наш кастомный метод
    # Ну а тут ниче кастомного не надо. Просто указываем, что искать по тайтлу 
    # И что нам достаточно если в тайтле это слово было, а не в точности тайтл писать
    title_contains = django_filters.CharFilter(field_name="title", lookup_expr="icontains") 

    class Meta:
        model = Article
        fields = ["fresh", "title_contains"]

    # Наш кастомный метод, который фильтрует статьи за посл 24 часа
    def filter_fresh(self, queryset, name, value):
        if value:
            since = timezone.now() - timedelta(days=1)
            return queryset.filter(published_at__gte=since)
        return queryset
