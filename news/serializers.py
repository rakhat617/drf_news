from rest_framework import serializers
from news.models import Article, Favorite

# Тупа простейший сериализатор. Тут ниче лишнего и не понадобилось
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"

# Тупа чуть посложнее получилось, ибо 
# 1) для отображения и добавления нам нужны разные "артикли" 
# то есть для отображения (лист метод) нам нужны статьи в полном виде 
# а для добавления статьи в избранное (пост метод) нужен только ее айди
# 2) нам нужна кастомная валидация чтобы при добавлении одной и той же
# статьи к одному юзеру, нам вылетала не 500 ошибка сервера, а 400 ошибка 
class FavoriteSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(read_only=True) # Для list 
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(), source="article", write_only=True
    ) # Для post

    class Meta:
        model = Favorite
        fields = ["id", "article", "article_id", "created_at"]
    
    def validate(self, attrs):
        user = self.context["request"].user
        article = attrs["article"]
        if Favorite.objects.filter(user=user, article=article).exists():
            raise serializers.ValidationError("Эта статья уже есть в избранном")
        return attrs