from django.db import models
from users.models import FoodgramUser
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone


class Tag(models.Model):
    """Модель для хранения тегов."""

    name = models.CharField(max_length=200, verbose_name='Название тега')
    color = models.CharField(
        max_length=7,
        null=False,
        validators=[
            RegexValidator(
                regex=r'^#[A-Za-z0-9]{0,6}$',
                message='Неверное значение. Допускаются только цифры, '
                'символ #(обратите внимание,что символ # должен быть первым )'
                'и английские буквы.'
            )
        ],
        verbose_name='Цвет тега'
    )
    slug = models.CharField(
        max_length=200,
        null=False,
        unique=True,
        verbose_name='слаг тега'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для хранения ингредиентов."""

    name = models.CharField(
        max_length=200, verbose_name='Название ингредиента')
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единица измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
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
        upload_to='recipes/',
        null=True,
        default=None,
        verbose_name='Изображение'
    )
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    text = models.TextField('Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(1, message='Время приготовления должно '
                              'быть не меньше одной минуты')
        ]
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
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
    amount = models.IntegerField(
        verbose_name='Количество ингрединта',
        validators=[
            MinValueValidator(1, 'Значение должно быть не меньше 1')
        ]
    )


class FavoriteRecipe(models.Model):
    """Модель для хранения избранных рецептов."""

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
    date_added = models.DateTimeField(
        default=timezone.now, verbose_name='Дата добавления')

    class Meta:
        ordering = ('user',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


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
        return f'{self.user.username} - {self.author.username}'


class Cart(models.Model):
    """Модель для хранения корзины."""

    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
