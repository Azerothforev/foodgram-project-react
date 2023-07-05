from django_filters import rest_framework as filters

from recipes.models import FavoriteRecipe, Ingredient, Recipe, ShopingCart, Tag


class IngredientsFilter(filters.FilterSet):
    """
    Фильтрация ингредиентов по полю 'name'
    регистронезависимо, по вхождению в начало названия.
    """
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipesFilter(filters.FilterSet):
    """
    Фильтрация рецептов по нескольким тегам в комбинации «или».
    Метод filter_is_favorited - фильтрует queryset по избранных рецептам.
    Метод filter_is_in_shopping_cart - фильтрует queryset по авторам,
    на которых подписан пользователь.
    """
    tags = filters.ModelMultipleChoiceFilter(
        to_field_name='id',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_subscribed = filters.BooleanFilter(
        method='filter_is_subscribed'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user

        if FavoriteRecipe.objects.filter(user=user).exists():
            return queryset.filter(favorite_recipe__user=user)

        return queryset.none()

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user

        if ShopingCart.objects.filter(user=user).exists():
            return queryset.filter(shoppingcart_recipe__user=user)

        return queryset.none()

    def filter_is_subscribed(self, queryset, name, value):
        user = self.request.user
        return queryset.filter(author=user)
