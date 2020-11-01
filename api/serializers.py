from rest_framework import serializers

from .models import Category, Comment, Genre, Review, Title


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field="slug", many=True,
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug",
    )

    class Meta:
        fields = ("id", "name", "year", "description", "genre", "category")
        model = Title


class TitleListSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = "__all__"
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True
    )

    def validate(self, data):
        title = self.context["title"]
        request = self.context["request"]
        if (
                request.method != "PATCH" and
                Review.objects.filter(title=title,
                                      author=request.user).exists()
        ):
            raise serializers.ValidationError(
                "О произведении можно оставить только один отзыв"
            )
        return data

    class Meta:
        model = Review
        fields = "__all__"
        extra_kwargs = {"title": {"required": False}}


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
    )

    class Meta:
        model = Comment
        exclude = ("review",)
