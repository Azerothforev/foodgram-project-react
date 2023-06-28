from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    FavoriteRecipe, IngredientInRecipe, Ingredient,
    Recipe, Follow, Tag, ShopingCart
)

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для пользовательской модели.
    """

    username = serializers.CharField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """
        Получает значение, указывающее, подписан ли пользователь на автора.
        """
        request = self.context.get('request')
        if request:
            user = request.user
            return Follow.objects.filter(author_id=obj.id, user=user).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Tag.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Ingredient.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipesSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели IngredientInRecipe.
    """

    id = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount',)


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """
    Сериализатор для минимальной информации о рецепте.
    """

    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientInRecipesSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', 'ingredients')
        read_only_fields = ('name', 'image', 'cooking_time', 'ingredients')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Recipe.
    """

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'text',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        """
        Получает информацию об ингредиентах для рецепта.
        """
        ingredient_in_recipes = obj.ingredientin_recipe.all()
        serialized_ingredients = []
        for ingredient_in_recipe in ingredient_in_recipes:
            serialized_ingredient = {
                'id': ingredient_in_recipe.ingredient.id,
                'name': ingredient_in_recipe.ingredient.name,
                'measurement_unit':
                ingredient_in_recipe.ingredient.measurement_unit,
                'amount': ingredient_in_recipe.amount,
            }
            serialized_ingredients.append(serialized_ingredient)
        return serialized_ingredients

    def get_is_favorited(self, obj):
        """
        Получает значение, указывающее, добавлен
        ли рецепт в избранное у пользователя.
        """
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and FavoriteRecipe.objects.filter(
                recipe_id=obj.id,
                user=request.user
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Получает значение, указывающее, добавлен
        ли рецепт в корзину у пользователя.
        """
        request = self.context.get('request')
        return (
            request
            and ShopingCart.objects.filter(
                recipe_id=obj.id,
                user=request.user
            ).exists()
        )


class RecipeAddSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецепта.
    """

    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = IngredientInRecipesSerializer(
        source='ingredientin_recipe', many=True)
    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'image', 'name', 'text', 'cooking_time',
        )

    def validate_tags(self, data):
        """
        Проверяет, выбраны ли хотя бы один тег и отсутствуют
        повторяющиеся теги.
        """
        tags = data

        if tags is None or len(tags) == 0:
            raise serializers.ValidationError('Выберите хотя бы 1 тег.')

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не должны повторяться.')

        return data

    def validate_ingredients(self, data):
        """
        Проверяет выбор хотя бы одного ингредиента и их количество.
        """
        ingredients = self.initial_data.get('ingredients')

        if len(ingredients) == 0:
            raise serializers.ValidationError(
                'Выберите хотя бы 1 ингредиент из списка.')

        ingredients_id = []
        for ingredient in ingredients:
            if ingredient.get('id') in ingredients_id:
                raise serializers.ValidationError(
                    'Ингредиенты не могут повторяться. Проверьте свой рецепт.')
            if ingredient.get('amount') in (None, 0):
                raise serializers.ValidationError(
                    'Количество ингредиента обязательно для заполнения.'
                    ' Минимальное значение 1.'
                )

            ingredients_id.append(ingredient.get('id'))

        return data

    def create(self, recipe_obj):
        """
        Создает новый рецепт.
        """
        author = self.context.get('request').user
        tags = recipe_obj.pop('tags')
        ingredients = recipe_obj.pop('ingredientin_recipe')
        recipe = Recipe.objects.create(author=author, **recipe_obj)

        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    recipe=recipe,
                    amount=ingredient.get('amount'),
                    ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                )
                for ingredient in ingredients
            ]
        )
        return recipe

    def update(self, instance, recipe_obj):
        """
        Обновляет рецепт.
        """
        instance.name = recipe_obj.get('name', instance.name)
        instance.text = recipe_obj.get('text', instance.text)
        instance.image = recipe_obj.get('image', instance.image)
        instance.cooking_time = recipe_obj.get
        ('cooking_time', instance.cooking_time)

        tags = recipe_obj.get('tags')
        if tags:
            instance.tags.set(tags)

        ingredients = recipe_obj.get('ingredientin_recipe')
        if ingredients:
            instance.ingredientin_recipe.all().delete()
            IngredientInRecipe.objects.bulk_create(
                [
                    IngredientInRecipe(
                        recipe=instance,
                        amount=ingredient.get('amount'),
                        ingredient=Ingredient.objects.get
                        (id=ingredient.get('id')),
                    )
                    for ingredient in ingredients
                ]
            )

        instance.save()
        return instance


class FollowSerializer(CustomUserSerializer):
    """
    Сериализатор подписок.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (
            CustomUserSerializer.Meta.fields + ('recipes', 'recipes_count',))
        read_only_fields = ('email', 'username',)

    def validate(self, data):
        """
        Проверяет подписки пользователя.
        """
        user = self.context.get('request').user
        author = self.instance
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(f'Вы уже подписаны на {author}.')
        return data

    def get_recipes(self, obj):
        """
        Возвращает список рецептов автора, на которого подписан пользователь.
        """
        limit = self.context.get('request')._request.GET.get('recipes_limit')
        recipes_data = Recipe.objects.filter(author=obj.id)
        if limit:
            recipes_data = recipes_data[:int(limit)]

        serializer = RecipeSerializer(data=recipes_data, many=True)
        serializer.is_valid()
        return serializer.data

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов у избранного автора.
        """
        return obj.recipe_set.count()
