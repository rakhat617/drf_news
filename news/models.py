from django.db import models

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
