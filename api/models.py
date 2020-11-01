import datetime
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import CustomUser as User


class Category(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Category"


class Genre(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Genre"


class Title(models.Model):
    name = models.CharField(max_length=60, db_index=True)
    year = models.IntegerField(
        db_index=True,
        validators=[MaxValueValidator(datetime.date.today().year)]
    )
    description = models.TextField()
    genre = models.ManyToManyField(Genre, related_name="titles")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Title"


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews", null=False
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name="reviews", null=False,
    )
    text = models.TextField(max_length=1000)
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)], null=False,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        null=False, blank=False,
    )

    class Meta:
        ordering = ["pub_date"]
        verbose_name = "Review"


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField(max_length=1000)
    pub_date = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        ordering = ["id"]
        verbose_name = "Comment"
