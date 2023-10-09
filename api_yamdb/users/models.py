from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    CHOICE_ROLES = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN)
    )

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Почта'
    )
    first_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        blank=True,
        max_length=150,
        verbose_name='Фамилия',
    )
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.TextField(
        choices=CHOICE_ROLES,
        default=USER,
        verbose_name='Права пользователя',
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username
