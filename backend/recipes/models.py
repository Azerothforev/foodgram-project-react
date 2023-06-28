from django.db import models
from django.core.validators import (
    RegexValidator, MinValueValidator, MaxValueValidator)

from users.models import FoodgramUser


def format_string(field1, field2):
    len_field1 = len(field1)
    len_field2 = len(field2)
    max_length = 20

    if len_field1 > max_length and len_field2 > max_length:
        return f'{field1[:max_length]}... - {field2[:max_length]}...'
    elif len_field1 > max_length and len_field2 <= max_length:
        return f'{field1[:max_length]}... - {field2}'
    elif len_field1 <= max_length and len_field2 > max_length:
        return f'{field1} - {field2[:max_length]}...'
    else:
        return f'{field1} - {field2}'


class Tag(models.Model):
    """Модель для хранения тегов."""

    name = models.CharField('Название тега', max_length=200)
    color = models.CharField(
        'Цвет тега',
        max_length=7,
        validators=[
            RegexValidator(
                regex=r'^#[A-Za-z0-9]{0,6}$',
                message='Неверное значение. Допускаются только цифры, '
                'символ #(обратите внимание,что символ # должен быть первым )'
                'и английские буквы.'
            )
        ],
    )
    slug = models.CharField(
        'слаг тега',
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        max_length = 20
        if len(self.name) > max_length:
            return self.name[:max_length] + '...'
        else:
            return self.name


class Ingredient(models.Model):
    """Модель для хранения ингредиентов."""

    name = models.CharField(
        'Название ингредиента', max_length=200)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        max_length = 20
        if len(self.name) > max_length:
            return self.name[:max_length] + '...'
        else:
            return self.name


class Recipe(models.Model):
    """Модель для хранения рецептов."""

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(Ingredient)
    tags = models.ManyToManyField(Tag)
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/',
        default=None
    )
    name = models.CharField('Название рецепта', max_length=200)
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Время приготовления должно '
                              'быть не меньше одной минуты'),
            MaxValueValidator(1440, message='Время приготовления не должно '
                              'превышать 1440 минут')
        ]
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        max_length = 20
        if len(self.name) > max_length:
            return self.name[:max_length] + '...'
        else:
            return self.name


class IngredientInRecipe(models.Model):
    """Модель для хранения связей между рецептами и ингредиентами."""

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        related_name='ingredient_inrecipe',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        related_name='ingredientin_recipe',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        'Количество ингрединта',
        validators=[
            MinValueValidator(1, 'Значение должно быть не меньше 1')
        ]
    )

    class Meta:
        ordering = ('ingredient__name',)
        verbose_name = 'Ингредиент и рецепт'
        verbose_name_plural = 'Ингредиенты и рецепты'

    def __str__(self):
        return format_string(self.ingredient.name, self.recipe.name)


class Follow(models.Model):
    """Модель для хранения подписок на авторов."""

    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор'
    )
    date_followed = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранный автор'
        verbose_name_plural = 'Подписки на авторов'

    def __str__(self):
        return format_string(self.user.username, self.author.username)


class ShopingCartAndFavoriteRecipe(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина и избранное'

    def __str__(self):
        return format_string(self.user.username, self.recipe.name)


class FavoriteRecipe(ShopingCartAndFavoriteRecipe):
    """Модель для хранения избранных рецептов."""

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'


class ShopingCart(ShopingCartAndFavoriteRecipe):
    """Модель для хранения корзины."""

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
