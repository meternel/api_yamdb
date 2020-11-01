from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api_yamdb.settings import EMAIL_FROM_DEFOULT, EMAIL_AUTH_URL
from users.models import CustomUser
from users.serializers import EmailSerializer, GetTokenSerializer, UserSerializer

from .permissions import IsAdmin


class GetConfirmationCode(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        user, created = CustomUser.objects.get_or_create(email=email)
        if created:
            user.username = email
            user.save()
        confirmation_code = default_token_generator.make_token(user)
        subject = "Регистрация в YaMDB"
        body = (
            f"Для продолжения регистрации {user.email} в YaMDB и\n"
            f"получения токена отправьте запрос на\n"
            f"{EMAIL_AUTH_URL} с\n"
            f"параметрами email и confirmation_code.\n\n"
            f"Ваш confirmation_code: {confirmation_code}\n"
        )
        send_mail(
            subject, body, EMAIL_FROM_DEFOULT, [user.email,], fail_silently=False,
        )

        return Response(serializer.data, status=200)


class GetToken(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get("email")
        code = serializer.data.get("confirmation_code")
        user = get_object_or_404(CustomUser, email=email)
        if default_token_generator.check_token(user, code):
            token = AccessToken.for_user(user)
            return Response({"token": f"{token}"}, status=200)
        return Response(status=400)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)

    @action(
        detail=False, methods=("patch", "get",), permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            if request.method == "GET":
                return Response(serializer.data, status=200)
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
