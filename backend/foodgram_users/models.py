from django.contrib.auth.models import AbstractUser
from django.db import models

EMAIL_MAX_LENGTH = 254


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=EMAIL_MAX_LENGTH,
        unique=True,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка на авторов'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.CheckConstraint(check=~models.Q(
                author=models.F('user')),
                name='could_not_follow_itself'
            ),
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_following')
        ]

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
