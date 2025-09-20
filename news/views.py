import requests
from django.conf import settings
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins, generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from news.models import Article, Favorite
from news.serializers import ArticleSerializer, FavoriteSerializer
from common.filters import ArticleFilter


# Вьюшка для подтягивания статей из сайта и сохранения в нашу базу
class ArticleUpdateView(APIView):
    # Я считаю только у админа должна быть такая власть, кек
    # Хотя можно и сделать для всех юзеров, ибо мы все равно ограничили
    # Количество запросов, только раз в 30 минут
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
    # Честно скажу, эту вьюку мне сделала ГПТ, ибо я хз был че с этим сайтом делать
    def post(self, request):
        cache_key = "articles_update" # Ключ который сохраняется в кеш (Тру или Фолс)
        cached = cache.get(cache_key) # Достаем его из кеша 
        if cached: # Если он Тру, значит запрос уже делался в последние 30 минут, мы просто выходим
            return Response({"detail": "Данные уже обновлялись недавно"}, status=status.HTTP_200_OK)

        url = "https://newsapi.org/v2/top-headlines" # ЮРЛ откуда будем доставать данные
        params = { # Параметры, по которым будем доставать
            "country": "us", # ГПТ выбрала штаты, ну и ладно. 
            # Хотя наверное можно сделать чтобы юзер сам вводил страну
            "apiKey": settings.NEWSAPI_KEY, # это апи кей, который нужно получить зарегавшись на сайте, 
            # и лучше сохранить его в .env
        }
        response = requests.get(url, params=params) # достаем, собственно, данные
        data = response.json() # форматируем их в json

        # Добавляем статьи, которые достали с сайта, в нашу БД 
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

        cache.set(cache_key, True, 60 * 30) # Сохраняем в кеш значение Тру на 30 минут
        # Отображаем сохраненные статьи
        return Response(ArticleSerializer(new_articles, many=True).data, status=status.HTTP_201_CREATED)


# Вьюшка для отображения сохраненных статей
# Сначала тоже сделал через АПИВью, но потом ГПТ мне подсказала
# Сделать через ЛистАПИВью, и вынести фильтрацию в отдельный файл, как мы делали в соц сети. 
# Но тут попроще конечно, можно было и не выносить по идее
# А потом я вспомнил что нужно кешировать, и все равно пришлось метод вручную писать
# Крч надо было АПИВью оставлять, ну уже пофиг 
class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all().order_by("-published_at")
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter # Указываем что нужно использовать наш кастомный фильтр

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
                type=openapi.TYPE_BOOLEAN,
                enum=[True, False],
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
    def get(self, request, *args, **kwargs):
        # Создаем ключ кэша по параметрам запроса
        cache_key = f"articles_list_{request.GET.urlencode()}"

        # Проверяем его, мб уже он есть по такому запросу
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Ну и собстна кладем результат в кеш на 10 минут
        cache.set(cache_key, serializer.data, 60 * 10)

        return Response(serializer.data, status=status.HTTP_200_OK)


# Вьюшка для избранного
# Тут крч сначала сделал с модел вью сетом, ибо с ним легче всего
# Но меня бесило, что в сваггере все 6 методов, когда нам нужно только 3
# И там можно ограничить, но почемуто ретрив все равно отображался
# Ну и крч сделал я через миксины, указав только нужные   
class FavoriteViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    # Это мы прописываем, чтобы он доставал только избранные текущего пользователя
    # (при лист или дестрой методе)
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): # Вот это чисто чтобы свагер норм работал, снова ГПТ спасла
            return Favorite.objects.none()
        return Favorite.objects.filter(user=self.request.user)

    # Это тоже, чтобы он автоматически сохранял в избранные текущего пользователя
    # То есть чтобы не надо было прописывать его айди, а просто достаточно айди статьи 
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # Ну и тут просто три метода с документацией (которая сделала ГПТ, храни ее господь)
    @swagger_auto_schema(
        operation_summary="Список избранного",
        operation_description="Возвращает список статей, добавленных в избранное текущим пользователем.",
        responses={200: FavoriteSerializer(many=True)},
        tags=["Избранное"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Хотя вот эту свагер схему ГПТ мне постоянно кривой какойто делала, пришлось самому покопаться
    # Чтобы сделать так, чтобы только айди статьи высвечивалось как нужное
    @swagger_auto_schema(
        operation_summary="Добавить статью в избранное",
        operation_description="Добавляет указанную статью в избранное текущего пользователя.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "article_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID статьи"),
            },
            required=["article_id"],
        ),
        responses={201: FavoriteSerializer(), 400: "Bad request"},
        tags=["Избранное"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить из избранного",
        operation_description="Удаляет статью из избранного текущего пользователя по её ID.",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="ID записи избранного",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={204: "Статья удалена", 404: "Not found"},
        tags=["Избранное"]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)