import requests
from datetime import timedelta
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from news.models import Article
from news.serializers import ArticleSerializer


class ArticleUpdateView(APIView):
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_summary="Обновить статьи из NewsAPI",
        operation_description="""
        Подтягивает свежие статьи из NewsAPI (top-headlines, country=us).
        - Сохраняет только новые (по уникальному полю `url`).
        - Если обновление уже было в последние 30 минут, вернёт сообщение без повторного запроса.
        """,
        responses={
            200: openapi.Response("Данные уже обновлялись недавно"),
            201: openapi.Response(
                description="Список добавленных новых статей",
                schema=ArticleSerializer(many=True),
            ),
        },
        tags=["Новости"]
    )
    def post(self, request):
        cache_key = "articles_update"
        cached = cache.get(cache_key)
        if cached:
            return Response({"detail": "Данные уже обновлялись недавно"}, status=status.HTTP_200_OK)

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "us",
            "apiKey": settings.NEWSAPI_KEY,
        }
        response = requests.get(url, params=params)
        data = response.json()

        new_articles = []
        for item in data.get("articles", []):
            if not Article.objects.filter(url=item["url"]).exists():
                article = Article.objects.create(
                    source_id=item["source"].get("id") if item.get("source") else None,
                    source_name=item["source"].get("name") if item.get("source") else "",
                    author=item.get("author"),
                    title=item.get("title"),
                    description=item.get("description"),
                    url=item.get("url"),
                    url_to_image=item.get("urlToImage"),
                    published_at=item.get("publishedAt"),
                    content=item.get("content"),
                )
                new_articles.append(article)

        cache.set(cache_key, True, 60 * 30)
        return Response(ArticleSerializer(new_articles, many=True).data, status=status.HTTP_201_CREATED)


class ArticleListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить список статей",
        operation_description="""
        Возвращает список сохранённых статей.

        Фильтры:
        - `fresh=true` → только статьи за последние 24 часа
        - `title_contains=<строка>` → поиск по заголовку (регистронезависимый)
        """,
        manual_parameters=[
            openapi.Parameter(
                "fresh",
                openapi.IN_QUERY,
                description="Если `true`, возвращает только свежие статьи за последние 24 часа",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "title_contains",
                openapi.IN_QUERY,
                description="Фильтр по заголовку статьи (подстрока)",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: ArticleSerializer(many=True)},
        tags=["Новости"]
    )
    def get(self, request):
        queryset = Article.objects.all().order_by("-published_at")

        fresh = request.query_params.get("fresh")
        if fresh == "true":
            since = timezone.now() - timedelta(days=1)
            queryset = queryset.filter(published_at__gte=since)

        title_contains = request.query_params.get("title_contains")
        if title_contains:
            queryset = queryset.filter(title__icontains=title_contains)

        serializer = ArticleSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)