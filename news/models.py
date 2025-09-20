from django.db import models
from django.conf import settings

# Моделька для статей 
# Прописал бланк тру и нулл тру на тех полях на которых ломалось
# Сделал ордеринг для админки по дате публикации, 
# чтобы свежие сначала отображались
class Article(models.Model):
    source_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="айди источника"
    )
    source_name = models.CharField(
        max_length=255,
        verbose_name="название источника",
    )
    author = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="автор статьи",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="название статьи",
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="описание статьи",
    )
    url = models.URLField(
        unique=True,
        verbose_name="ссылка на статью",
    )
    url_to_image = models.URLField(
        null=True,
        blank=True,
        verbose_name="ссылка на картинку"
    )
    published_at = models.DateTimeField(
        verbose_name="дата публикации",
    )
    content = models.TextField(
        null=True,
        blank=True,
        verbose_name="текст статьи",
    )

    def __str__(self):
        return f"{self.title} : {self.url}"

    class Meta:
        ordering = ("-published_at",)
        verbose_name = "статья"
        verbose_name_plural = "статьи"


# Моделька для избранного 
# Сначала думал просто добавить в модель юзеров
# еще одно поле "favorite_articles", которые было бы мени ту мени
# Но понял, что лучше сделать так, ибо, опять же,
# Это более гибкий подход и гораздо легче с этим работать
# Можно делать модел сериалайзеры, модел вью сеты и тд
# Ну и еще вот доп поля добавлять, типа дату добавления например 
class Favorite(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="user_favorites",
        verbose_name="пользователь"
    )
    article = models.ForeignKey(
        to=Article, 
        on_delete=models.CASCADE, 
        related_name="favorite_article",
        verbose_name="избранная статья"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата добавления в избранное"
    )

    # Вот здесь обязательно настроить, чтобы одинаковый артикль 
    # нельзя было несколько раз записать к одному юзеру
    # ну и для прикола тоже сортирую их для админки по дате добавления 
    class Meta:
        unique_together = ("user", "article")
        ordering = ("-created_at",)
        verbose_name = "избранная статья"
        verbose_name_plural = "избранные статьи"

    def __str__(self):
        return f"{self.user} -> {self.article.title}"