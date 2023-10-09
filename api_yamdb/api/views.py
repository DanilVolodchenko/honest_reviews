from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status, permissions, viewsets
from rest_framework_simplejwt.tokens import RefreshToken

from api_yamdb.settings import EMAIL_HOST
from .serializers import (SignUpSerializer,
                          ConfirmationCodeSerializer,
                          UserSerializer,
                          MeSerializer,
                          CategorySerializer,
                          GenreSerializer,
                          TitleSerializer,
                          ReviewSerializer,
                          CommentSerializer,
                          TitleGETSerializer
                          )
from users.models import User
from .permissions import IsAdmin, IsAdminModerOwnerOrReadOnly
from reviews.models import Category, Genre, Title, Review
from .mixins import CustomMixin
from .filters import TitleFilter


class SingUpView(GenericAPIView):
    """Получение кода подтверждения на указанный email."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        if User.objects.filter(username=username, email=email):
            return Response('Такой пользователь зарегистрирован',
                            status=status.HTTP_200_OK)
        if (User.objects.filter(email=email)
                or User.objects.filter(username=username)):
            return Response('Такой email или username занят',
                            status=status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(username=username, email=email)
        user = User.objects.get(username=username, email=email)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            message=f'Здравствуйте, {username}\n'
                    f'Код подтверждения: {confirmation_code}',
            from_email=EMAIL_HOST,
            recipient_list=[request.data.get('email')],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class VerifyToken(GenericAPIView):
    """Проверка кода подтверждения и выдача JWT-токена."""

    def post(self, request):
        serializer = ConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        verify_confirmation_code = default_token_generator.check_token(
            user,
            confirmation_code
        )
        if verify_confirmation_code:
            return Response(
                {'access_token': str(
                    RefreshToken.for_user(user).access_token
                )},
                status=status.HTTP_200_OK
            )
        return Response(
            {'confirmation_code': 'Неверный код подтверждения'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Действия с пользователями."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (SearchFilter,)

    @action(
        methods=['get', 'patch'], detail=False,
        url_path='me', url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """Получение информации пользователя о себе."""
        if request.method == 'GET':
            user = get_object_or_404(
                User, username=request.user
            )
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        user = get_object_or_404(
            User, username=request.user
        )
        serializer = MeSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CustomMixin):
    """Действия с категориями."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class GenreViewSet(CustomMixin):
    """Действия с жанрами."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class TitleViewSet(viewsets.ModelViewSet):
    """Действия с произведениями."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)

    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class ReviewViewSet(viewsets.ModelViewSet):
    """Действия с отзывами."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModerOwnerOrReadOnly,)

    def get_queryset(self):
        title = self.get_title_id()
        new_queryset = title.reviews.all()
        return new_queryset

    def perform_create(self, serializer):
        title = self.get_title_id()
        serializer.save(author=self.request.user, title=title)

    def get_title_id(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title


class CommentViewSet(viewsets.ModelViewSet):
    """Действия с комментариями к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModerOwnerOrReadOnly,)

    def get_queryset(self):
        review = self.get_review_id()
        new_queryset = review.comments.all()
        return new_queryset

    def perform_create(self, serializer):
        review = self.get_review_id()
        serializer.save(author=self.request.user, review=review)

    def get_review_id(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id)
        return review
