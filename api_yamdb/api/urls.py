from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (SingUpView,
                    VerifyToken,
                    UserViewSet,
                    CategoryViewSet,
                    GenreViewSet,
                    TitleViewSet,
                    ReviewViewSet,
                    CommentViewSet)

router_v1 = DefaultRouter()
router_v1.register(r'users', UserViewSet)
router_v1.register('categories', CategoryViewSet, basename='category')
router_v1.register('genres', GenreViewSet, basename='genre')
router_v1.register('titles', TitleViewSet, basename='title')
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register(
    r'^titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)

urlpatterns = [
    path('v1/auth/signup/', SingUpView.as_view(), name='signup'),
    path('v1/auth/token/', VerifyToken.as_view(), name='verify_email'),
    path('v1/', include(router_v1.urls)),
]
