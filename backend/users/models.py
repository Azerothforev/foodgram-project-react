from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


USER_EMAIL_MAX_LENGTH = 254
USER_USERNAME_MAX_LENGTH = 150


def role_max_length(role_list):
    """
    Возвращает максимальную длину роли из списка.
    """

    max_length = 0
    for role in role_list:
        if len(role[0]) > max_length:
            max_length = len(role[0])
    return max_length


class FoodgramUser(AbstractUser):
    """
    Модель пользователей.
    """

    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'пользователь'),
        (ADMIN, 'администратор')
    ]

    email = models.EmailField(
        max_length=USER_EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Электронная почта'
    )
    status = models.CharField(
        choices=ROLE_CHOICES,
        default=USER,
        max_length=role_max_length(ROLE_CHOICES),
        verbose_name='Статус пользователя на сайте'
    )
    username = models.CharField(
        max_length=USER_USERNAME_MAX_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='Никнейм'
    )
    first_name = models.CharField(
        max_length=30,
        blank=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=128,
        blank=False,
        verbose_name='Пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_user_role(self):
        return self.status == self.USER

    @property
    def is_admin_role(self):
        return self.status == self.ADMIN
